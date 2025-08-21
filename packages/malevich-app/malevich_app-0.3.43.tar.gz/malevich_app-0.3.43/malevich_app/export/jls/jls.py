from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from malevich_app.export.jls.JuliusApp import JuliusApp
from malevich_app.export.jls.WrapperMode import InputWrapper


# FIXME get_scale_part_all for inputs and fix get wrong part after input in processor

def __tags(tags: Optional[Dict[str, str]], **kwargs) -> Optional[Dict[str, str]]:
    if tags is None:
        return kwargs
    if kwargs is None:
        return tags
    res = tags.copy()
    res.update(**kwargs)
    return res


def input_doc(id: Optional[str] = None, collection_from: Optional[str] = None, collections_from: Optional[List[str]] = None, extra_collection_from: Optional[str] = None, extra_collections_from: Optional[List[str]] = None, query: Optional[str] = None, finish_msg: Optional[str] = None, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_input(fun, id, collection_from, collections_from, extra_collection_from, extra_collections_from, False, query, finish_msg=finish_msg, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs), mode=InputWrapper.INPUT_DOC)
        return fun
    return wrapper


def input_df(id: Optional[str] = None, collection_from: Optional[str] = None, collections_from: Optional[List[str]] = None, extra_collection_from: Optional[str] = None, extra_collections_from: Optional[List[str]] = None, by_args: bool = False, query: Optional[str] = None, finish_msg: Optional[str] = None, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_input(fun, id, collection_from, collections_from, extra_collection_from, extra_collections_from, by_args, query, finish_msg=finish_msg, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs), mode=InputWrapper.INPUT_DF)
        return fun
    return wrapper


def input_true(id: Optional[str] = None, collection_from: Optional[str] = None, collections_from: Optional[List[str]] = None, extra_collection_from: Optional[str] = None, extra_collections_from: Optional[List[str]] = None, query: Optional[str] = None, finish_msg: Optional[str] = None, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_input(fun, id, collection_from, collections_from, extra_collection_from, extra_collections_from, False, query, finish_msg=finish_msg, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs), mode=InputWrapper.INPUT_TRUE)
        return fun
    return wrapper


def processor(id: Optional[str] = None, finish_msg: Optional[str] = None, drop_internal: bool = True, get_scale_part_all: bool = False, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, is_stream: bool = False, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_processor(fun, id, finish_msg=finish_msg, cpu_bound=cpu_bound, is_stream=is_stream, tags=__tags(tags, **kwargs), drop_internal=drop_internal, get_scale_part_all=get_scale_part_all)
        return fun
    return wrapper


def output(id: Optional[str] = None, collection_name: Optional[str] = None, collection_names: Optional[List[str]] = None, finish_msg: Optional[str] = None, drop_internal: bool = True, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_output(fun, id, collection_out_name=collection_name, collection_out_names=collection_names, finish_msg=finish_msg, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs), drop_internal=drop_internal)
        return fun
    return wrapper


def condition(id: Optional[str] = None, finish_msg: Optional[str] = None, drop_internal: bool = True, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_condition(fun, id, finish_msg=finish_msg, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs), drop_internal=drop_internal)
        return fun
    return wrapper


def scheme():
    def wrapper(cl):
        if issubclass(cl, BaseModel):
            Wrapper.app.register_scheme(cl)
            return cl

        class SchemaClass(cl, BaseModel):
            model_config = ConfigDict(
                title=cl.__name__,
                model_title_generator=lambda *args: cl.__name__
            )

            def __init__(self, *args, **kwargs):
                super(cl, self).__init__(*args, **kwargs)
                super(BaseModel, self).__init__()

        SchemaClass.__module__ = cl.__module__
        SchemaClass.__name__ = cl.__name__
        SchemaClass.__doc__ = cl.__doc__
        SchemaClass.__annotations__ = cl.__annotations__
        SchemaClass.__pydantic_core_schema__['ref'] = cl.__qualname__
        Wrapper.app.register_scheme(SchemaClass)
        return SchemaClass
    return wrapper


def init(id: Optional[str] = None, enable: bool = True, tl: Optional[int] = None, prepare: bool = False, cpu_bound: bool = False, tags: Optional[Dict[str, str]] = None, **kwargs):
    def wrapper(fun):
        Wrapper.app.register_init(fun, id, enable=enable, tl=tl, prepare=prepare, cpu_bound=cpu_bound, tags=__tags(tags, **kwargs))
        return fun
    return wrapper


class Wrapper:
    app = JuliusApp()
