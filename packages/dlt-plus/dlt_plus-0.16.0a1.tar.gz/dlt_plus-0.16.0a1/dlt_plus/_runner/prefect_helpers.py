import dlt
import dlt_plus
from typing import Any
from prefect.logging import get_run_logger
from dlt_plus._runner.prefect_collector import PrefectCollector
from prefect import task
from prefect.futures import wait
from prefect.cache_policies import NO_CACHE


@task(
    log_prints=True,
    task_run_name="run_{task_name}",
    cache_policy=NO_CACHE,
)
def run_pipeline_with_source_task(
    pipeline: dlt.Pipeline,
    source: Any,
    task_name: str,
    **run_kwargs: Any,
) -> None:
    prefect_logger = get_run_logger()
    pipeline.collector = PrefectCollector(1, logger=prefect_logger)  # type: ignore
    dlt_plus.runner(pipeline).run(data=source, **run_kwargs)


@task(
    cache_policy=NO_CACHE  # << otherwise error from trying to hash pipeline-object
)
def decompose_and_run_in_pipeline_task(
    pipeline: dlt.Pipeline, source: dlt.sources.DltSource, **run_kwargs: Any
) -> None:
    """
    WARNING: Experimental, do not use in production
    Must be called inside a flow, otherwise .submit will not work
    Decomposes source into scc, uses task-pipeline for each.
    Runs first source to establish schema, then all others in parallel tasks
    """
    if pipeline.dev_mode:
        raise ValueError("Cannot decompose pipelines with `dev_mode=True`")

    # todo: warn on incremental sources

    sources = source.decompose(strategy="scc")

    # run first source
    first_source = sources[0]
    task_name = _task_name_from_source(first_source)
    task_pipeline = _make_task_pipeline(pipeline, task_name)
    run_pipeline_with_source_task(
        task_pipeline,
        first_source,
        task_name,
        **run_kwargs,
    )
    # run rest of sources
    futures = []
    for s in sources[1:]:
        task_name = _task_name_from_source(s)
        task_pipeline = _make_task_pipeline(pipeline, task_name)
        future = run_pipeline_with_source_task.submit(
            task_pipeline,
            s,
            task_name,
            **run_kwargs,
        )
        futures.append(future)

    wait(futures)


def _make_task_pipeline(pipeline: dlt.Pipeline, new_name: str) -> dlt.Pipeline:
    """
    Creates a new pipeline with the given name, dropping the existing pipeline, syncing from
    the destination to get latest schema and state.
    """
    pipeline.activate()
    task_pipeline = pipeline.drop(pipeline_name=new_name)
    return task_pipeline


def _task_name_from_source(source: dlt.sources.DltSource) -> str:
    return list(source.resources.selected.keys())[0] if source.resources.selected else source.name
