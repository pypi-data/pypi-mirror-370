"""Base Pipeline Preset Config.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    NONE
"""

from typing import Any

from pydantic import BaseModel

from glchat_plugin.config.constant import SearchType


class BasePipelinePresetConfig(BaseModel):
    """A Pydantic model representing the base preset configuration of all pipelines.

    Attributes:
        pipeline_preset_id (str): The pipeline preset id.
        supported_models (dict[str, Any]): The supported models.
        supported_agents (list[str]): The supported agents.
        support_pii_anonymization (bool): Whether the pipeline supports pii anonymization.
        support_multimodal (bool): Whether the pipeline supports multimodal.
        use_docproc (bool): Whether to use the document processor.
        search_types (list[SearchType]): The supported search types.
    """

    pipeline_preset_id: str
    supported_models: dict[str, Any]
    supported_agents: list[str]
    support_pii_anonymization: bool
    support_multimodal: bool
    use_docproc: bool
    search_types: list[SearchType]
