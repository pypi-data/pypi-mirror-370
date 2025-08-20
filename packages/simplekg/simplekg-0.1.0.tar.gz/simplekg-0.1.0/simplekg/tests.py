import os
from kg import KnowledgeGraphGenerator


def main():
    # Example usage
    kg = KnowledgeGraphGenerator(model="openai/gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

if __name__ == "__main__":
    main()