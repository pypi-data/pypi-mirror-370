import io
import os
import traceback
from typing import List, Optional
from zipfile import ZipFile

from malevich_app.export.secondary.LogHelper import log_error
from malevich_app.export.secondary.const import STORAGE_PATH, TEMP_OBJ_DIR, COLLECTIONS_PATH, COLLECTIONS_OBJ_PATH

__counter = 0


def zip_files(dir_from: str, path_to: str, paths: List[str], *, ignore_not_exist: bool = False):
    if not ignore_not_exist:
        for path in paths:
            assert os.path.exists(os.path.join(dir_from, path)), f"path {path} not exist"

    try:
        prefix_size = len(dir_from) + 1
        with ZipFile(path_to, mode="w", allowZip64=True) as archive:
            if len(paths) == 0:
                for root, dirs, files in os.walk(dir_from):
                    for subpath in files + dirs:
                        subpath = os.path.join(root, subpath)
                        archive.write(subpath, arcname=subpath[prefix_size:])
            else:
                for path in paths:
                    real_path = os.path.join(dir_from, path)
                    if os.path.isfile(real_path):
                        archive.write(real_path, arcname=path)
                    elif os.path.isdir(real_path):
                        for root, dirs, files in os.walk(real_path):
                            for subpath in files + dirs:
                                subpath = os.path.join(root, subpath)
                                archive.write(subpath, arcname=subpath[prefix_size:])
                    elif not ignore_not_exist:
                        raise RuntimeError(f"path {path} not exist")
    except BaseException as ex:
        os.remove(path_to)
        raise ex


def unzip_files(path_from: str, dir_to: str):   # do nothing if failed
    with ZipFile(path_from, 'r', allowZip64=True) as zf:
        for z_file in zf.infolist():
            name = z_file.filename
            real_path = os.path.join(dir_to, name)
            if z_file.is_dir():
                os.makedirs(real_path, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(real_path), exist_ok=True)
            with open(real_path, 'wb') as fw:
                fw.write(zf.read(name))


def unzip_raw(raw_zip: bytes, operation_id: str, run_id: Optional[str], asset: bool, logs_buffer: io.StringIO, *, login: Optional[str] = None) -> bool:
    global __counter
    path_from = f"{TEMP_OBJ_DIR}{os.sep}{__counter}"
    __counter += 1

    ok = True
    try:
        with open(path_from, "wb") as fw:
            fw.write(raw_zip)

        if asset:
            assert login is not None, "login should exist for unzip raw collection objects"
            dir_to = COLLECTIONS_OBJ_PATH(login)
        else:
            dir_to = STORAGE_PATH(operation_id)
        if run_id is not None:
            dir_to += f"{os.sep}{run_id}"
        unzip_files(path_from, dir_to)
    except:
        logs_buffer.write(f"{traceback.format_exc()}\n")
        log_error(traceback.format_exc())
        ok = False

    os.remove(path_from)
    return ok


def zip_raw(paths: List[str], operation_id: str, run_id: Optional[str], logs_buffer: io.StringIO, *, ignore_not_exist: bool = False) -> Optional[bytes]:
    try:
        dir_from = STORAGE_PATH(operation_id)
        if run_id is not None:
            dir_from += f"{os.sep}{run_id}"
        if all(not os.path.exists(os.path.join(dir_from, path)) for path in paths):
            return bytes()

        global __counter
        path_to = f"{TEMP_OBJ_DIR}{os.sep}{__counter}"
        __counter += 1
        zip_files(dir_from, path_to, paths, ignore_not_exist=ignore_not_exist)
        with open(path_to, "rb") as fr:
            data = fr.read()
    except:
        logs_buffer.write(f"{traceback.format_exc()}\n")
        log_error(traceback.format_exc())
        return None

    os.remove(path_to)
    return data


def zip_raw_collections(paths: List[str], operation_id: str, logs_buffer: io.StringIO, asset: bool, *, login: Optional[str] = None) -> Optional[bytes]:
    try:
        if asset:
            assert login is not None, "login should exist for zip raw collection objects"
            dir_from = COLLECTIONS_OBJ_PATH(login)
        else:
            dir_from = COLLECTIONS_PATH(operation_id)
        if all(not os.path.exists(os.path.join(dir_from, path)) for path in paths):
            return bytes()

        global __counter
        path_to = f"{TEMP_OBJ_DIR}{os.sep}{__counter}"
        __counter += 1
        zip_files(dir_from, path_to, paths, ignore_not_exist=True)
        with open(path_to, "rb") as fr:
            data = fr.read()
    except:
        logs_buffer.write(f"{traceback.format_exc()}\n")
        log_error(traceback.format_exc())
        return None

    os.remove(path_to)
    return data
