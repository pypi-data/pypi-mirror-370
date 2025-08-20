from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Tuple, Optional, Dict, List, Set


class Concept(BaseModel):
    """Each object represents one SKOS concept"""
    
    prefLabel_he: str = Field(..., description="The canonical Hebrew label. Must be EXACTLY one of the provided concepts. Do not invent new concept.")
    prefLabel_en: str = Field(..., description="the canonical English label")
    altLabels_he: list[str] = Field(default_factory=list, description="list of Hebrew synonyms / variants")
    altLabels_en: list[str] = Field(default_factory=list, description="list of English synonyms / variants")
    conceptDescription_he: str = Field(..., description="A short description of the concept, in Hebrew. This is not a definition, but rather a short description of the concept's meaning or usage.")
    

class Relation(BaseModel):
    """Knowledge graph subject–predicate–object triple."""
    subject: str = Field(..., description="Must match EXACTLY a string from entities list. Do not invent or alter.")
    predicate: str = Field(..., description="Short English verb phrase (e.g., 'is part of', 'is located in').")
    object: str = Field(..., description="Must match EXACTLY a string from entities list. Do not invent or alter.")



class Predicate(BaseModel):
    """Each object represents one canonical relation (predicate)."""
    prefLabel_en: str = Field( ..., description="Canonical English label for the relation, formatted for ontology use (short, verb phrase, camelCase if appropriate)")
    altLabels_en: list[str] = Field( ..., description="List of alternative phrasings or synonyms for the relation")
    mapping_examples: list[str] = Field( ...,description="Examples of raw relation strings from the input that map to this canonical relation" )


class Graph(BaseModel):
  entities: Set[str] = Field(..., description="All entities including additional ones from response")
  relations: Set[Tuple[str, str, str]] = Field(..., description="List of (subject, predicate, object) triples")
  text:str = Field(..., description="The original text used to generate the graph")
  concepts: Optional[List[Concept]] = Field(default_factory=list, description="List of concepts")
  #predicates: Optional[List[Predicate]] = Field(default_factory=list, description="List of predicates")
  ontologies: Optional[Dict[str, List[Predicate]]] = Field(default_factory=dict, description="Dictionary mapping ontology names to lists of predicates")
  subgraphs: Optional[List[Graph]] = Field(default_factory=list, description="List of subgraphs")
  base_graph: Optional[Graph] = Field(default=None, description="A copy of the initial graph before any processing or merging")


  
# Resolve forward references
Graph.update_forward_refs()