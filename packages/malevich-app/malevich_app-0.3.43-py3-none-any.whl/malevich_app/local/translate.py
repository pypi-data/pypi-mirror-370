from malevich_coretools.abstract.pipeline import Pipeline, Processor, Condition, AlternativeArgument, BaseArgument, Argument, Result
from malevich_coretools.abstract import Cfg, AppSettings
from malevich_app.export.abstract.pipeline import (Pipeline as InternalPipeline,
                                      Processor as InternalProcessor,
                                      Condition as InternalCondition,
                                      AlternativeArgument as InternalAlternativeArgument,
                                      BaseArgument as InternalBaseArgument,
                                      Argument as InternalArgument,
                                      Result as InternalResult)
from malevich_app.export.abstract.abstract import Cfg as InternalCfg, AppSettings as InternalAppSettings


def __translate_BaseArgument(argument: BaseArgument) -> InternalBaseArgument:
    return InternalBaseArgument(
        id=argument.id,
        indices=argument.indices,
        collectionName=argument.collectionName,
        collectionId=argument.collectionId,
    )


def __translate_Argument(argument: Argument) -> InternalArgument:
    return InternalArgument(
        group=None if argument.group is None else [__translate_BaseArgument(base_arg) for base_arg in argument.group],
        conditions=argument.conditions,

        id=argument.id,
        indices=argument.indices,
        collectionName=argument.collectionName,
        collectionId=argument.collectionId,
    )


def __translate_AlternativeArgument(argument: AlternativeArgument) -> InternalAlternativeArgument:
    return InternalAlternativeArgument(
        group=None if argument.group is None else [__translate_BaseArgument(base_arg) for base_arg in argument.group],
        alternative=None if argument.alternative is None else [__translate_Argument(base_arg) for base_arg in argument.alternative],

        id=argument.id,
        indices=argument.indices,
        collectionName=argument.collectionName,
        collectionId=argument.collectionId,
    )


def __translate_Processor(processor: Processor) -> InternalProcessor:
    assert processor.conditionsStructure is None, f"use conditions instead of conditionsStructure for {bind_id}"
    assert processor.loopConditionsStructure is None, f"use loopConditions instead of loopConditionsStructure for {bind_id}"

    return InternalProcessor(
        cfg=processor.cfg,
        arguments={name: __translate_AlternativeArgument(arg) for name, arg in processor.arguments.items()},
        conditions=processor.conditions,
        loopArguments=None if processor.loopArguments is None else {name: __translate_AlternativeArgument(arg) for name, arg in processor.loopArguments.items()},
        loopConditions=processor.loopConditions,

        processorId=processor.processorId,
        outputId=processor.outputId,
    )


def __translate_Condition(condition: Condition) -> InternalCondition:
    assert condition.conditionsStructure is None, f"use conditions instead of conditionsStructure for {bind_id}"
    assert condition.loopConditionsStructure is None, f"use loopConditions instead of loopConditionsStructure for {bind_id}"

    return InternalCondition(
        cfg=condition.cfg,
        arguments={name: __translate_AlternativeArgument(arg) for name, arg in condition.arguments.items()},
        conditions=condition.conditions,
        loopArguments=None if condition.loopArguments is None else {name: __translate_AlternativeArgument(arg) for name, arg in condition.loopArguments.items()},
        loopConditions=condition.loopConditions,

        conditionId=condition.conditionId,
    )


def __translate_Result(result: Result) -> InternalResult:
    return InternalResult(
        name=result.name,
        index=result.index,
    )


def pipeline_translate(pipeline: Pipeline) -> InternalPipeline:
    pipeline.internal()
    return InternalPipeline(
        processors={bind_id: __translate_Processor(proc) for bind_id, proc in pipeline.processors.items()},
        conditions={bind_id: __translate_Condition(cond) for bind_id, cond in pipeline.conditions.items()},
        results={bind_id: [__translate_Result(res) for res in results] for bind_id, results in pipeline.results.items()},
        pullCollectionPolicy=pipeline.pullCollectionPolicy,
    )


def __translate_app_settings(app_settings: AppSettings) -> InternalAppSettings:
    return InternalAppSettings(
        taskId=app_settings.taskId,
        appId=app_settings.appId,
        saveCollectionsName=[app_settings.saveCollectionsName] if isinstance(app_settings.saveCollectionsName, str) else app_settings.saveCollectionsName,
    )


def cfg_translate(cfg: Cfg) -> InternalCfg:
    assert len(cfg.app_cfg_extension) == 0, "app_cfg_extension not allow in cfg yet"    # FIXME

    return InternalCfg(
        collections=cfg.collections,
        different=cfg.different,
        schemes_aliases=cfg.schemes_aliases,
        msg_url=cfg.msg_url,
        init_apps_update=cfg.init_apps_update,
        app_settings=[__translate_app_settings(app_settings) for app_settings in cfg.app_settings],
        email=cfg.email,
    )
