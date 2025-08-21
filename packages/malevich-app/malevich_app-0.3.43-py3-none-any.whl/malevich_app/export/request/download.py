import requests
from malevich_app.export.secondary.const import CHUNK_SIZE


def save_response(res, filename):
    with open(filename, "wb") as fw:
        for chunk in res.iter_content(CHUNK_SIZE):
            if chunk:
                fw.write(chunk)


def download_google_drive(id, filename):
    def confirm_token(res):
        for k, v in res.cookies.items():
            if k.startswith('download_warning'):
                return v
        return None
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    params = {'id': id}
    res = session.get(URL, params=params, stream=True)
    token = confirm_token(res)

    if token:
        params["confirm"] = token
        res = session.get(URL, params=params, stream=True)
    save_response(res, filename)
