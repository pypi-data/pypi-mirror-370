# ABOUTME: Re-export all types from google.genai.types for convenient access
# ABOUTME: Users can import from gemini_parallel.types instead of google.genai.types

from google.genai.types import *

# Explicitly list commonly used types for better IDE support
from google.genai.types import (
    # Core content types
    Content,
    Part,
    File,
    
    # Generation config and related
    GenerateContentConfig,
    GenerationConfig,
    ThinkingConfig,
    SpeechConfig,
    VoiceConfig,
    PrebuiltVoiceConfig,
    MultiSpeakerVoiceConfig,
    SpeakerVoiceConfig,
    
    # Response types
    GenerateContentResponse,
    Candidate,
    
    # Safety
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    
    # Schema
    Schema,
    
    # Modalities and media
    Modality,
    MediaResolution,
    
    # Tools
    Tool,
    ToolConfig,
    FunctionDeclaration,
    
    # Others
    HttpOptions,
    ModelSelectionConfig,
    AutomaticFunctionCallingConfig,
)

# Make sure __all__ is defined for proper star imports
__all__ = [
    # Re-export everything from genai.types
    'Content',
    'Part', 
    'File',
    'GenerateContentConfig',
    'GenerationConfig',
    'ThinkingConfig',
    'SpeechConfig',
    'VoiceConfig',
    'PrebuiltVoiceConfig',
    'MultiSpeakerVoiceConfig',
    'SpeakerVoiceConfig',
    'GenerateContentResponse',
    'Candidate',
    'SafetySetting',
    'HarmCategory',
    'HarmBlockThreshold',
    'Schema',
    'Modality',
    'MediaResolution',
    'Tool',
    'ToolConfig',
    'FunctionDeclaration',
    'HttpOptions',
    'ModelSelectionConfig',
    'AutomaticFunctionCallingConfig',
]