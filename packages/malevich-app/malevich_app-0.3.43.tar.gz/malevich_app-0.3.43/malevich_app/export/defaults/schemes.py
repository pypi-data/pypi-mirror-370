from malevich_app.export.jls.jls import scheme


@scheme()
class default_scheme:
    data: object


@scheme()
class obj:
    path: str
