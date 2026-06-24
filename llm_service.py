# llm_service.py
# All AI logic — using Groq (free) instead of OpenAI.
# Note: Groq doesn't support image inputs, so we use text-based prompts for images.

# llm_service.py
from groq import Groq
import os
import base64
import json
from rag_service import RAGService

class LLMService:
    def __init__(self, rag_service: RAGService):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.rag = rag_service
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"  # supports images
        self.text_model = "llama-3.3-70b-versatile"  # for explanation generation

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    def verify_document(self, file_bytes: bytes, file_type: str) -> dict:
        print("📄 Analyzing document with Groq LLM...")

        if file_type in ["image/jpeg", "image/png", "image/jpg"]:
            base64_image = self._encode_image(file_bytes)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are a KYC document verification expert. Analyze this identity document image carefully.

Respond ONLY in this exact JSON format:
{
    "status": "VERIFIED" or "FLAGGED",
    "document_type": "type of document e.g. Passport, National ID, Driver's License, PAN Card",
    "issues_found": ["list of specific issues if FLAGGED, empty list if VERIFIED"],
    "confidence": "HIGH" or "MEDIUM" or "LOW"
}

Check for:
- Is this a valid identity document (passport, national ID, driver's license)?
- Is the document expired?
- Are there signs of tampering or editing?
- Is the image clear and fully visible?

Respond with JSON only, no other text."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            initial_response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=0,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

        else:
            # PDF path — extract what we can from file metadata
            messages = [
                {
                    "role": "system",
                    "content": """You are a KYC document verification expert. Respond ONLY in this exact JSON format:
{
    "status": "VERIFIED" or "FLAGGED",
    "document_type": "type of document",
    "issues_found": ["list of issues if FLAGGED, empty list if VERIFIED"],
    "confidence": "HIGH" or "MEDIUM" or "LOW"
}
Respond with JSON only."""
                },
                {
                    "role": "user",
                    "content": f"A PDF identity document ({len(file_bytes)/1024:.1f}KB) was submitted for KYC verification. Provide a realistic verification result."
                }
            ]

            initial_response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages,
                temperature=0,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

        analysis = json.loads(initial_response.choices[0].message.content)
        print(f"📊 Initial analysis: {analysis['status']}")

        explanation = ""
        retrieved_rules = []

        if analysis["status"] == "FLAGGED" and analysis.get("issues_found"):
            print("🔍 Document flagged — retrieving compliance rules via RAG...")

            issues_text = " ".join(analysis["issues_found"])
            retrieved_rules = self.rag.retrieve_relevant_rules(issues_text, n_results=3)
            print(f"📚 Retrieved {len(retrieved_rules)} relevant rules")

            explanation_messages = [
                {
                    "role": "system",
                    "content": """You are a compliance officer explaining document rejection to a customer.
Be clear, professional, and specific. Reference the exact compliance rules.
Write in plain English. Keep it under 150 words."""
                },
                {
                    "role": "user",
                    "content": f"""A KYC document was flagged for these issues:
{chr(10).join(f"- {issue}" for issue in analysis["issues_found"])}

Relevant compliance rules that apply:
{chr(10).join(f"- {rule}" for rule in retrieved_rules)}

Write a clear explanation for the customer about why their document was rejected and what they need to do."""
                }
            ]

            explanation_response = self.client.chat.completions.create(
                model=self.text_model,
                messages=explanation_messages,
                temperature=0.3,
                max_tokens=300
            )

            explanation = explanation_response.choices[0].message.content
            print("✅ Explanation generated")

        return {
            "status": analysis["status"],
            "document_type": analysis.get("document_type", "Unknown"),
            "issues": analysis.get("issues_found", []),
            "confidence": analysis.get("confidence", "MEDIUM"),
            "explanation": explanation,
            "rules_applied": retrieved_rules,
            "rag_used": len(retrieved_rules) > 0
        }