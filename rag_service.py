# rag_service.py
# RAG system using local embeddings (sentence-transformers) — completely free!
# No API key needed for embeddings — runs on your own machine.

import chromadb
from chromadb.utils import embedding_functions
from compliance_rules import COMPLIANCE_RULES

class RAGService:
    def __init__(self):
        # In-memory ChromaDB
        self.client = chromadb.Client()

        # Free local embedding model — runs on your CPU, no API needed
        # Downloads the model once (~90MB) on first run
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Create collection with local embeddings
        self.collection = self.client.create_collection(
            name="kyc_compliance_rules",
            embedding_function=self.embedding_fn
        )

        self._index_rules()
        print("✅ RAG Service initialized — compliance rules indexed")

    def _index_rules(self):
        """
        Convert all compliance rules to embeddings and store in ChromaDB.
        Runs once at startup using your local CPU — no API cost.
        """
        documents = [rule["rule"] for rule in COMPLIANCE_RULES]
        ids = [rule["id"] for rule in COMPLIANCE_RULES]
        metadatas = [{"category": rule["category"]} for rule in COMPLIANCE_RULES]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def retrieve_relevant_rules(self, issue_description: str, n_results: int = 3) -> list:
        """
        Find the most relevant compliance rules for a given issue.
        Uses local embeddings — fast and free.
        """
        results = self.collection.query(
            query_texts=[issue_description],
            n_results=n_results
        )
        return results["documents"][0]