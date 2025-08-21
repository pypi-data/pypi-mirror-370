from enum import IntEnum
from typing import Optional, List, Dict, Union

from pydantic import BaseModel
from malevich_app.export.secondary.EntityException import EntityException


class PullCollectionPolicy(IntEnum):
    INIT = 0
    IF_NOT_EXIST = 1
    FORCE_RELOAD = 2
    FORCE_RELOAD_ALL = 3


class BaseArgument(BaseModel):
    id: Optional[str] = None                            # from - bindProcessorId
    indices: Optional[List[int]] = None                 # full if None
    # or
    collectionName: Optional[str] = None                # get id (or obj path) from cfg by it
    # or
    collectionId: Optional[str] = None                  # hardcode collection with id (or obj path)

    def validation(self):
        if (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) != 1:
            raise EntityException("one way of constructing the argument must be chosen")


class Argument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    conditions: Optional[Dict[str, bool]] = None        # valid only for alternative, bindConditionId -> value, must be specified explicitly, then it will be derived from the pipeline structure

    def validation(self):
        if self.group is not None:
            if self.id is not None or self.collectionName is not None or self.collectionId is not None:
                raise EntityException("one way of constructing the argument must be chosen")
            for subarg in self.group:
                subarg.validation()
        else:
            if (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) != 1:
                raise EntityException("one way of constructing the argument must be chosen")


class AlternativeArgument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    alternative: Optional[List[Argument]] = None        # if set - should be only one valid argument with conditions

    def validation(self):
        if self.group is not None:
            if self.id is not None or self.collectionName is not None or self.collectionId is not None:
                raise EntityException("one way of constructing the argument must be chosen")
            for subarg in self.group:
                subarg.validation()
        elif self.alternative is not None:
            for alt_arg in self.alternative:
                if alt_arg.group is not None:
                    if alt_arg.id is not None or alt_arg.collectionName is not None or alt_arg.collectionId is not None:
                        raise EntityException("one way of constructing the argument must be chosen")
                    for subarg in alt_arg.group:
                        subarg.validation()
                else:
                    if (alt_arg.id is not None) + (alt_arg.collectionName is not None) + (alt_arg.collectionId is not None) != 1:
                        raise EntityException("one way of constructing the argument must be chosen")
        else:
            if (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) != 1:
                raise EntityException("one way of constructing the argument must be chosen")


class AppEntity(BaseModel):
    cfg: Optional[str] = None                                                       # local cfg for processor/condition
    arguments: Dict[str, AlternativeArgument] = {}                                  # first call
    conditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None      # condition bindId to it result
    loopArguments: Optional[Dict[str, AlternativeArgument]] = None                  # other calls, problems
    loopConditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None  # condition bindId to it result for loop


class Processor(AppEntity):
    processorId: str
    outputId: Optional[str] = None


class Condition(AppEntity):                             # at least one of (true, false) set
    conditionId: str


class Result(BaseModel):                                # save collection (only processor)
    name: str
    index: Optional[int] = None


class Pipeline(BaseModel):
    processors: Dict[str, Processor] = {}               # bindProcessorId to Processor
    conditions: Dict[str, Condition] = {}               # bindConditionId to Condition
    results: Dict[str, List[Result]] = {}               # bindProcessorId to results
    bindIdToCluster: Dict[str, int] = {}                # bindId to cluster index
    bindIds: Dict[str, int] = {}                        # bindId to scale (old)
    pullCollectionPolicy: PullCollectionPolicy = PullCollectionPolicy.IF_NOT_EXIST

    def fix(self, index: int):
        if index != 0:
            removed_bind_ids = []
            for bind_id, scale in self.bindIds.items():
                if scale <= index:
                    self.processors.pop(bind_id, None)
                    self.conditions.pop(bind_id, None)
                    self.results.pop(bind_id, None)
                    self.bindIdToCluster.pop(bind_id, None)
                    removed_bind_ids.append(bind_id)
            for bind_id in removed_bind_ids:
                self.bindIds.pop(bind_id)

        for processor in self.processors.values():
            if isinstance(processor.conditions, Dict):
                processor.conditions = [processor.conditions]
            if isinstance(processor.loopConditions, Dict):
                processor.loopConditions = [processor.loopConditions]

        for condition in self.conditions.values():
            if isinstance(condition.conditions, Dict):
                condition.conditions = [condition.conditions]
            if isinstance(condition.loopConditions, Dict):
                condition.loopConditions = [condition.loopConditions]
