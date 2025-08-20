import nltk

def chunk_text(text: str, max_chunk_size=500) -> list[str]:

    """
    Chunk text by sentence, respecting a maximum chunk size.
    Falls back to word-based chunking if a single sentence is too large.
    
    :param text: The text to chunk.
    :param max_chunk_size: The maximum length (in characters) of any chunk.
    :return: A list of text chunks.
    """
    # Step 1: Split text into sentences
    sentences = nltk.sent_tokenize(text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence stays within the limit, append it.
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            # If the current chunk has some content, push it and start a new one.
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # Check if the sentence itself is larger than the limit.
            # If yes, chunk it by words (fallback).
            if len(sentence) > max_chunk_size:
                words = sentence.split()
                temp_chunk = ""

                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= max_chunk_size:
                        temp_chunk += word + " "
                    else:
                        chunks.append(temp_chunk.strip())
                        temp_chunk = word + " "

                # Add the leftover if any
                if temp_chunk:
                    chunks.append(temp_chunk.strip())
            else:
                # If the sentence is smaller than max_chunk_size, just start a new chunk with it.
                current_chunk = sentence + " "

    # If there's a leftover chunk that didn't get pushed, add it
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def compute_ontology_embeddings(ontology_relations, 
                                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                                filename=None):
    """
    Compute Ontology embeddings once and save them to file.
    example 
            skos_relations = {
            "skos:broader": "Indicates a more general concept",
            "skos:narrower": "Indicates a more specific concept",
            "skos:related": "Indicates an associative relationship",
            "skos:exactMatch": "Concepts are exactly equivalent",
            "skos:closeMatch": "Concepts are sufficiently similar but not identical",
            "skos:broadMatch": "Broader concept in another scheme",
            "skos:narrowMatch": "Narrower concept in another scheme",
            "skos:relatedMatch": "Associative relation in another scheme"
        }
           compute_ontology_embeddings(skos_relations, filename="full/path/skos_embeddings.npz")
    """
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    skos_labels = list(ontology_relations.keys())
    skos_texts = [f"{k}: {v}" for k, v in ontology_relations.items()]

    embeddings = model.encode(skos_texts, convert_to_numpy=True, normalize_embeddings=True)

    if filename:
        np.savez(filename, embeddings=embeddings, labels=skos_labels, texts=skos_texts)
    else:
        return embeddings

def load_ontology_embeddings(filename):
    """
    Load ontology embeddings, labels, and texts from file.
    """
    import numpy as np
    data = np.load(filename, allow_pickle=True)
    embeddings = data["embeddings"]
    labels = data["labels"].tolist()
    texts = data["texts"].tolist()
    return embeddings, labels, texts

def is_english(text):
    """
    Check if the text contains English characters or numeric characters or non-alphanumeric characters.
    
    """
    import re
    # Check if the text contains any English letters (a-z, A-Z), digits (0-9), or non-alphanumeric characters
    return bool(re.search(r'[a-zA-Z0-9\W]', text))