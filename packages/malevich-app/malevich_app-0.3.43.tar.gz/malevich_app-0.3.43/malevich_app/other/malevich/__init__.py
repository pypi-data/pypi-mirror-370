from malevich_app.export.secondary.jls_imported import imported2, set_imported2

if not imported2:
    from malevich_app.jls_lib.utils import *
    from malevich_app.export.jls.df import M, DF, DFS, Sink, OBJ, Doc, Docs
    from malevich_app.export.defaults.schemes import *
    set_imported2(True)
from malevich_app.docker_export.schemes import *
