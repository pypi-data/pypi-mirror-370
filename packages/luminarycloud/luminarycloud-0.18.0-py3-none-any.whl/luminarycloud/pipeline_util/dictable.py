from dataclasses import fields, is_dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luminarycloud.pipelines.parameters import PipelineParameter


class PipelineDictable:
    """
    A mixin for dataclasses that can contain PipelineParameters and/or other PipelineDictables
    (i.e. it's recursive). Used to construct a dictionary that can be serialized to YAML for a
    Pipeline definition, and collects all PipelineParameters encountered along the way.
    """

    def _to_pipeline_dict(self) -> tuple[dict, list["PipelineParameter"]]:
        if not is_dataclass(self):
            raise ValueError("PipelineDictable can only be used on dataclasses")
        result = {}
        params = []
        for field in fields(self):
            value = getattr(self, field.name)
            if hasattr(value, "_to_pipeline_dict"):
                result[field.name], downstream_params = value._to_pipeline_dict()
                params.extend(downstream_params)
            else:
                result[field.name] = value
        return result, params
