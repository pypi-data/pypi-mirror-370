"""
Provider Enum Module.

This module defines the `Provider` enum, which lists the supported AI service providers
available for use in the application. These providers are used to dynamically configure
and initialize the appropriate AI models and services.
"""

# Standard library imports
from enum import Enum


class Provider(str, Enum):
    """
    Enum for AI service providers.

    This enum represents the various AI service providers that can be selected
    for initializing and interacting with language models.

    Attributes:
        OpenAI (str): Represents the OpenAI provider.
        Anthropic (str): Represents the Anthropic provider.
        Mistral (str): Represents the Mistral provider.
        Fireworks (str): Represents the Fireworks provider.
        GoogleGenAI (str): Represents the Google Generative AI provider.
        Grok (str): Represents the Grok provider.
        Groq (str): Represents the Groq provider.
        VertexAI (str): Represents the Google Vertex AI provider.

    Example:
        >>> from lib.enums.model_enum import Provider
        >>> provider = Provider.OpenAI
        >>> print(provider)
        OpenAI

        >>> if provider == Provider.OpenAI:
        ...     print("Using OpenAI as the provider.")
        Using OpenAI as the provider.
    """

    OpenAI = "OpenAI"
    Anthropic = "Anthropic"
    Mistral = "Mistral"
    Fireworks = "Fireworks"
    GoogleGenAI = "GoogleGenAI"
    Grok = "Grok"
    Groq = "Groq"
    VertexAI = "VertexAI"
