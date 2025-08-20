"""
SimpleKG: A complete workflow for generating, normalizing, and visualizing Knowledge Graphs
from unstructured Hebrew text.

This package integrates LLM-based extraction, entity and relation normalization,
and ontology alignment (SKOS, Dublin Core, CIDOC CRM, or custom).
"""

__version__ = "0.1.0"
__author__ = "Hadar Miller"
__email__ = "your.email@example.com"

# Import main classes and functions for easy access
from .kg import KnowledgeGraphGenerator
from .models import Graph, Predicate
from .utils import load_ontology_embeddings, chunk_text

# Define what gets imported with "from simplekg import *"
__all__ = [
    "KnowledgeGraphGenerator",
    "Graph", 
    "Predicate",
    "load_ontology_embeddings",
    "chunk_text",
]

# Package metadata
def get_version():
    """Get the version of the simplekg package."""
    return __version__