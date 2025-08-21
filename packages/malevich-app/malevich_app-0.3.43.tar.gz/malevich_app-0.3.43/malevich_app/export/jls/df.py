import importlib
import json
import os
from functools import cached_property, cache
import pandas as pd
from typing import Generic, TypeVar, List, Any, Optional, Union, Tuple, Callable, ForwardRef, Dict, Iterator
from pydantic import BaseModel
from pydantic.v1.json import pydantic_encoder
from typing_extensions import TypeVarTuple, Unpack
from mypy_extensions import VarArg
from malevich_app.export.secondary.const import DELIMITER, CONTEXT_TYPE, CONTEXT, DOC_SCHEME_PREFIX, DOCS_SCHEME_PREFIX

Schemes = TypeVarTuple('Schemes')
Scheme = TypeVar('Scheme')

_docs_first_k_show = 3
_dummy_scheme_attr = "__dummy_scheme"

def __is_tuple(type):
    return str(type).startswith("typing.Tuple[") or str(type).startswith("tuple[")


def _is_DF(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "DF"


def _is_DFS(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "DFS"


def _is_M(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "M"


def __is_Sink(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "Sink"


def __is_Context(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == "malevich_app.jls_lib.utils" and type.__origin__.__name__ == "Context"


def __is_Sink_full(type) -> bool:
    return __is_Sink(type) or (hasattr(type, "__module__") and hasattr(type, "__name__") and type.__module__ == __name__ and type.__name__ == "Sink")


def __is_OBJ(type) -> bool:
    return hasattr(type, "__module__") and hasattr(type, "__name__") and type.__module__ == __name__ and type.__name__ == "OBJ"


def _is_Doc(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "Doc"


def _is_Docs(type) -> bool:
    return hasattr(type, "__origin__") and type.__origin__.__module__ == __name__ and type.__origin__.__name__ == "Docs"


def get_model_name(context) -> Optional[str]:
    if hasattr(context, "__args__"):
        if len(context.__args__) > 0:
            return context.__args__[0].__name__
    return None


def get_argcount(fun: callable) -> int:
    return getattr(fun, "__argcount", fun.__code__.co_argcount)


def get_argnames(fun: callable) -> Tuple[str, ...]:
    varnames = getattr(fun, "__varnames", fun.__code__.co_varnames)
    return varnames[0:get_argcount(fun)]


def get_annotations(fun: callable) -> Dict[str, Any]:
    annotations = getattr(fun, "__annotations", fun.__annotations__)
    return dict(annotations.items())


class M(Generic[Scheme]):
    pass


class DF(Generic[Scheme], pd.DataFrame):    # TODO override main funcs
    def __init__(self, df: Union[pd.DataFrame, BaseModel, Dict, List, 'Doc', 'Docs']):
        if df is None:
            super().__init__(df)
            return

        if isinstance(df, Docs):
            df = df.parse(recursive=True)
        elif isinstance(df, Doc):
            df = [df.dict()]
        elif isinstance(df, Dict):  # Doc
            df = [df]
        elif issubclass(df.__class__, BaseModel):
            df = [df.model_dump()]
        else:
            assert isinstance(df, List) or isinstance(df, pd.DataFrame), f"DF create: expected pd.DataFrame (or Docs, Doc, BaseModel, List, Dict), found {type(df)}"
        super().__init__(df)

    def cast(self, scheme: str):
        raise NotImplementedError("scheme cast not yet implemented")    # TODO

    def scheme(self):
        raise NotImplementedError("scheme not yet implemented")         # TODO

    @cached_property
    def scheme_name(self) -> Optional[str]:
        scheme = self._scheme_cls
        if scheme is None:
            return None
        if hasattr(scheme, "__name__"):
            return scheme.__name__
        if hasattr(scheme, "_name"):
            return scheme._name
        if isinstance(scheme, str):
            return scheme
        if isinstance(scheme, ForwardRef):
            return scheme.__forward_arg__
        return scheme

    @cached_property
    def _scheme_cls(self) -> Optional[Any]:
        if hasattr(self, "__orig_class__"):
            return self.__orig_class__.__args__[0]
        return None


class DFS(Generic[Unpack[Schemes]]):
    def __init__(self):
        """set dfs with init"""
        self.__dfs: List[Union[DF, DFS, OBJ, Doc, Docs, None]] = []
        self.__inited = False

    def init(self, *dfs: Union[str, pd.DataFrame, BaseModel, Dict, List], nested: bool = False) -> 'DFS':
        """must be called after __init__, nested should be False"""
        assert not self.__inited, "DFS already inited"
        self.__inited = True
        if len(dfs) > 0:
            self.__init(list(dfs), nested)
        return self

    def __add_jdf(self, df: Union[str, pd.DataFrame, BaseModel, Dict, List], type) -> None:
        if isinstance(df, str):
            self.__dfs.append(OBJ(df))
        elif (hasattr(type, "__origin__") and type.__origin__ is DF) or type is DF:
            self.__dfs.append(type(df))
        elif (hasattr(type, "__origin__") and type.__origin__ is Doc) or type is Doc:
            self.__dfs.append(type(df).init())
        elif (hasattr(type, "__origin__") and type.__origin__ is Docs) or type is Docs:
            self.__dfs.append(type(df).init())
        elif isinstance(df, Dict) or issubclass(df.__class__, BaseModel):
            self.__dfs.append(Doc[type](df).init())
        elif isinstance(df, List):
            self.__dfs.append(Docs[type](df).init())
        else:
            self.__dfs.append(DF[type](df))

    def __init(self, dfs: List[Union[str, pd.DataFrame, BaseModel, Dict, List]], nested: bool = False) -> None:
        types = self.__orig_class__.__args__ if hasattr(self, "__orig_class__") else [Any for _ in dfs]
        many_df_index = None
        for i, type in enumerate(types):
            if _is_M(type):
                assert not nested, "nested M in DFS"
                if many_df_index is not None:
                    raise Exception("more than one M in DFS")
                else:
                    many_df_index = i
        if many_df_index is None:
            assert len(types) == len(dfs), f"wrong arguments size: expected {len(types)}, found {len(dfs)}"
            for df, type in zip(dfs, types):
                self.__add_jdf(df, type)
        else:
            assert len(types) - 1 <= len(dfs), f"wrong arguments size: expected at least {len(types) - 1}, found {len(dfs)}"
            for df, type in zip(dfs[:many_df_index], types[:many_df_index]):
                self.__add_jdf(df, type)
            count = len(dfs) + 1 - len(types)
            if count != 0:
                type_many = types[many_df_index].__args__[0]
                temp = DFS[tuple([type_many] * count)]().init(*dfs[many_df_index:many_df_index + count], nested=True)
            else:
                temp = DFS[Any]().init(nested=True)
            self.__dfs.append(temp)
            for df, type in zip(dfs[many_df_index + count:], types[many_df_index + 1:]):
                self.__add_jdf(df, type)

    def __len__(self) -> int:
        return len(self.__dfs)

    def __getitem__(self, key: int) -> Union[DF, 'DFS', 'OBJ', 'Doc', 'Docs', None]:
        return self.__dfs[key]

    def __iter__(self) -> Iterator[Union[DF, 'DFS', 'OBJ', 'Doc', 'Docs', None]]:
        return iter(self.__dfs)

    def _apply(self, df_fun: Callable[[Union['DF', 'OBJ', 'Doc', 'Docs']], Union['DF', 'OBJ', 'Doc', 'Docs']]) -> 'DFS':
        for i, df in enumerate(self.__dfs):
            if isinstance(df, DFS):
                df._apply(df_fun)
            else:
                self.__dfs[i] = df_fun(df)
        return self

    def __repr__(self) -> str:
        if len(self.__dfs) == 0:
            return "empty DFS"
        return f"\n{DELIMITER}\n".join(map(lambda x: str(x), self))

    __str__ = __repr__


class Sink(Generic[Unpack[Schemes]]):   # FIXME inside
    def __init__(self):
        """set sink with init"""
        self.__data: List[Union[DFS, DF, Docs, Doc]] = []
        self.__inited = False

    def init(self, *list_data: List[Union[str, pd.DataFrame, BaseModel, Dict, List]]) -> 'Sink':
        """must be called after __init__"""
        assert not self.__inited, "Sink already inited"
        self.__inited = True
        self.__init(list(list_data))
        return self

    def __init(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]]) -> None:
        types = self.__orig_class__.__args__ if hasattr(self, "__orig_class__") else None

        if types is not None and len(types) == 1:
            type = types[0]
            if _is_DFS(type):
                self.__init_DFS(list_data, type)
                return
            if _is_DF(type):
                self.__init_DF(list_data, type)
                return
            if _is_Docs(type):
                self.__init_Docs(list_data, type)
                return
            if _is_Doc(type):
                self.__init_Doc(list_data, type)
                return
        self.__init_common(list_data, types)

    def __init_DFS(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]], type: Any) -> None:
        for data in list_data:
            self.__data.append(type().init(*data))

    def __init_DF(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]], type: Any) -> None:
        for data in list_data:
            self.__data.append(type(*data))

    def __init_Docs(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]], type: Any) -> None:
        for data in list_data:
            self.__data.append(type(*data).init())

    def __init_Doc(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]], type: Any) -> None:
        for data in list_data:
            self.__data.append(type(*data).init())

    def __init_common(self, list_data: List[List[Union[str, pd.DataFrame, BaseModel, Dict, List]]], types: Optional[Any]) -> None:
        if types is not None:
            for data in list_data:
                self.__data.append(DFS[types]().init(*data))
        else:
            for data in list_data:
                self.__data.append(DFS[tuple([Any for _ in data])]().init(*data))

    def __len__(self) -> int:
        return len(self.__data)

    def __getitem__(self, key: int) -> Union[DFS, DF, 'Docs', 'Doc']:
        return self.__data[key]

    def __iter__(self) -> Iterator[Union[DFS, DF, 'Docs', 'Doc']]:
        return iter(self.__data)

    def _apply(self, df_fun: Callable[[Union['DF', 'OBJ', 'Doc', 'Docs']], Union['DF', 'OBJ', 'Doc', 'Docs']]) -> 'Sink':
        for i, dfs in enumerate(self.__data):
            if isinstance(dfs, DFS):
                dfs._apply(df_fun)
            else:
                self.__data[i] = df_fun(dfs)
        return self

    def __repr__(self) -> str:
        return f"\n{DELIMITER * 2}\n".join(map(lambda x: str(x), self))

    __str__ = __repr__


