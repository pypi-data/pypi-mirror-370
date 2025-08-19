# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["ComponentListParams"]


class ComponentListParams(TypedDict, total=False):
    type: Literal[
        "chat",
        "data_analyst",
        "flashcards",
        "scenarios",
        "practice_test",
        "audio_recap",
        "tutor_me",
        "explainers",
        "uploads",
        "chat_analytics",
    ]
    """Filter by component type"""
