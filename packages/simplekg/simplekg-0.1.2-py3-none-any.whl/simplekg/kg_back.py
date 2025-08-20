from html import entities
import os
from dotenv import load_dotenv
import pickle
import dspy
import json
import os
import sys
from typing import List, Literal,  Tuple, Optional

from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from .models import Graph
from .utils import load_ontology_embeddings

class KnowledgeGraphGenerator:
    
    def __init__(self, model: str , api_key: str , temperature: float = 0.0, api_base: str = None, chunck_size: int = 0):
        """Initialize the Knowledge Graph Generator with model configuration."""
        self.dspy = dspy
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.api_base = api_base
        self.init_graph(chunk_size=chunck_size)
        self.init_model(model, temperature, api_key, api_base)

    def init_model(self, model: str = None, temperature: float = None, api_key: str = None, api_base: str = None):
        """Initialize or reinitialize the model with new parameters."""
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if api_key is not None:
            self.api_key = api_key
        if api_base is not None:
            self.api_base = api_base

        if self.api_key:
            self.lm = dspy.LM(model=self.model, api_key=self.api_key, temperature=self.temperature, api_base=self.api_base)
        else:
            self.lm = dspy.LM(model=self.model, temperature=self.temperature, api_base=self.api_base)
    
        dspy.configure(lm=self.lm)

    def init_graph(self, text: str = "", path: str = None, chunk_size: int = 0):
        """Initialize an empty graph."""
        if path is None:
            if chunk_size > 0:
                from .utils import chunk_text
                texts = chunk_text(text, chunk_size)
                subgraphs = []
                for t in texts:
                    subgraphs.append(Graph(entities=set(), relations=set(), text=t, concepts=[]))
            else:
                subgraphs = [Graph(entities=set(), relations=set(), text=text, concepts=[])]
            self.graph = Graph(entities=set(), relations=set(), text=text, subgraphs=subgraphs, concepts=[])
        else:
            def custom_decoder(data):
                # This function is called for every object in the JSON data
                # We can check if it's a list that needs to be a tuple
                if isinstance(data, list) and len(data) == 3 and all(isinstance(i, str) for i in data):
                    # A simple check to see if this list should be a tuple
                    return tuple(data)
                return data
            
            with open(path, 'r') as f:
                cgraph_dict = json.load(f, object_hook=custom_decoder)

            self.graph = Graph(**cgraph_dict)
    
    def dump_graph(self, file_path: str):
        """Dump the graph to a file."""
        
        def set_encoder(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        with open(file_path, 'w') as f:
            json.dump(self.graph.model_dump(), f, indent=2, ensure_ascii=False, default=set_encoder)
        

    def extract_entities(self, text: str = None, chunk_size: int = 0):
        """Extract entities from text.
           the text is chuncked into smaller parts (subgraphs) if chunk_size is provided.
           Entities are extracted from each subgraph.
           Finally all subgraphs are merged into the main graph.        
         """
        
        def process_graph(lg: Graph):
            """Process a single graph to extract entities from the subgraphs in the self.graph."""


            class TextEntities(dspy.Signature):
            # __doc__ = f"""Extract *ALL* concepts from the source text. 
            #     Extracted concepts are subjects or objects.
            #     This is for an extraction task, please be THOROUGH and accurate to the reference text."""
                __doc__ = f"""Extract ALL individual concepts and entities mentioned, including specific subcomponents, 
                            regardless of whether broader categories are also mentioned. 
                            Do not merge distinct entities. Return both broad and granular entities.
                            This is for an extraction task, please be THOROUGH and accurate to the reference text."""
            
                source_text: str = dspy.InputField()  
                entities: list[str] = dspy.OutputField(desc="THOROUGH list of key entities")

            extract = dspy.Predict(TextEntities)
            result = extract(source_text=lg.text)
            #lg.entities = set(result.entities)
            return set(result.entities)


        if text:
            self.init_graph(text=text, chunk_size=chunk_size)
        
        if self.graph.text is None:
            raise ValueError("Text must be provided for entity extraction.")

        with ThreadPoolExecutor() as executor:
            entity_sets = list(executor.map(process_graph, self.graph.subgraphs))

        for subgraph, entities in zip(self.graph.subgraphs, entity_sets):
            subgraph.entities = entities

        #merge subgraphs entities to main graph
        for subgraph in self.graph.subgraphs:
            self.graph.entities.update(subgraph.entities)
        self.graph.entities = set(self.graph.entities)  # Ensure entities are unique        
           
    def entities2concepts(self, op_mode = "merge"):
        '''
        Convert (merge/connect) entities to concepts using a dspy signature.
        '''

        def mergeNodesEdges(prefLabel: str, altLabels: list[str]):
            relations = list(self.graph.relations)
            # Filter out relations where subject or object is in altLabels
            # and replace them with the prefLabel.
            # This ensures that all relations involving altLabels are replaced with the prefLabel.
            # This is done to unify the entities under a single concept.
            new_relations = [x for x in relations if x[0] not in  altLabels and x[2] not in altLabels]
            for al in altLabels:
                new_relations.extend([(prefLabel,r,s) for o,r,s in relations if o==al])
                new_relations.extend([(o,r,prefLabel) for o,r,s in relations if s==al])
            
            new_nodes = [x for x in self.graph.entities if x not in altLabels]

            # Update the graph's entities and relations
            self.graph.entities = set(new_nodes)
            self.graph.relations = set(new_relations)


        def getConceptsLLM():
            """Use LLM to propose merge of entities into higher level concepts."""
            class Groups(BaseModel):
                """Each object represents one SKOS concept"""
                
                prefLabel_he: str = Field(..., description="Must be from entities list, the canonical Hebrew label")
                prefLabel_en: str = Field(..., description="the canonical English label")
                altLabels_he: list[str] = Field(..., description="list of Hebrew synonyms / variants")
                altLabels_en: list[str] = Field(..., description="list of English synonyms / variants")
                

            class EntitiesNormalization(dspy.Signature):
                """
                You are an expert in Hebrew linguistic normalization, ontology engineering, and SKOS vocabulary design.

                You receive:
                - A list of concepts (Hebrew terms), automatically extracted from a source text.
                - The source text itself for context validation.

                The concepts may contain duplicates due to:
                - Synonyms
                - Spelling variations
                - Orthographic differences
                - Morphological forms
                - Presence or absence of diacritics

                Your task:
                1. Identify and group concepts that refer to the same underlying meaning or entity.
                2. Use the source text to validate that each group truly refers to the same concept in context.
                3. For each group:
                    a. Choose ONE canonical Hebrew label (prefer the most complete, formal, and unambiguous form).
                    b. Provide all other variants in the group as alternate labels in Hebrew.
                    c. Provide an English translation for the canonical label.
                    d. Provide English translations for the variants, if possible.
                4. Ensure all Hebrew labels preserve original orthography (except for normalization in grouping).
                5. Structure the output so it can be directly mapped to SKOS:
                    - "prefLabel_he": canonical Hebrew label
                    - "prefLabel_en": canonical English label
                    - "altLabels_he": list of Hebrew synonyms/variants
                    - "altLabels_en": list of English synonyms/variants

                Important:
                - Do not merge concepts unless you are confident they are equivalent in meaning in this context.
                - Preserve distinct concepts even if they are superficially similar.
                """

                source_text: str = dspy.InputField(desc="Full source text for context validation")
                concepts: list[str] = dspy.InputField(desc="List of Hebrew concepts extracted from the text")
                groups: list[Groups] = dspy.OutputField(desc="List of grouped concepts with canonical labels and SKOS-compatible alternate labels")

            extract = dspy.Predict(EntitiesNormalization)
            concepts = extract(source_text=self.graph.text, concepts=self.graph.entities)
            return concepts
        
        def mergeConcepts(new_concepts):
            # merge newly detected concepts into the graph's existing concepts

            if len(self.graph.concepts)==0:
                self.graph.concepts = new_concepts.groups
                return
            
            # If the graph already has concepts, merge the new concepts into the existing ones
            existing_concepts = {c.prefLabel_he: c for c in self.graph.concepts}
            for c in new_concepts.groups:
                if c.prefLabel_he in existing_concepts:
                    # If the concept already exists, merge the alternate labels
                    existing_concept = existing_concepts[c.prefLabel_he]
                    existing_concept.altLabels_he.extend(c.altLabels_he)
                    existing_concept.altLabels_en.extend(c.altLabels_en)
                else:
                    # If the concept is new, add it to the graph's concepts
                    self.graph.concepts.append(c)

        # Get concepts from LLM
        new_concepts = getConceptsLLM()
        mergeConcepts(new_concepts)
        # Merge entities in the graph based on the concepts
        for concept in self.graph.concepts:
            if len(concept.altLabels_he) > 0:
                # Merge entities in the graph based on the concept's preferred and alternate labels
                mergeNodesEdges(concept.prefLabel_he, concept.altLabels_he)

    def extract_relations(self, text: str = None, context: str = ""):
        """Extract relations from text."""
        
        def process_graph(lg: Graph):
            """Process a single graph to extract relations from the subgraphs in the self.graph."""
            
            class Relation(BaseModel):
                """Knowledge graph subject-predicate-object tuple."""
                subject: str = Field(..., description="Must be from entities list")
                predicate: str = Field(..., description="The relation between subject and object, expressed in English, even if translation from another language is required.")
                object: str = Field(..., description="Must be from entities list")
            
            class ExtractTextRelations(dspy.Signature):
                __doc__ = f"""Extract subject-predicate-object triples from the source text. 
                            Subject and object *MUST* be from entities list. Entities provided were previously extracted from the same source text.
                            This is for an extraction task, please be thorough, accurate, and faithful to the reference text. {context}"""
                
                source_text: str = dspy.InputField()
                entities: list[str] = dspy.InputField()
                relations: list[Relation] = dspy.OutputField(desc="List of subject-predicate-object tuples. Be thorough.")

            extract = dspy.Predict(ExtractTextRelations)
            result = extract(source_text=lg.text, entities=list(lg.entities))
            res_relations = [(r.subject, r.predicate, r.object) for r in result.relations]
            return set(res_relations)


        if text:
            self.graph.text = text

        if self.graph.text is None:
            raise ValueError("Text must be provided for relation extraction.")

        if len(self.graph.entities)==0:
            raise ValueError("Entities must be extracted before relations can be extracted.")

        with ThreadPoolExecutor() as executor:
            relation_sets = list(executor.map(process_graph, self.graph.subgraphs))
        
        for subgraph, relations in zip(self.graph.subgraphs, relation_sets):
            subgraph.relations = relations
        

        # Merge subgraphs relations to main graph
        for subgraph in self.graph.subgraphs:
            self.graph.relations.update(subgraph.relations)
        self.graph.relations = set(self.graph.relations)  # Ensure relations are unique

        base_graph = Graph(
            entities=self.graph.entities.copy(), 
            relations=self.graph.relations.copy(), 
            text=self.graph.text
        )
        self.graph.base_graph = base_graph  # Store the initial graph before any processing or merging

    def relations2predicates(self, op_mode = "SKOS", granularity: str = "MEDIUM"):
        """
        Convert (merge/connect) relations to predicates using a dspy signature.
        This function uses a dspy signature to normalize relations into predicates.
        The granularity parameter controls how aggressively relations are merged:
        - HIGH: Merge broadly, combining many near-synonyms.
        - MEDIUM: Merge clear synonyms but keep distinct semantic categories.
        - LOW: Keep relations as distinct as possible, only merge exact or trivial variants.
        """
        
        def getpredicateByOntology(ontology_embedding_file, 
                     model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
            """
            Use Ontology relations to map raw relations to preferred labels,
            and return them as a list of Predicate objects.
            """
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            from collections import defaultdict
            from .models import Predicate

            # 1. Collect raw relations (middle element of each triple)
            raw_relations = [x[1] for x in self.graph.relations]

            # 2. Load embedding model
            model = SentenceTransformer(model_name)
            relation_embeddings = model.encode(raw_relations, convert_to_numpy=True, normalize_embeddings=True)

            # 3. Load precomputed SKOS embeddings
            ontology_embeddings, ontology_labels,ontology_texts = load_ontology_embeddings(ontology_embedding_file)

            # 4. Map each raw relation to the closest SKOS label
            cluster_map = defaultdict(list)

            for rel, emb in zip(raw_relations, relation_embeddings):
                sims = cosine_similarity([emb], ontology_embeddings)[0]
                best_idx = int(np.argmax(sims))
                best_skos = ontology_labels[best_idx]
                cluster_map[best_skos].append(rel)

            # 5. Build Predicate objects
            predicates = []
            for ontology_label, variants in cluster_map.items():
                pred = Predicate(
                    prefLabel_en=ontology_label,
                    altLabels_en=sorted(set(variants)),
                    mapping_examples=variants  # here you keep all, or sample if too many
                )
                predicates.append(pred)
            
            class Predicates(BaseModel):
                """List of predicates extracted from the ontology."""
                predicates: List[Predicate] = Field(..., description="List of predicates with preferred and alternate labels.")

            # 6. Return as Predicates model
            predicates_model = Predicates(predicates=predicates)
            return predicates_model

        def getPredicatesLLM(granularity: str = "MEDIUM"):
            """Use LLM to propose merge of entities into higher level concepts."""
            
            from .models import Predicate
            
            class RelationsNormalization(dspy.Signature):
                """
                You are an expert in ontology engineering, SKOS design, and relation normalization.

                You receive:
                - A list of subject–predicate–object triplets, where the predicate (middle element) is the relation to normalize.

                The predicates may contain duplicates or variants due to:
                - Synonyms
                - Morphological or tense variation
                - Different phrasings of the same underlying relation

                Your task:
                1. Extract all unique relation labels from the middle element of each triplet.
                2. Group semantically equivalent relations together.
                3. Merge according to the specified granularity level:
                   - HIGH: Merge broadly, combining many near-synonyms.
                   - MEDIUM: Merge clear synonyms but keep distinct semantic categories.
                   - LOW: Keep relations as distinct as possible, only merge exact or trivial variants.
                4. For each group:
                    a. Choose ONE canonical English label (short, ontology-ready form, e.g., 'isPartOf', 'contains').
                    b. List all other variants as alternate labels.
                    c. Provide representative examples from the input triplets that demonstrate usage of the relation.

                Structure the output as a list of relation groups:
                - "prefLabel_en": canonical predicate
                - "altLabels_en": synonyms/variants
                - "mapping_examples": original forms drawn from the triplets
                """

                triplets: list[tuple[str, str, str]] = dspy.InputField(
                    desc="List of subject–predicate–object triplets; normalize only the middle element (relation)"
                )
                granularity: str = dspy.InputField(
                    desc="Granularity of merging: HIGH (broad merges), MEDIUM (moderate merges), LOW (fine-grained distinctions)"
                )
                predicates: list[Predicate] = dspy.OutputField(
                    desc="Normalized relations grouped under canonical labels"
                )

            extract = dspy.Predict(RelationsNormalization)
            predicates = extract(triplets=self.graph.relations, granularity=granularity)
            return predicates

        def mergePredicates(new_predicates):
            """Merge newly detected predicates into the graph's existing predicates."""
            if len(self.graph.predicates) == 0:
                self.graph.predicates = new_predicates.predicates
                return
                
            # If the graph already has predicates, merge the new predicates into the existing ones
            existing_predicates = {p.prefLabel_en: p for p in self.graph.predicates}
            for p in new_predicates.predicates:
                if p.prefLabel_en in existing_predicates:
                    # If the predicate already exists, merge the alternate labels and examples
                    existing_predicate = existing_predicates[p.prefLabel_en]
                    existing_predicate.altLabels_en.extend(p.altLabels_en)
                    existing_predicate.mapping_examples.extend(p.mapping_examples)
                else:
                    # If the predicate is new, add it to the graph's predicates
                    self.graph.predicates.append(p)

        def checkRelation(subj: str, pred: str, obj: str, relation2predicate: dict):
            """Check if the relation need to be changed to a preferred label."""
            if pred in relation2predicate:
                return (subj, relation2predicate[pred], obj)
            return (subj, pred, obj)

        if op_mode == "LLM":
            new_predicates = getPredicatesLLM(granularity=granularity)
        else:
            ontology_embedding_file = os.getenv(op_mode, None)
            if ontology_embedding_file is None:
                raise ValueError(f"Ontology embedding file not found for mode {op_mode}. Please set the environment variable.")
            new_predicates = getpredicateByOntology(ontology_embedding_file)
        
        mergePredicates(new_predicates)
        
        # relation to predicate dictionary
        rel2pred = {}
        for predicate in self.graph.predicates:
            for alt_label in predicate.altLabels_en:
                rel2pred[alt_label] = predicate.prefLabel_en

        new_relations = [checkRelation(subj, pred, obj, rel2pred) for subj, pred, obj in self.graph.relations]
        self.graph.relations = set(new_relations)


    def visualize(self, output_path=None):
        from pyvis.network import Network
        from collections import defaultdict
        import math
        import random

        def random_color():
            """Generate a random pastel color in hex."""
            # Generate slightly lighter pastel colors
            r = int(127 + random.random() * 128)
            g = int(127 + random.random() * 128)
            b = int(127 + random.random() * 128)
            return f"#{r:02x}{g:02x}{b:02x}"

        def graph_to_pyvis_data():
            """Convert a Graph object into pyvis-compatible node and edge lists."""
            nodes = []  # list of dicts: {id, label, title, color, size, ...}
            edges = []  # list of dicts: {source, target, label, title, color, ...}

            default_node_color = "#ADD8E6"  # Light blue
            default_edge_color = "#A9A9A9"  # Dark gray
            cluster_colors = {}
            edge_cluster_colors = {}
            node_degrees = defaultdict(int)  # To calculate node sizes

            # Pre-calculate degrees
            for subj, _, obj in self.graph.relations:
                node_degrees[subj] += 1
                node_degrees[obj] += 1

            for entity in self.graph.entities:
                degree = node_degrees.get(entity, 0)
                size = min(max(10 + 5 * math.log(1 + degree), 10), 40)
                title = f"<b>Entity:</b> {entity}<br><b>Degree:</b> {degree}"
                nodes.append(
                    {
                        "id": entity,
                        "label": entity,
                        "title": title,
                        "color": default_node_color,
                        "size": size,
                        "shape": "dot",
                    }
                )

            #unique_preds = self.graph.edges
            unique_preds = {relation[1] for relation in self.graph.relations}
            pred_colors = {pred: random_color() for pred in unique_preds}
            for subj, pred, obj in self.graph.relations:
                color = pred_colors.get(pred, default_edge_color)
                title = f"<b>Relation:</b> {pred}"
                edges.append(
                    {
                        "source": subj,
                        "target": obj,
                        "label": pred,
                        "title": title,
                        "color": color,
                    }
                )

            return nodes, edges



        """Render the graph object to an interactive HTML file using pyvis."""
        if not self.graph or not self.graph.entities or not self.graph.relations:
            raise ValueError("Error: Cannot visualize empty or invalid graph\n")

        nodes, edges = graph_to_pyvis_data()

        try:
            net = Network(
                height="800px",
                width="100%",
                directed=True,
                notebook=output_path is None,
                cdn_resources="remote",
                
            )
        except Exception as e:
            raise ValueError(f"Error initializing Network: {e}\n")
            
        # Enhanced aesthetics and physics options - Removed comments for JSON compatibility
        net.set_options(
            """
            var options = {
            "nodes": {
                "font": {"size": 14, "face": "tahoma"},
                "borderWidth": 1,
                "borderWidthSelected": 2
            },
            "edges": {
                "arrows": {"to": {"enabled": true, "scaleFactor": 0.6}},
                "color": {"inherit": false},
                "smooth": {"type": "dynamic", "roundness": 0.2},
                "font": {"size": 11, "face": "tahoma", "align": "middle", "strokeWidth": 2, "strokeColor": "#ffffff"},
                "width": 1.5,
                "hoverWidth": 0.5,
                "selectionWidth": 1
            },
            "physics": {
                "enabled": true,
                "barnesHut": {
                "gravitationalConstant": -25000,
                "centralGravity": 0.1,
                "springLength": 120,
                "springConstant": 0.05,
                "damping": 0.15,
                "avoidOverlap": 0.5
                },
                "maxVelocity": 50,
                "minVelocity": 0.5,
                "solver": "barnesHut",
                "stabilization": {
                "enabled": true,
                "iterations": 1000,
                "updateInterval": 50,
                "onlyDynamicEdges": false,
                "fit": true
                },
                "timestep": 0.5,
                "adaptiveTimestep": true
            },
            "interaction": {
                "dragNodes": true,
                "dragView": true,
                "hideEdgesOnDrag": false,
                "hideNodesOnDrag": false,
                "hover": true,
                "hoverConnectedEdges": true,
                "keyboard": {"enabled": true},
                "multiselect": true,
                "navigationButtons": true,
                "selectable": true,
                "selectConnectedEdges": true,
                "tooltipDelay": 200,
                "zoomView": true
            },
            "manipulation": {
                "enabled": false
            }
            }
            """
        )

        # Add nodes and edges with specific properties
        try:
            for n in nodes:
                net.add_node(
                    n["id"],
                    label=n["label"],
                    title=n.get("title"),  # HTML title for hover tooltip
                    color=n.get("color"),
                    size=n.get("size"),
                    shape=n.get("shape", "dot"),  # Use shape if defined
                )

            for e in edges:
                net.add_edge(
                    e["source"],
                    e["target"],
                    label=e.get("label"),
                    title=e.get("title"),  # HTML title for hover tooltip
                    color=e.get("color"),
                )

            if output_path is None:
                return net
            else:
                net.write_html(output_path)
            #print(f"Successfully generated visualization: {output_path}")
        except Exception as e:
            #print(f"edge: {e}\nnodes: {nodes}\n edges: {edges}")
            raise ValueError(f"Error generating HTML file with pyvis: {e}")
            