class OBJ:
    def __init__(self, path: str, *, is_new: bool = False):
        self.__path: Any = path
        self.__is_new = is_new

    @property
    def path(self) -> str:
        return self.__path

    @property
    def _is_new(self) -> bool:
        return self.__is_new

    @cached_property
    def raw(self) -> bytes:
        with open(self.__path, 'rb') as f:
            data = f.read()
        return data

    @cached_property
    def as_df(self) -> DF['obj']:
        """df, file paths"""
        paths = []
        if os.path.isfile(self.__path):
            paths.append(self.__path)
        else:
            for address, _, files in os.walk(self.__path):
                for name in files:
                    paths.append(os.path.join(address, name))
        return DF['obj'](pd.DataFrame.from_dict({"path": paths}))

    @cached_property
    def df(self) -> pd.DataFrame:
        """pd.read_csv by path"""
        try:
            df = pd.read_csv(self.__path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
        return df

    def __repr__(self) -> str:
        return f"OBJ(path={self.__path})"

    __str__ = __repr__


class Doc(Generic[Scheme]):
    def __init__(self, data: Union[Scheme, Dict, 'Doc', pd.DataFrame, List]):
        if isinstance(data, List):
            assert len(data) == 1, f"Doc create: too big List, expected size=1, found={len(data)}"
            data = data[0]
        if isinstance(data, Doc):
            data = data.parse()
        elif isinstance(data, pd.DataFrame):
            assert data.shape[0] == 1, f"Doc create: too big pd.DataFrame, expected size=1, found={data.shape[0]}"
            data = data.to_dict(orient="records")[0]
        assert data is None or isinstance(data, Dict) or issubclass(data.__class__, BaseModel), f"wrong Doc data type: expected Dict, pd.DataFrame or subclass of BaseModel, found {type(data)}"
        self.__data: Union[Scheme, BaseModel, Dict] = data

    def parse(self) -> Union[Scheme, BaseModel, Dict]:
        return self.__data

    def init(self) -> 'Doc':
        if self.__data is None:
            return self

        scheme = self._scheme_cls
        if scheme is Any:
            assert isinstance(self.__data, Dict) or issubclass(self.__data.__class__, BaseModel), f"wrong Doc data type: expected Dict or subclass of BaseModel, found {type(self.__data)}"
            return self
        if scheme is None or getattr(scheme, "__name__", None) == "NoneType":
            return self
        if isinstance(scheme, str):
            # json_scheme = schemes[scheme]
            raise Exception(f"Doc not yet work with user json schemes: {scheme}")
        if isinstance(scheme, ForwardRef):
            # json_scheme = schemes[scheme]
            raise Exception(f"Doc not yet work with user json schemes: {scheme.__forward_arg__}")
        if hasattr(scheme, _dummy_scheme_attr):
            # json_scheme = schemes[scheme]
            raise Exception(f"Doc not yet work with user json schemes: {scheme.__name__}")
        if issubclass(scheme, BaseModel):
            if isinstance(self.__data, Dict):
                self.__data = scheme(**self.__data)
            elif isinstance(self.__data, scheme):
                pass
            else:
                self.__data = scheme(**self.__data.model_dump())
        else:
            raise Exception(f"Unknown Doc type: {scheme}")
        return self

    def __getitem__(self, k):
        return self.__data[k]

    def __repr__(self):
        return f"Doc(__data={{{self.__data}}})"

    __str__ = __repr__

    @cached_property
    def scheme_name(self) -> Optional[str]:
        scheme = self._scheme_cls
        if scheme is None:
            return None
        if hasattr(scheme, "__name__"):
            return scheme.__name__
        if hasattr(scheme, "_name"):
            return scheme._name
        if isinstance(scheme, str):
            return scheme
        if isinstance(scheme, ForwardRef):
            return scheme.__forward_arg__
        return scheme

    @cached_property
    def _scheme_cls(self) -> Optional[Any]:
        if hasattr(self, "__orig_class__"):
            return self.__orig_class__.__args__[0]
        return None

    def dict(self) -> Dict[str, Any]:
        if isinstance(self.__data, Dict):
            return self.__data
        return self.__data.model_dump()

    def json(self) -> str:
        return json.dumps(self.dict(), default=pydantic_encoder)


class Docs(Generic[Scheme]):
    def __init__(self, data: Union[List[Scheme], List[Dict], List[Doc], 'Docs', Scheme, Dict, 'Doc', pd.DataFrame]):
        if data is not None:
            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")
            if isinstance(data, List):
                if len(data) > 0:
                    first = data[0]
                    assert isinstance(first, Dict) or issubclass(first.__class__, BaseModel) or isinstance(first, Doc), f"wrong Docs data type: expected List[Dict] or List[Doc] or List[subclass of BaseModel] or Docs, Scheme, Dict, Doc, pd.DataFrame; found List[{type(first)}]"
            elif isinstance(data, Docs):
                data = data.parse(recursive=True)
            else:
                assert isinstance(data, Doc) or isinstance(data, Dict) or issubclass(data.__class__, BaseModel), f"wrong Docs data type: expected List[Dict] or List[Doc] or List[subclass of BaseModel] or Docs, Scheme, Dict, Doc, pd.DataFrame; found {type(data)}"
        self.__data: List[Doc[Scheme]] = data

    @cache
    def parse(self, *, recursive: bool = False) -> Union[List[Doc[Scheme]], List[Union[Scheme, BaseModel, Dict]]]:
        if recursive:
            return [doc.parse() for doc in self.__data]
        return self.__data

    def init(self) -> 'Docs':
        if self.__data is None:
            return self

        scheme = self._scheme_cls
        if isinstance(self.__data, List):
            self.__data = list(map(lambda doc: Doc[scheme](doc).init(), self.__data))
        else:
            self.__data = [Doc[scheme](self.__data).init()]
        return self

    def __len__(self) -> int:
        return len(self.__data)

    def __getitem__(self, key: int) -> Optional[Doc]:
        return self.__data[key]

    def __iter__(self) -> Iterator[Doc]:
        return iter(self.__data)

    def __repr__(self):
        if len(self.__data) == 0:
            return f"Docs(__data=[])"
        if len(self.__data) <= _docs_first_k_show:
            return f"Docs(__data={self.__data[:_docs_first_k_show]}, len={len(self.__data)})"
        return f"Docs(__data=[{', '.join(map(str, self.__data[:_docs_first_k_show]))}, ...], len={len(self.__data)})"

    __str__ = __repr__

    @cached_property
    def scheme_name(self) -> Optional[str]:
        scheme = self._scheme_cls
        if scheme is None:
            return None
        if hasattr(scheme, "__name__"):
            return scheme.__name__
        if hasattr(scheme, "_name"):
            return scheme._name
        if isinstance(scheme, str):
            return scheme
        if isinstance(scheme, ForwardRef):
            return scheme.__forward_arg__
        return scheme

    @cached_property
    def _scheme_cls(self) -> Optional[Any]:
        if hasattr(self, "__orig_class__"):
            return self.__orig_class__.__args__[0]
        return None

    def json(self) -> str:
        return json.dumps([doc.dict() for doc in self.__data], default=pydantic_encoder)


class Stream:
    def __init__(self, f):
        if not callable(f):
            raise TypeError("stream should be callable")
        self.f = f

    def __call__(self):
        return self.f()

    def __repr__(self):
        return f"Stream(f={self.f})"

    __str__ = __repr__


JDF = Union[DF, DFS, Sink, OBJ, Doc, Docs]
dfs_many_fun = lambda *dfs: DFS[M[Any]]().init(*dfs, nested=False)


def get_fun_info(fun: callable, *, by_names: bool = False) -> Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]:     # TODO(not ignore return later)
    def __name(type: Any, repr: bool = False) -> Optional[str]:
        if type is None or type is Any:
            return "" if repr else None
        if isinstance(type, str):
            return type
        if isinstance(type, ForwardRef):
            return type.__forward_arg__
        if hasattr(type, "__origin__") and type.__origin__ is Doc:
            return f"{DOC_SCHEME_PREFIX}{__name(type(None)._scheme_cls, repr=True)}"
        if hasattr(type, "__origin__") and type.__origin__ is Docs:
            return f"{DOCS_SCHEME_PREFIX}{__name(type(None)._scheme_cls, repr=True)}"
        if type is Doc:
            return DOC_SCHEME_PREFIX
        if type is Docs:
            return DOCS_SCHEME_PREFIX
        assert hasattr(type, "__name__"), f"unsupported type: {type}"
        if type.__name__ == "NoneType":
            return "" if repr else None
        return type.__name__

    def __inside_types(type) -> Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]:      # TODO check nested types not in this module (for example - DF[DF])
        if _is_DF(type):
            return type, (__name(type(None)._scheme_cls),)
        elif _is_DFS(type):
            temp = type()
            sz = len(temp.__orig_class__.__args__)
            schemes = []
            for df in temp.init(*[None] * sz):
                if isinstance(df, DFS):
                    sub_df = df[0]
                    name = __name(sub_df._scheme_cls, repr=True)
                    if isinstance(sub_df, DF):
                        schemes.append(f"{name}*")  # example result: scheme*  - end with * - many
                    elif isinstance(sub_df, Docs):
                        schemes.append(f"{DOCS_SCHEME_PREFIX}{name}*")
                    elif isinstance(sub_df, Doc):
                        schemes.append(f"{DOC_SCHEME_PREFIX}{name}*")
                    else:
                        assert False, f"internal error: unknown DFS type in DFS: {type(df)}"
                elif isinstance(df, DF):
                    schemes.append(__name(df._scheme_cls))
                elif isinstance(df, Docs):
                    schemes.append(f"{DOCS_SCHEME_PREFIX}{__name(df._scheme_cls, repr=True)}")
                elif isinstance(df, Doc):
                    schemes.append(f"{DOC_SCHEME_PREFIX}{__name(df._scheme_cls, repr=True)}")
                else:
                    assert False, f"internal error: unknown DFS type: {type(df)}"
            return lambda *dfs: type().init(*dfs, nested=False), tuple(schemes)
        elif __is_Sink(type):
            temp = type()
            types = temp.__orig_class__.__args__
            schemes = []
            data = temp.init([None] * len(types))[0]
            if isinstance(data, DFS):
                for df in data:
                    if isinstance(df, DFS):
                        sub_df = df[0]
                        name = __name(sub_df._scheme_cls, repr=True)
                        if isinstance(sub_df, DF):
                            schemes.append(f"{name}*")  # example result: scheme*  - end with * - many
                        elif isinstance(sub_df, Docs):
                            schemes.append(f"{DOCS_SCHEME_PREFIX}{name}*")
                        elif isinstance(sub_df, Doc):
                            schemes.append(f"{DOC_SCHEME_PREFIX}{name}*")
                        else:
                            assert False, f"internal error: unknown DFS type in DFS: {type(df)}"
                    elif isinstance(df, DF):
                        schemes.append(__name(df._scheme_cls))
                    elif isinstance(df, Docs):
                        schemes.append(f"{DOCS_SCHEME_PREFIX}{__name(df._scheme_cls, repr=True)}")
                    elif isinstance(df, Doc):
                        schemes.append(f"{DOC_SCHEME_PREFIX}{__name(df._scheme_cls, repr=True)}")
                    else:
                        assert False, f"internal error: unknown Sink type in DFS: {type(df)}"
            elif isinstance(data, DF):
                schemes.append(__name(data._scheme_cls))
            elif isinstance(data, Docs):
                schemes.append(f"{DOCS_SCHEME_PREFIX}{__name(data._scheme_cls, repr=True)}")
            elif isinstance(data, Doc):
                schemes.append(f"{DOC_SCHEME_PREFIX}{__name(data._scheme_cls, repr=True)}")
            else:
                assert False, f"internal error: unknown Sink type: {type(data)}"
            return lambda *list_dfs: type().init(*list_dfs), tuple(schemes)
        elif __is_OBJ(type):
            return type, ("OBJ",)
        elif __is_Context(type):
            return type, (CONTEXT_TYPE,)
        elif _is_Doc(type):
            return lambda doc: type(doc).init(), (f"{DOC_SCHEME_PREFIX}{__name(type(None)._scheme_cls, repr=True)}",)
        elif _is_Docs(type):
            return lambda docs: type(docs).init(), (f"{DOCS_SCHEME_PREFIX}{__name(type(None)._scheme_cls, repr=True)}",)
        elif __is_tuple(type):
            typef = lambda *dfs: DFS[type.__args__]().init(*dfs, nested=False)
            return typef, tuple(map(__name, type.__args__))
        elif isinstance(type, List):
            typef = lambda *dfs: DFS[type]().init(*dfs, nested=False)
            return typef, tuple(map(__name, type))
        else:
            name = __name(type)
            if name == CONTEXT_TYPE:
                return None, (name,)
            if name is None:
                typef = lambda *dfs: ((Doc[type](*dfs).init() if isinstance(dfs[0], Dict) or issubclass(dfs[0].__class__, BaseModel) else
                                      Docs[type](*dfs).init() if isinstance(dfs[0], List) else DF[type](*dfs))) \
                    if len(dfs) == 1 else DFS[M[type]]().init(*dfs, nested=False)
                return typef, None
            if name == "DF" and hasattr(type, "__module__") and type.__module__ == __name__:
                return __inside_types(DF[Any])
            if name == "DFS" and hasattr(type, "__module__") and type.__module__ == __name__:
                return __inside_types(DFS[M[Any]])
            if name == "Sink" and hasattr(type, "__module__") and type.__module__ == __name__:
                return __inside_types(Sink[Any])
            if name.startswith(DOC_SCHEME_PREFIX) and hasattr(type, "__module__") and type.__module__ == __name__:
                return __inside_types(Doc[Any])
            if name.startswith(DOCS_SCHEME_PREFIX) and hasattr(type, "__module__") and type.__module__ == __name__:
                return __inside_types(Docs[Any])
            typef = DF[type]
            return typef, (name,)

    types_dict = get_annotations(fun)
    ret_type = None if "return" not in types_dict else __inside_types(types_dict.pop("return"))[1]
    if by_names:
        types = {}
        sink_index = None
        for i, varname in enumerate(get_argnames(fun)):
            varname_type = types_dict.get(varname, None)
            types[varname] = __inside_types(varname_type)

            if __is_Sink_full(varname_type):
                assert sink_index is None, "double Sink"
                sink_index = varname
    else:
        types = []
        sink_index = None
        for i, varname in enumerate(get_argnames(fun)):
            varname_type = types_dict.get(varname, None)
            types.append(__inside_types(varname_type))

            if __is_Sink_full(varname_type):
                assert sink_index is None, "double Sink"
                sink_index = i

        for type in types[1:-1]:
            assert type[1] != CONTEXT, "wrong context position"
    return types, ret_type, sink_index


