"""
SimpleKG: A complete workflow for generating, normalizing, and visualizing Knowledge Graphs
from unstructured Hebrew text.

This package integrates LLM-based extraction, entity and relation normalization,
and ontology alignment (SKOS, Dublin Core, CIDOC CRM, or custom).
"""

__version__ = "0.1.2"
__author__ = "Hadar Miller"
__email__ = "miller.hadar@gmail.com"

# Import main classes and functions for easy access
from .kg import KnowledgeGraphGenerator
from .models import Graph, Predicate
from .utils import load_ontology_embeddings, chunk_text

# Set up NLTK data on import
from .nltk_setup import ensure_nltk_data
try:
    ensure_nltk_data()
except Exception as e:
    # Silently handle any NLTK setup issues
    pass

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