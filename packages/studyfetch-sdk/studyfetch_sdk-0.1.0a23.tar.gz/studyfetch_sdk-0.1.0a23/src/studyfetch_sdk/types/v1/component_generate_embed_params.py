# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ComponentGenerateEmbedParams", "Features", "Theme"]


class ComponentGenerateEmbedParams(TypedDict, total=False):
    expiry_hours: Annotated[float, PropertyInfo(alias="expiryHours")]
    """Token expiry time in hours"""

    features: Features
    """Feature toggles"""

    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Group IDs for collaboration"""

    height: str
    """Embed height (e.g., "400px", "100vh")"""

    session_id: Annotated[str, PropertyInfo(alias="sessionId")]
    """Session ID for continuity"""

    theme: Theme
    """Theme customization"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID for tracking"""

    width: str
    """Embed width (e.g., "100%", "600px")"""


class Features(TypedDict, total=False):
    enable_bad_words_filter: Required[Annotated[bool, PropertyInfo(alias="enableBadWordsFilter")]]
    """Enable bad words filter"""

    enable_component_creation: Annotated[bool, PropertyInfo(alias="enableComponentCreation")]
    """Enable component creation"""

    enable_follow_ups: Annotated[bool, PropertyInfo(alias="enableFollowUps")]
    """Enable follow-up questions"""

    enable_guardrails: Annotated[bool, PropertyInfo(alias="enableGuardrails")]
    """Enable guardrails"""

    enable_history: Annotated[bool, PropertyInfo(alias="enableHistory")]
    """Enable history"""

    enable_image_sources: Annotated[bool, PropertyInfo(alias="enableImageSources")]
    """Enable image sources"""

    enable_outline: Annotated[bool, PropertyInfo(alias="enableOutline")]
    """Enable outline"""

    enable_transcript: Annotated[bool, PropertyInfo(alias="enableTranscript")]
    """Enable transcript"""

    enable_voice: Annotated[bool, PropertyInfo(alias="enableVoice")]
    """Enable voice input"""

    enable_web_search: Annotated[bool, PropertyInfo(alias="enableWebSearch")]
    """Enable web search"""

    enable_web_search_sources: Annotated[bool, PropertyInfo(alias="enableWebSearchSources")]
    """Enable web search sources"""

    placeholder_text: Annotated[str, PropertyInfo(alias="placeholderText")]
    """Placeholder text"""


class Theme(TypedDict, total=False):
    background_color: Annotated[str, PropertyInfo(alias="backgroundColor")]
    """Background color (hex)"""

    border_radius: Annotated[str, PropertyInfo(alias="borderRadius")]
    """Border radius"""

    font_family: Annotated[str, PropertyInfo(alias="fontFamily")]
    """Font family"""

    font_size: Annotated[str, PropertyInfo(alias="fontSize")]
    """Font size"""

    hide_branding: Annotated[bool, PropertyInfo(alias="hideBranding")]
    """Hide branding"""

    logo_url: Annotated[str, PropertyInfo(alias="logoUrl")]
    """Logo URL"""

    padding: str
    """Padding"""

    primary_color: Annotated[str, PropertyInfo(alias="primaryColor")]
    """Primary color (hex)"""

    secondary_color: Annotated[str, PropertyInfo(alias="secondaryColor")]
    """Secondary color (hex)"""

    text_color: Annotated[str, PropertyInfo(alias="textColor")]
    """Text color (hex)"""