def __get_schemes_names(input_fun: callable):
    schemes_names: List[Tuple[Optional[str], ...]] = []
    schemes_info = get_fun_info(input_fun)
    for info in schemes_info[0]:
        schemes_names.append(info[1])
    return schemes_names


def get_fun_info_verbose(fun: callable) -> List[Tuple[str, Optional[str]]]:
    def __name(type: Any, none_value: Optional[str] = "Any") -> Optional[str]:
        if type is None or type is Any:
            return none_value
        if isinstance(type, str):
            return f'"{type}"'
        if isinstance(type, ForwardRef):
            return f'"{type.__forward_arg__}"'
        if hasattr(type, "__origin__") and type.__origin__ is Doc:
            name = __name(type(None)._scheme_cls, none_value=None)
            if name is not None:
                return f"Doc[{name}]"
            return "Doc"
        if hasattr(type, "__origin__") and type.__origin__ is Docs:
            name = __name(type(None)._scheme_cls, none_value=None)
            if name is not None:
                return f"Docs[{name}]"
            return "Docs"
        if type is Doc:
            return "Doc"
        if type is Docs:
            return "Docs"
        assert hasattr(type, "__name__"), f"unsupported type: {type}"
        if type.__name__ == "NoneType":
            return none_value
        return type.__name__

    def __inside_types(type) -> Optional[str]:
        if _is_DF(type):
            return f"DF[{__name(type(None)._scheme_cls)}]"
        elif _is_DFS(type):
            schemes = []
            for scheme in type.__args__:
                if _is_M(scheme):
                    schemes.append(f"M[{__name(scheme.__args__[0])}]")
                elif _is_DF(scheme):
                    schemes.append(f"DF[{__name(scheme(None)._scheme_cls)}]")
                else:
                    schemes.append(__name(scheme))
            return f"DFS[{', '.join(schemes)}]"
        elif __is_Sink(type):
            schemes = []
            for scheme in type.__args__:
                if _is_M(scheme):
                    schemes.append(f"M[{__name(scheme.__args__[0])}]")
                elif _is_DFS(scheme):
                    subschemes = []
                    for subscheme in scheme.__args__:
                        if _is_M(subscheme):
                            subschemes.append(f"M[{__name(subscheme.__args__[0])}]")
                        elif _is_DF(subscheme):
                            subschemes.append(__name(subscheme(None)._scheme_cls))
                        else:
                            subschemes.append(__name(subscheme))
                    schemes.append(f"DFS[{', '.join(subschemes)}]")
                elif _is_DF(scheme):
                    schemes.append(f"DF[{__name(scheme(None)._scheme_cls)}]")
                else:
                    schemes.append(__name(scheme))
            return f"Sink[{', '.join(schemes)}]"
        elif __is_OBJ(type):
            return "OBJ"
        elif __is_Context(type):
            if hasattr(type, "__args__") and len(type.__args__) == 1:
                return f"{CONTEXT_TYPE}[{type.__args__[0].__name__}]"
            return CONTEXT_TYPE
        elif _is_Doc(type):
            return f"Doc[{__name(type(None)._scheme_cls)}]"
        elif _is_Docs(type):
            return f"Docs[{__name(type(None)._scheme_cls)}]"
        elif __is_tuple(type):
            return f"DFS[{', '.join(map(__name, type.__args__))}]"
        elif isinstance(type, List):
            return f"DFS[{', '.join(map(__name, type))}]"
        else:
            name = __name(type, none_value=None)
            if name == CONTEXT_TYPE:
                return name
            if name is None:
                return None
            if name == "DF" and hasattr(type, "__module__") and type.__module__ == __name__:
                return "DF[Any]"
            if name == "DFS" and hasattr(type, "__module__") and type.__module__ == __name__:
                return "DFS[M[Any]]"
            if name == "Sink" and hasattr(type, "__module__") and type.__module__ == __name__:
                return "Sink[Any]"
            if name == "Doc" or name.startswith("Doc[") and hasattr(type, "__module__") and type.__module__ == __name__:
                return name
            if name == "Docs" or name.startswith("Docs[") and hasattr(type, "__module__") and type.__module__ == __name__:
                return name
            return f"DF[{name}]"

    types_dict = get_annotations(fun)
    res = []
    for varname in get_argnames(fun):
        varname_type = types_dict.get(varname, None)
        res.append((varname, __inside_types(varname_type)))

    res.append(("return", None if "return" not in types_dict else __inside_types(types_dict.pop("return"))))
    return res


