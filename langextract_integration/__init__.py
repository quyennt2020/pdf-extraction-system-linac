"""
LangExtract Integration Module for Medical Device Ontology System

This module integrates Google's LangExtract library with the existing 
PDF extraction system to provide enhanced entity extraction capabilities
specialized for LINAC medical devices.

Key Features:
- Source grounding for precise entity location tracking
- Multi-pass extraction for improved recall
- Schema-constrained extraction for consistent output
- Interactive visualization for expert review
"""

from .linac_extractor import LinacExtractor, LinacExtractionConfig
from .medical_schema_builder import MedicalSchemaBuilder
from .langextract_bridge import LangExtractBridge, ExtractionConfig
from .grounding_visualizer import GroundingVisualizer

__all__ = [
    "LinacExtractor",
    "LinacExtractionConfig",
    "MedicalSchemaBuilder", 
    "LangExtractBridge",
    "ExtractionConfig",
    "GroundingVisualizer"
]

__version__ = "1.0.0"