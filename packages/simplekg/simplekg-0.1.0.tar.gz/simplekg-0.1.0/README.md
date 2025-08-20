# SimpleKG 🧠

[![PyPI version](https://badge.fury.io/py/simplekg.svg)](https://badge.fury.io/py/simplekg)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SimpleKG** is a powerful Python package for generating Knowledge Graphs from Hebrew text using state-of-the-art language models like OpenAI's GPT-4o. It extracts entities, relationships, and creates visual knowledge representations with ontology support.

## 🚀 Features

- **Hebrew Text Processing**: Specialized for Hebrew text analysis and knowledge extraction
- **Entity & Relation Extraction**: Automatically identifies concepts and their relationships
- **Ontology Integration**: Supports SKOS and other ontology standards
- **Interactive Visualizations**: Generates beautiful HTML visualizations of knowledge graphs
- **Command Line Interface**: Easy-to-use CLI for batch processing
- **Python API**: Flexible programmatic interface for integration
- **Multiple Output Formats**: JSON, HTML visualizations, and more

## 📦 Installation

Install SimpleKG using pip:

```bash
pip install simplekg
```

## 🔧 Quick Start

### Command Line Interface

```bash
# Process a Hebrew text file
simplekg -i input.txt -o output/ --model "openai/gpt-4o" --api-key YOUR_API_KEY

# Use environment variable for API key
export OPENAI_API_KEY="your-api-key"
simplekg -i input.txt -o output/

# Get help
simplekg --help
```

### Python API

```python
from simplekg import KnowledgeGraphGenerator

# Initialize the generator
kggen = KnowledgeGraphGenerator(
    model="openai/gpt-4o",
    api_key="your-api-key"
)

# Process Hebrew text
text = "טקסט עברי לעיבוד..."
kggen.extractConcepts(text=text)
kggen.extractRelations()
kggen.groupConcepts()

# Apply ontology
kggen.relations2ontology(["SKOS"])

# Generate visualization
kggen.visualize("output.html")

# Save as JSON
kggen.dump_graph("graph.json")
```

## 🛠️ API Reference

### KnowledgeGraphGenerator

The main class for knowledge graph generation.

**Parameters:**
- `model` (str): Language model to use (default: "openai/gpt-4o")
- `api_key` (str): API key for the language model
- `temperature` (float): Model temperature (default: 0.0)
- `api_base` (str): Custom API base URL (optional)
- `chunk_size` (int): Text chunk size for processing (default: 0)

**Key Methods:**
- `extractConcepts(text, chunk_size=0, verbose=False)`: Extract concepts from text
- `extractRelations(verbose=False)`: Extract relationships between concepts
- `groupConcepts(verbose=False)`: Group similar concepts
- `relations2ontology(ontologies)`: Apply ontology standards
- `visualize(output_file)`: Generate HTML visualization
- `dump_graph(output_file)`: Save graph as JSON

## 📊 Supported Ontologies

- **SKOS** (Simple Knowledge Organization System)
- More ontologies coming soon!

## 🎯 Use Cases

- **Academic Research**: Process Hebrew academic papers and texts
- **Digital Humanities**: Analyze Hebrew literature and historical documents
- **Knowledge Management**: Create knowledge bases from Hebrew content
- **Content Analysis**: Understand relationships in Hebrew texts
- **Educational Tools**: Build learning resources from Hebrew materials

## 🔑 Environment Setup

Set up your API key as an environment variable:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export OPENAI_API_KEY="your-openai-api-key"
```

## 📁 Output Files

SimpleKG generates several types of output:

- **JSON Graph**: Complete graph data structure
- **HTML Visualization**: Interactive web-based visualization
- **Ontology Files**: Structured ontology representations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use SimpleKG in your research, please cite:

```bibtex
@software{simplekg,
  author = {Your Name},
  title = {SimpleKG: Knowledge Graph Generation from Hebrew Text},
  url = {https://gitlab.com/millerhadar/simplekg},
  version = {0.1.0},
  year = {2025}
}
```

## 🔗 Links

- [Documentation](https://gitlab.com/millerhadar/simplekg)
- [Issues](https://gitlab.com/millerhadar/simplekg/-/issues)
- [PyPI Package](https://pypi.org/project/simplekg/)

---

Made with ❤️ for the Hebrew NLP community

---

## 🚀 Installation

### From PyPI (recommended)
```bash
pip install simplekg
```

### From Source
```bash
git clone https://gitlab.com/millerhadar/simplekg.git
cd simplekg
pip install -e .
```

### Development Installation
```bash
git clone https://gitlab.com/millerhadar/simplekg.git
cd simplekg
pip install -e ".[dev]"
```

---

## 🎯 Features
- Extract entities and relations from raw text using an LLM.
- Normalize entities into SKOS-compatible **concepts** (canonical + alt labels).
- Normalize relations into **predicates** with multiple strategies:
  - LLM clustering with adjustable granularity (LOW, MEDIUM, HIGH).
  - Embedding-based clustering + LLM naming.
  - Alignment to known ontologies (SKOS, Dublin Core, CIDOC CRM).
- Support for **multiple ontologies** in parallel.
- Graph export and HTML visualization.

---

## 📖 Workflow

### 1. Initialize
```python
import simplekg as kg
import os

kggen = kg.KnowledgeGraphGenerator(
    model="openai/gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 2. Extract Entities
```python
kggen.extractConcepts(text=text, chunk_size=chunk_size, verbose=True)
```

- `chunk_size=0`: analyze the text as a whole (may dilute context).
- `chunk_size>0`: split text into smaller parts, generate subgraphs, then merge.

### 3. Extract Relations
```python
kggen.extractRelations(verbose = True)
```

### 4. Normalize Entities
Groups entities into **concepts** (canonical + alternate names).

```python
kggen.groupConcepts(chunk_size= 160, threshold= 160, max_iterations= 2, verbose=True)
```

### 5. Normalize Relations
- **LLM clustering**: more detailed, but text-specific.
- **Ontology alignment**: more general, enables cross-text comparison.
- **Multiple ontologies**: select the best relation across several vocabularies.
- **LLM validation** *(planned)*: confirm embedding-based alignment.

```python
kggen.relations2ontology(["SKOS"])
kggen.relations2ontology(["CIDOC_CRM", "DUBLIN_CORE"])
```

### 6. Visualization
Convert the KG into a chosen ontology and render HTML.

```python
ontology = "SKOS"  # or "MIX" for multiple ontologies
kggen.graph2Ontology(ontology)
viz = kggen.visualize(f"../../vis/{file_name}_c{chunk_size}_ontology_{ontology}.html")
```

---

## � Command Line Interface

SimpleKG also provides a command-line interface:

```bash
# Basic usage
simplekg --input-file text.txt --output-dir ./output

# With specific model and ontologies
simplekg --input-file text.txt --model "openai/gpt-4o" --ontologies SKOS CIDOC_CRM --verbose

# Get help
simplekg --help
```

---

## �📚 Supported Ontologies

### SKOS
- `skos:broader` / `skos:narrower`
- `skos:related`
- Mapping terms: `exactMatch`, `closeMatch`, etc.

### Dublin Core
- `dcterms:isPartOf` / `dcterms:hasPart`
- `dcterms:references` / `dcterms:isReferencedBy`
- Versioning, formats, replacements, requirements.

### CIDOC CRM (selected)
- `P5_consists_of` (part-of)
- `P7_took_place_at` (event location)
- `P13_destroyed` (destruction)
- `P53_has_former_or_current_location`
- `P94_has_created` (production/creation)

---

## ⚖️ Design Trade-offs
- **Whole text vs. chunks**: global context vs. fine-grained extraction.
- **LLM relation clustering**: richer inside one graph, less comparable across graphs.
- **Ontology alignment**: more comparable across graphs, but risk of oversimplification.

---

## 📌 References
- [SKOS Specification](https://www.w3.org/TR/skos-reference/)
- [Dublin Core Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
- [CIDOC CRM Official Site](https://cidoc-crm.org/)

---

## 🔮 Roadmap
- LLM-based validation for ontology alignment.
- Integration with additional ontologies.
- More advanced visualization options.

---
