# rag_service.py
import chromadb
from compliance_rules import COMPLIANCE_RULES
import os

class RAGService:
    def __init__(self):
        self.client = chromadb.Client()

        # Use ChromaDB's built-in lightweight embeddings
        # No sentence-transformers needed — saves 400MB of memory!
        self.collection = self.client.create_collection(
            name="kyc_compliance_rules"
        )

        self._index_rules()
        print("✅ RAG Service initialized — compliance rules indexed")

    def _index_rules(self):
        documents = [rule["rule"] for rule in COMPLIANCE_RULES]
        ids = [rule["id"] for rule in COMPLIANCE_RULES]
        metadatas = [{"category": rule["category"]} for rule in COMPLIANCE_RULES]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def retrieve_relevant_rules(self, issue_description: str, n_results: int = 3) -> list:
        results = self.collection.query(
            query_texts=[issue_description],
            n_results=n_results
        )
        return results["documents"][0]