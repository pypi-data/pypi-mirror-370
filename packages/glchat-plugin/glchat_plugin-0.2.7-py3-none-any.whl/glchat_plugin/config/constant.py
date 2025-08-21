"""Constants for the API.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

import warnings
from enum import StrEnum


class SearchType(StrEnum):
    """The type of search to perform.

    Attributes:
        NORMAL: Get answer from chatbot knowledge.
        SEARCH: Get answer from various connectors.
        WEB: Get more relevant information from the web. (DEPRECATED)
            Web Search uses real-time data. Agent selection isn't available in this mode.
        DEEP_RESEARCH: Get answer from Deep Research Agent.
    """

    NORMAL = "normal"
    SEARCH = "search"
    _WEB = "web"  # Underscore to hide it from normal use
    DEEP_RESEARCH = "deep_research"

    @property
    def WEB(cls) -> "SearchType":
        """Deprecated: Use SEARCH instead.

        Will be removed in version 0.3.0
        """
        warnings.warn(
            "SearchType.WEB is deprecated and will be removed in a future version. Use SearchType.SEARCH instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls._WEB