def get_context_argname(fun: callable) -> Optional[str]:    # only for init
    count = get_argcount(fun)
    if count == 0:
        return None
    elif count == 1:
        varname = get_argnames(fun)[0]
        type = get_annotations(fun).get(varname, None)
        assert getattr(type, "__name__", None) == CONTEXT_TYPE or __is_Context(type), f"wrong type in init: {type}"
        return varname
    raise Exception(f"too many arguments in init: {count}")


def get_context_info(schemes_info: List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]]) -> Optional[Dict[str, Any]]:
    context_cl = None
    if len(schemes_info) > 0:
        if schemes_info[0][1] == CONTEXT:
            context_cl = schemes_info[0][0]
        elif schemes_info[-1][1] == CONTEXT:
            context_cl = schemes_info[-1][0]
    if context_cl is None:
        return None
    try:
        if not hasattr(context_cl, "__args__") or len(context_cl.__args__) == 0:
            return None
        arg = context_cl.__args__[0]
        module_name, name = arg.__module__, arg.__name__
        if module_name == "builtins" and name == "NoneType":
            return None

        module = importlib.import_module(module_name)
        cl: BaseModel = getattr(module, name)
        if issubclass(cl, BaseModel):
            return cl.model_json_schema()
    except:
        pass
    return None


# example

# T = TypeVar('T')
#
#
# class Context(Generic[T]):
#     def __init__(self, a):
#         pass
#
#
# def set_internal_attrs(fun, new_fun):
#     setattr(new_fun, '__argcount', getattr(fun, "__argcount", fun.__code__.co_argcount))
#     setattr(new_fun, '__varnames', getattr(fun, "__varnames", fun.__code__.co_varnames))
#     setattr(new_fun, '__annotations', getattr(fun, "__annotations", fun.__annotations__))


# def dec():
#     def wrap(fun):
#         def temp(*args):
#             return fun(*args)
#
#         set_internal_attrs(fun, temp)
#         return temp
#     return wrap


# def fun(df: DFS['scheme', 'scheme']):
#     pass
#
#
# def fun2(df: Sink['scheme', 'scheme2']):
#     pass
#
#
# class A(BaseModel):
#     a: str
#     b: int
#
#
# def fun3(df: OBJ, dfs: DFS['a', OBJ], ctx: Context[A]):
#     pass
#
#
# if __name__ == '__main__':
#     print(get_fun_info(fun3))
#     print(__get_schemes_names(fun3))
#     print(get_fun_info_verbose(fun3))
#     print(get_context_info(get_fun_info(fun3)[0]))
