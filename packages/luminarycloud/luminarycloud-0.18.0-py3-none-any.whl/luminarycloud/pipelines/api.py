# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass

from datetime import datetime

from luminarycloud._helpers import timestamp_to_datetime

from ..enum.pipeline_job_status import PipelineJobStatus
from ..pipelines import Pipeline, PipelineArgs
from .._client import get_default_client
from .._proto.api.v0.luminarycloud.pipelines import pipelines_pb2 as pipelinespb


@dataclass
class PipelineRecord:
    id: str
    name: str
    description: str | None
    definition_yaml: str
    create_time: datetime
    update_time: datetime

    def pipeline(self) -> Pipeline:
        return Pipeline._from_yaml(self.definition_yaml)

    @classmethod
    def from_proto(cls, proto: pipelinespb.Pipeline) -> "PipelineRecord":
        return cls(
            id=proto.id,
            name=proto.name,
            description=proto.description,
            definition_yaml=proto.definition_yaml,
            create_time=timestamp_to_datetime(proto.created_at),
            update_time=timestamp_to_datetime(proto.updated_at),
        )


@dataclass
class PipelineJobRecord:
    id: str
    pipeline_id: str
    project_id: str
    name: str
    description: str | None
    status: PipelineJobStatus
    create_time: datetime
    update_time: datetime
    started_at: datetime | None
    completed_at: datetime | None

    @classmethod
    def from_proto(cls, proto: pipelinespb.PipelineJob) -> "PipelineJobRecord":
        return cls(
            id=proto.id,
            pipeline_id=proto.pipeline_id,
            project_id=proto.project_id,
            name=proto.name,
            description=proto.description,
            status=PipelineJobStatus(proto.status),
            create_time=timestamp_to_datetime(proto.created_at),
            update_time=timestamp_to_datetime(proto.updated_at),
            started_at=(
                timestamp_to_datetime(proto.started_at) if proto.HasField("started_at") else None
            ),
            completed_at=(
                timestamp_to_datetime(proto.completed_at)
                if proto.HasField("completed_at")
                else None
            ),
        )


def create_pipeline(
    name: str, pipeline: Pipeline | str, description: str | None = None
) -> PipelineRecord:
    """
    Create a new pipeline.

    Parameters
    ----------
    name : str
        Name of the pipeline.
    pipeline : Pipeline | str
        The pipeline to create. Accepts a Pipeline object or a YAML-formatted pipeline definition.
    description : str, optional
        Description of the pipeline.
    """
    if isinstance(pipeline, Pipeline):
        definition_yaml = pipeline.to_yaml()
    else:
        definition_yaml = pipeline
    req = pipelinespb.CreatePipelineRequest(
        name=name, definition_yaml=definition_yaml, description=description
    )
    res: pipelinespb.CreatePipelineResponse = get_default_client().CreatePipeline(req)
    return PipelineRecord.from_proto(res.pipeline)


def list_pipelines() -> list[PipelineRecord]:
    """
    List all pipelines.
    """
    req = pipelinespb.ListPipelinesRequest()
    res: pipelinespb.ListPipelinesResponse = get_default_client().ListPipelines(req)
    return [PipelineRecord.from_proto(p) for p in res.pipelines]


def get_pipeline(id: str) -> PipelineRecord:
    """
    Get a pipeline by ID.

    Parameters
    ----------
    id : str
        ID of the pipeline to fetch.
    """
    req = pipelinespb.GetPipelineRequest(id=id)
    res: pipelinespb.GetPipelineResponse = get_default_client().GetPipeline(req)
    return PipelineRecord.from_proto(res.pipeline)


def create_pipeline_job(
    pipeline_id: str, args: PipelineArgs, project_id: str, name: str, description: str | None = None
) -> PipelineJobRecord:
    """
    Create a new pipeline job.

    Parameters
    ----------
    pipeline_id : str
        ID of the pipeline to invoke.
    args : PipelineArgs
        Arguments to pass to the pipeline.
    project_id : str
        ID of the project to run the pipeline job in.
    name : str
        Name of the pipeline job.
    description : str, optional
        Description of the pipeline job.
    """

    col_values = [[] for _ in args.params]
    for row in args.rows:
        for i, v in enumerate(row.row_values):
            col_values[i].append(v)

    cols = []

    for i, param in enumerate(args.params):
        if param._represented_type() == str:
            cols.append(
                pipelinespb.PipelineJobArgsColumn(
                    string_column=pipelinespb.PipelineJobArgsColumn.StringColumn(
                        name=param.name,
                        values=col_values[i],
                    )
                )
            )
        elif param._represented_type() == int:
            cols.append(
                pipelinespb.PipelineJobArgsColumn(
                    int_column=pipelinespb.PipelineJobArgsColumn.IntColumn(
                        name=param.name,
                        values=col_values[i],
                    )
                )
            )
        elif param._represented_type() == float:
            cols.append(
                pipelinespb.PipelineJobArgsColumn(
                    double_column=pipelinespb.PipelineJobArgsColumn.DoubleColumn(
                        name=param.name,
                        values=col_values[i],
                    )
                )
            )
        elif param._represented_type() == bool:
            cols.append(
                pipelinespb.PipelineJobArgsColumn(
                    bool_column=pipelinespb.PipelineJobArgsColumn.BoolColumn(
                        name=param.name,
                        values=col_values[i],
                    )
                )
            )

    req = pipelinespb.CreatePipelineJobRequest(
        pipeline_id=pipeline_id,
        args_columns=cols,
        name=name,
        description=description,
        project_id=project_id,
    )
    res: pipelinespb.CreatePipelineJobResponse = get_default_client().CreatePipelineJob(req)
    return PipelineJobRecord.from_proto(res.pipeline_job)


def get_pipeline_job(id: str) -> PipelineJobRecord:
    """
    Get a pipeline job by ID.
    """
    req = pipelinespb.GetPipelineJobRequest(id=id)
    res: pipelinespb.GetPipelineJobResponse = get_default_client().GetPipelineJob(req)
    return PipelineJobRecord.from_proto(res.pipeline_job)


def list_pipeline_jobs() -> list[PipelineJobRecord]:
    """
    List all pipeline jobs.
    """
    req = pipelinespb.ListPipelineJobsRequest()
    res: pipelinespb.ListPipelineJobsResponse = get_default_client().ListPipelineJobs(req)
    return [PipelineJobRecord.from_proto(p) for p in res.pipeline_jobs]
