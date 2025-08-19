# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.pipelines import pipelines_pb2 as pipelinespb


class PipelineJobStatus(IntEnum):
    """
    Status of a pipeline job.

    Attributes
    ----------
    PENDING
    RUNNING
    COMPLETED
    FAILED
    """

    UNSPECIFIED = pipelinespb.PIPELINE_JOB_STATUS_UNSPECIFIED

    PENDING = pipelinespb.PIPELINE_JOB_STATUS_PENDING
    RUNNING = pipelinespb.PIPELINE_JOB_STATUS_RUNNING
    COMPLETED = pipelinespb.PIPELINE_JOB_STATUS_COMPLETED
    FAILED = pipelinespb.PIPELINE_JOB_STATUS_FAILED
