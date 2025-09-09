"""
Core processing modules for PDF extraction and knowledge graph construction
"""

from .pdf_processor import MedicalDevicePDFProcessor
from ..ai_extraction.hierarchical_extractor import HierarchicalEntityExtractor as EntityExtractor
# from .knowledge_graph import KnowledgeGraphManager
from .ontology_builder import OntologyBuilder as OntologyManager
# from .deduplicator import Deduplicator

__all__ = [
    'MedicalDevicePDFProcessor',
    'EntityExtractor',
    # 'KnowledgeGraphManager',
    'OntologyManager',
    # 'Deduplicator'
]
