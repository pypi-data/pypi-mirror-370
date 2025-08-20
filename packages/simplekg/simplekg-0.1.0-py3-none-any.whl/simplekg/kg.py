from html import entities
import os
from dotenv import load_dotenv
import pickle
import dspy
import json
import os
import sys
from typing import List, Literal,  Tuple, Optional, Set, Dict

from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from .models import Graph, Concept, Relation
from .utils import load_ontology_embeddings, is_english

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

    def init_model(self, model: str = None, temperature: float = None, api_key: str = None, max_tokens: int = 8000):
        """Initialize or reinitialize the model with new parameters."""
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if api_key is not None:
            self.api_key = api_key
        
        self.max_tokens = max_tokens

        if self.api_key:
            self.lm = dspy.LM(model=self.model, api_key=self.api_key, temperature=self.temperature,  max_tokens=self.max_tokens)
        else:
            self.lm = dspy.LM(model=self.model, temperature=self.temperature,  max_tokens=self.max_tokens)

        dspy.configure(lm=self.lm)

    def init_graph(self, text: str = "", path: str = None, chunk_size: int = 0):
        """Initialize an empty graph."""
        self.relation_embeddings = None
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


    def extractConcepts(self, text: str = None, chunk_size: int = 0, verbose: bool = False):
        """Extract concepts from text.
           the text is chuncked into smaller parts (subgraphs) if chunk_size is provided.
           Concepts are extracted from each subgraph.
           Finally all subgraphs are merged into the main graph.        
         """
        
        def deDupConcepts(concepts: List[Concept]):
            # Remove duplicates
            ret = []
            ret_labels = []
            for c in concepts:
                if c.prefLabel_he not in ret_labels:
                    ret.append(c)
                    ret_labels.append(c.prefLabel_he)

            return ret
            

        def process_graph(lg: Graph):
            """Process a single graph to extract entities from the subgraphs in the self.graph."""


            class TextEntities(dspy.Signature):
                """
                Extract ALL individual concepts and entities from the source text.

                Requirements:
                - Extract every entity explicitly mentioned, including fine-grained subcomponents and broader categories.
                - Do not merge distinct entities.
                - Each extracted entity MUST appear in the output as `prefLabel_he`.
                - `altLabels_he` must always be an empty list [].
                - `altLabels_en` must always be an empty list [].
                - Provide SKOS-compatible Concept objects with Hebrew/English labels and a short Hebrew description.
                - Be thorough and faithful to the reference text.
                """

                source_text: str = dspy.InputField(desc="Full source text for entity extraction.")
                
                concepts: list[Concept] = dspy.OutputField(
                    desc="List of Concept objects. Each entity from the text appears as prefLabel_he. altLabels_he must remain empty."
                )

            extract = dspy.Predict(TextEntities)
            result = extract(source_text=lg.text)
            
            
            return result.concepts


        if text:
            self.init_graph(text=text, chunk_size=chunk_size)
        
        if self.graph.text is None:
            raise ValueError("Text must be provided for entity extraction.")

        with ThreadPoolExecutor() as executor:
            entity_sets = list(executor.map(process_graph, self.graph.subgraphs))

        for subgraph, concepts in zip(self.graph.subgraphs, entity_sets):
            subgraph.concepts = deDupConcepts(concepts)
            subgraph.entities = {c.prefLabel_he for c in concepts}

        #merge subgraphs entities to main graph
        graph_concept_labels = {c.prefLabel_he for c in self.graph.concepts}
        for subgraph in self.graph.subgraphs:
            self.graph.entities.update(subgraph.entities)
            # Merge only new concepts, that are concepts with new prefLabels_he
            # This ensures that we do not duplicate concepts already present in the main graph
            for c in subgraph.concepts:
                if c.prefLabel_he not in graph_concept_labels:
                    self.graph.concepts.append(c)
                else:
                    # Merge the description of the two concepts.
                    existing_concept = next((x for x in self.graph.concepts if x.prefLabel_he == c.prefLabel_he), None)
                    if existing_concept:
                        existing_concept.conceptDescription_he += f". {c.conceptDescription_he}"
                
            

            
        self.graph.entities = set(self.graph.entities)  # Ensure entities are unique        
        self.graph.concepts = deDupConcepts(self.graph.concepts)

        if verbose:
            print(f"Number of subgraphs: {len(self.graph.subgraphs)}")
            print(f"Number of concepts: {len(self.graph.concepts)}")
            print(f"concepts: " + ", ".join(self.graph.entities))


    def _extractRelations(self, text: str = None, context: str = "", verbose: bool = False):
        """Extract relations from text."""
        
        def process_graph(lg: Graph):
            """Process a single graph to extract relations from the subgraphs in the self.graph."""
            
            class Relation(BaseModel):
                """Knowledge graph subject-predicate-object tuple."""
                subject: str = Field(..., description="Must be EXACTLY  one of the provided entities list. Do not invent new entities.")
                predicate: str = Field(..., description="The relation between subject and object, Must be expressed in English, even if translation from another language is required.")
                object: str = Field(..., description="Must be EXACTLY  one of the provided entities list. Do not invent new entities.")
            
            class ExtractTextRelations(dspy.Signature):
                """
                    Extract subject–predicate–object triples from the source text.

                    Rules:
                    - Subject and object MUST be chosen verbatim from the 'entities' list. 
                    Do not invent, translate, or modify them.
                    - Predicate MUST be in English, a short verb phrase (e.g., 'is part of', 'is located in').
                    - If no valid subject/object pair exists, skip that triple.
                    - Do not output free text or commentary, only structured JSON.

                    Output format example:
                    [
                    {"subject": "Entity1", "predicate": "is located in", "object": "Entity2"},
                    {"subject": "Entity3", "predicate": "is part of", "object": "Entity4"}
                    ]
                    """
                
                source_text: str = dspy.InputField(desc="The text to extract relations from.")
                entities: list[str] = dspy.InputField(desc="List of valid entities. Subjects/objects MUST come from this list.")
                relations: list[Relation] = dspy.OutputField(desc="List of {subject, predicate, object}. If no triples, return [].")

            extract = dspy.Predict(ExtractTextRelations)
            result = extract(source_text=lg.text, entities=list(lg.entities))

            # Filter out relations where subject or object is not in the entities list
            valid_entities = set(lg.entities)
            res_relations = []
            for r in result.relations:
                if r.subject in valid_entities and r.object in valid_entities:
                    res_relations.append((r.subject, r.predicate, r.object))
                else:
                    # drop or log invalid triples
                    continue

            # Validate all predicates are in English
            from .utils import is_english

            for r in result.relations:
                if not is_english(r.predicate):
                   raise ValueError(f"extract_relations --> Invalid predicate found: {r.predicate}")

            #res_relations = [(r.subject, r.predicate, r.object) for r in result.relations]
            return set(res_relations)


        if text:
            self.graph.text = text

        if self.graph.text is None:
            raise ValueError("Text must be provided for relation extraction.")

        if len(self.graph.entities)==0:
            raise ValueError("Entities must be extracted before relations can be extracted.")

        with ThreadPoolExecutor(max_workers=2) as executor:
            relation_sets = list(executor.map(process_graph, self.graph.subgraphs))
        
        for subgraph, relations in zip(self.graph.subgraphs, relation_sets):
            subgraph.relations = relations

        # Merge subgraphs relations to main graph
        for subgraph in self.graph.subgraphs:
            self.graph.relations.update(subgraph.relations)
        self.graph.relations = set(self.graph.relations)  # Ensure relations are unique

        if verbose:
            print(f"Number of RDF relations: {len(self.graph.relations)}")
        
        base_graph = Graph(
            entities=self.graph.entities.copy(), 
            relations=self.graph.relations.copy(), 
            text=self.graph.text
        )
        self.graph.base_graph = base_graph  # Store the initial graph before any processing or merging


    def extractRelations(self, text: str = None, context: str = "", verbose: bool = False):
        """Extract relations from text, robust to schema errors and rate limits."""

        class ExtractTextRelations(dspy.Signature):
            """
            Extract subject–predicate–object triples from the source text.

            Rules:
            - Subject and object MUST be chosen verbatim from the 'entities' list.
            - Predicate MUST be in English, expressed as a short verb phrase.
            - If no valid triple exists, return [].
            - Do not output commentary, only structured JSON.

            Output format example:
            [
            {"subject": "Entity1", "predicate": "is located in", "object": "Entity2"},
            {"subject": "Entity3", "predicate": "is part of", "object": "Entity4"}
            ]
            """

            source_text: str = dspy.InputField(desc="The text to extract relations from.")
            entities: List[str] = dspy.InputField(desc="List of valid entities. Subjects/objects MUST come from this list.")
            relations: List[Relation] = dspy.OutputField(desc="List of subject–predicate–object triples.")


        def process_graph(lg) -> Set[Tuple[str, str, str]]:
            """Extract relations for a single subgraph, with retry on rate-limit."""

            extract = dspy.Predict(ExtractTextRelations)

            retries = 0
            while True:
                try:
                    result = extract(source_text=lg.text, entities=list(lg.entities))
                    break
                except Exception as e:
                    if "RateLimitError" in str(e) and retries < 5:
                        wait_time = 2 ** retries
                        if verbose:
                            print(f"Rate limit hit. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        raise

            valid_entities = set(lg.entities)
            res_relations = []

            for r in result.relations:
                subj = r.subject.strip()
                obj = r.object.strip()
                pred = r.predicate.strip()

                # Filter subject/object
                if subj not in valid_entities or obj not in valid_entities:
                    continue

                # Validate predicate is English
                if not is_english(pred):
                    if verbose:
                        print(f"Dropped non-English predicate: {pred}")
                    continue

                res_relations.append((subj, pred, obj))

            return set(res_relations)


        # If text is provided, update graph text
        if text:
            self.graph.text = text

        if self.graph.text is None:
            raise ValueError("Text must be provided for relation extraction.")

        if len(self.graph.entities) == 0:
            raise ValueError("Entities must be extracted before relations can be extracted.")

        # Concurrency control to respect rate limits
        with ThreadPoolExecutor(max_workers=2) as executor:
            relation_sets = list(executor.map(process_graph, self.graph.subgraphs))

        # Attach relations back to subgraphs
        for subgraph, relations in zip(self.graph.subgraphs, relation_sets):
            subgraph.relations = relations

        # Merge subgraph relations into main graph
        for subgraph in self.graph.subgraphs:
            self.graph.relations.update(subgraph.relations)

        self.graph.relations = set(self.graph.relations)

        if verbose:
            print(f"Number of RDF relations: {len(self.graph.relations)}")

        # Store baseline graph
        base_graph = Graph(
            entities=self.graph.entities.copy(),
            relations=self.graph.relations.copy(),
            text=self.graph.text,
        )
        self.graph.base_graph = base_graph


    def groupConcepts(self, op_mode = "merge", chunk_size: int = 50, threshold: int = 100, max_iterations=2, verbose: bool = False):
        '''
        Convert (merge/connect) entities to concepts using a dspy signature.
        '''

        def alignNodesEdges():
            # convert entities to the concept prefLabel_he
            label2concept = {
                                label: concept.prefLabel_he
                                for concept in self.graph.concepts
                                for label in concept.altLabels_he
                            }
            self.graph.entities = set([label2concept.get(e, e) for e in self.graph.entities])
            self.graph.relations = set([(label2concept.get(s, s), r, label2concept.get(o, o)) for s, r, o in self.graph.relations]) 

        def groupConceptsLargeLLM(chunk_size= chunk_size, threshold= threshold, max_iterations= max_iterations,verbose: bool = verbose):
            """
            Scalable concept grouping using LLM with parallel batching.
            
            Args:
                chunk_size (int): Number of concepts per batch (to fit LLM context).
                threshold (int): When the number of concepts drops below this, 
                                run a final global merge in one pass.
                max_iterations (int): Maximum number of iterations to prevent infinite loops.
                verbose (bool): Print progress info.
            """

            class GroupConcepts(dspy.Signature):
                """
                You are an expert in ontology engineering and Hebrew linguistic normalization.

                You receive:
                - A list of Concept objects, each with canonical labels, alternate labels, and a Hebrew description.

                The concepts may contain duplicates due to:
                - Synonyms
                - Spelling variations
                - Orthographic differences
                - Morphological forms
                - Presence or absence of diacritics

                Your task:
                1. Analyze the concepts (prefLabel_he, altLabels_he, conceptDescription_he).
                2. Detect groups of concepts that clearly refer to the same underlying meaning.
                3. For each group:
                    - Select ONE canonical concept to keep.
                    - Populate its 'altLabels_he' with prefLabel_he values of all grouped concepts.
                    - Populate its 'altLabels_en' with English translations of all grouped concepts.
                    - Rewrite or extend the conceptDescription_he to reflect the merged group.
                4. Do not omit any required field, even if you must use a minimal placeholder like 'No description provided.'”
                5. Ensure every input concept is accounted for in exactly one output group (no omissions).
                6. Do not invent new concepts — only reorganize the provided ones.
                
                Output MUST be a JSON object with exactly one top-level field: 'grouped_concepts',
                which is a list of Concept objects.

                Example:
                {
                "grouped_concepts": [
                    {
                    "prefLabel_he": "אידיאות חדשות",
                    "prefLabel_en": "New Ideas",
                    "altLabels_he": ["אידיאות חדשות"],
                    "altLabels_en": ["New Ideas"],
                    "conceptDescription_he": "רעיונות חדשים המתפתחים...",
                    }
                ]
                }
                            
                """

                concepts: List[Concept] = dspy.InputField(
                    desc="List of Concept objects extracted from the text, with labels and descriptions."
                )
                grouped_concepts: List[Concept] = dspy.OutputField(
                    desc="List of merged Concept objects, Each object MUST include prefLabel_he, prefLabel_en, altLabels_he, altLabels_en, conceptDescription_he (non-empty string)"
                )

            extract = dspy.Predict(GroupConcepts)

            def process_chunk(chunk):
                """Process one chunk of concepts with the LLM."""
                result = extract(concepts=chunk)
                return result.grouped_concepts

            current_concepts = self.graph.concepts

            round_no = 1
            while len(current_concepts) > threshold:
                if verbose:
                    print(f"[Round {round_no}] Grouping {len(current_concepts)} concepts in parallel batches...")

                # Split into chunks
                chunks = [current_concepts[i:i + chunk_size] for i in range(0, len(current_concepts), chunk_size)]

                # Process chunks in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    results = list(executor.map(process_chunk, chunks))

                # Flatten results
                current_concepts = [c for group in results for c in group]

                if verbose:
                    print(f"[Round {round_no}] Reduced to {len(current_concepts)} concepts.")
                round_no += 1

                if round_no > max_iterations:
                    print(f"Reached maximum iterations ({max_iterations}). Stopping early.")
                    break

            # Final consolidation pass
            if len(current_concepts) <= threshold:
                if verbose:
                    print(f"[Final Round] Consolidating {len(current_concepts)} concepts in a single pass.")
                current_concepts = extract(concepts=current_concepts).grouped_concepts
            
            return current_concepts


        #self.graph.concepts = mergeConceptsLLM()
        self.graph.concepts =  groupConceptsLargeLLM(chunk_size = chunk_size, threshold = threshold, max_iterations=max_iterations,verbose= verbose)
        if verbose:
            print(f"Number of concepts after grouping: {len(self.graph.concepts)}")
        
        alignNodesEdges()
        
        base_graph = Graph(
            entities=self.graph.entities.copy(), 
            relations=self.graph.relations.copy(), 
            text=self.graph.text
        )
        self.graph.base_graph = base_graph  # Store the initial graph before any processing or merging

    

    def ontologyRecommendation(self):
        if self.graph.base_graph is None:
            return "No base graph available. Please run extract_entities and extract_relations first."
        
        class OntologySelector(dspy.Signature):
            """
            Given:
                - A set of candidate ontologies with their relations and descriptions.
                - A list of target relations (in natural language, possibly multilingual).
            Task:
                - Select the ontology that best covers the given relations.
                - Justify the choice with reference to ontology focus (events, places, names, metadata).
            Output:
                - primary_ontology: str (name of the ontology that best fits)
                - mapping_strategy: str (how relations map to the ontology concepts)
                - rationale: str (explanation of why this ontology is the best fit)
            """

            candidate_ontologies = dspy.InputField(type=str, desc="Ontology descriptions and relation sets, as text")
            target_relations = dspy.InputField(type=list, desc="List of relations to be modeled")
            primary_ontology = dspy.OutputField(type=str, desc="Name of best ontology")
            mapping_strategy = dspy.OutputField(type=str, desc="How to map input relations to ontology properties")
            rationale = dspy.OutputField(type=str, desc="Explanation of the decision")

        extract = dspy.Predict(OntologySelector)

        # Get the path to the ontologies.txt file relative to this module
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontologies_file = os.path.join(current_dir, "ontologies.txt")
        
        with open(ontologies_file, "r") as f:
            ontologies_text = f.read()

        result = extract(candidate_ontologies=ontologies_text,
                         target_relations=list(self.graph.base_graph.relations))
        respond = f"Based on the relations extracted, The Primary Ontology: {result.primary_ontology}\nThe mapping strategy: {result.mapping_strategy}\nRationale: {result.rationale}"
        return respond


    def relations2ontology(self, ontologies: list[str] = ["SKOS"], granularity: str = "MEDIUM"):
        """
        Convert (merge/connect) relations to predicates using a dspy signature.
        This function uses a dspy signature to normalize relations into predicates.
        The granularity parameter controls how aggressively relations are merged:
        - HIGH: Merge broadly, combining many near-synonyms.
        - MEDIUM: Merge clear synonyms but keep distinct semantic categories.
        - LOW: Keep relations as distinct as possible, only merge exact or trivial variants.
        """

        def load_precomputed_ontologies_embeddings(ontology_embedding_files: list[str]):
            """
            Load precomputed ontology embeddings from ALL ontology files and combine them.
            
            Args:
                ontology_embedding_files: List of paths to ontology embedding files
                
            Returns:
                tuple: (combined_ontology_embeddings, all_ontology_labels)
            """
            all_ontology_embeddings = []
            all_ontology_labels = []
            
            for ontology_file in ontology_embedding_files:
                ontology_embeddings, ontology_labels, _ = load_ontology_embeddings(ontology_file)
                all_ontology_embeddings.append(ontology_embeddings)
                all_ontology_labels.extend(ontology_labels)
            
            # Concatenate all embeddings into a single matrix
            combined_ontology_embeddings = np.vstack(all_ontology_embeddings)
            
            return combined_ontology_embeddings, all_ontology_labels

        def getPredicateByCosineOntology(combined_ontology_embeddings, all_ontology_labels, 
                     model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
            """
            Use Ontology relations to map raw relations to preferred labels,
            and return them as a list of Predicate objects.
            
            Args:
                combined_ontology_embeddings: Combined embeddings matrix from all ontologies
                all_ontology_labels: List of all ontology labels corresponding to embeddings
                model_name: Name of the sentence transformer model to use
            """
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            from collections import defaultdict
            from .models import Predicate

            # 1. Collect raw relations (middle element of each triple)
            raw_relations = [x[1] for x in self.graph.base_graph.relations]

            # 2. Check if relation embeddings are already loaded, if not create them
            # This is done to avoid recomputing embeddings for the same relations.
            if self.relation_embeddings is None:
                model = SentenceTransformer(model_name)
                self.relation_embeddings = model.encode(raw_relations, convert_to_numpy=True, normalize_embeddings=True)

            # 3. Map each raw relation to the closest ontology label across ALL ontologies
            cluster_map = defaultdict(list)

            for rel, emb in zip(raw_relations, self.relation_embeddings):
                sims = cosine_similarity([emb], combined_ontology_embeddings)[0]
                best_idx = int(np.argmax(sims))
                best_ontology = all_ontology_labels[best_idx]
                cluster_map[best_ontology].append(rel)

            # 4. Build Predicate objects
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

            # 5. Return as Predicates model
            predicates_model = Predicates(predicates=predicates)
            return predicates_model

        def createLLMOntology(granularity: str = "MEDIUM"):
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

        if "LLM" in ontologies:
            new_predicates = createLLMOntology(granularity=granularity)
        else:
            # Check available ontology embedding files
            ontology_embedding_files = []
            for o in ontologies:
                of = os.getenv(o, None)
                if of is None:
                    raise ValueError(f"Ontology embedding file not found for mode {o}. Please set the environment variable.")
                ontology_embedding_files.append(of)

            # Load precomputed ontology embeddings
            combined_ontology_embeddings, all_ontology_labels = load_precomputed_ontologies_embeddings(ontology_embedding_files)
            
            # Get predicates using the loaded embeddings
            new_predicates = getPredicateByCosineOntology(combined_ontology_embeddings, all_ontology_labels)

        if len(ontologies) == 1:
            self.graph.ontologies[ontologies[0]] = new_predicates.predicates
        else:
            self.graph.ontologies["MIX"] = new_predicates.predicates


    def graph2Ontology(self, ontology = "SKOS"):
        """
        
        """
        
        def checkRelation(subj: str, pred: str, obj: str, relation2predicate: dict):
            """Check if the relation need to be changed to a preferred label."""
            if pred in relation2predicate:
                return (subj, relation2predicate[pred], obj)
            return (subj, pred, obj)

        
        if ontology not in self.graph.ontologies:
            return

        # Restore Base Graph
        if self.graph.base_graph is not None:
            self.graph.entities = self.graph.base_graph.entities.copy()
            self.graph.relations = self.graph.base_graph.relations.copy()
            self.graph.text = self.graph.base_graph.text

        #mergePredicates(self.graph.ontologies[ontology])
        
        # relation to predicate dictionary
        rel2pred = {}
        for predicate in self.graph.ontologies[ontology]:
            for alt_label in predicate.altLabels_en:
                rel2pred[alt_label] = predicate.prefLabel_en

        new_relations = [checkRelation(subj, pred, obj, rel2pred) for subj, pred, obj in self.graph.relations]
        self.graph.relations = set(new_relations)


    def generateKG(self, text_path: str, text_file_name: str, ontologies: list, viz_path: str = None, chunk_size: int = 0, verbose: bool = False):
        try:
            with open(f"{text_path}{text_file_name}", "r", encoding="utf-8") as file:
                text = file.read()
                text = text.strip().replace("\n", " ")
        except FileNotFoundError:
            raise ValueError(f"File not found: {text_path}")
        except Exception as e:
            raise ValueError(f"Error reading file {text_path}: {e}")
        
        try:
            self.extractConcepts(text=text, chunk_size=chunk_size)
            if verbose:
                print(f"Number of subgraphs: {len(self.graph.subgraphs)}")
                print(f"Number of Concepts: {len(self.graph.entities)}")
                print(f"Concepts list: " + ", ".join(self.graph.entities))
        except ValueError as e:
            print(f"Error processing concepts: {e}")
            return


        try:
            self.extractRelations()
            if verbose:
                print(f"Number of subgraphs: {len(self.graph.subgraphs)}")
                print(f"Number of RDF relations: {len(self.graph.relations)}")
        except ValueError as e:
            print(f"Error processing relations: {e}")
            return
        
        

        try:
            self.groupConcepts()
            if verbose:
                print(f"Number of concepts: {len(self.graph.concepts)}")
                print(f"Concepts list: " + ", ".join([c.prefLabel_he for c in self.graph.concepts]))
        except ValueError as e:
            print(f"Error processing concepts: {e}")
            return
        

        for ontology in ontologies:
            try:
                self.relations2ontology(ontologies=[ontology], granularity="MEDIUM")
                if verbose:
                    print(f"Ontology {ontology}: prepared")
            except ValueError as e:
                print(f"Error processing ontology {ontology}: {e}")
                continue

        if viz_path:
            file_name = text_file_name.split(".")[0]
            for ontology in ontologies:
                try:
                    self.graph2Ontology(ontology=ontology)
                    if verbose:
                        print(f"Ontology {ontology}: converted to graph relations")
                    viz = self.visualize(f"{viz_path}{file_name}_c{chunk_size}_ontology_{ontology}.html")
                except ValueError as e:
                    print(f"Error converting ontology {ontology} to graph: {e}")
                    continue
                
                
                
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
            