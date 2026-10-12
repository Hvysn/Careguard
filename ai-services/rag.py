import os
from typing import Dict, Any, List

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from ingest import get_embedding_model
from config import settings

HEALTHCARE_RAG_PROMPT = """You are a specialized AI Assistant for Healthcare Insurance Policy & Claims Adjudication.
Your role is to assist claims analysts by answering questions strictly based on the retrieved insurance policy excerpts provided below.

Strict Compliance Rules:
1. ONLY use information explicitly stated in the context. Never fabricate or assume coverage terms.
2. If the policy context does not state the rule or is insufficient, explicitly state: "Information not found in available policy documents. Human claims analyst review required."
3. Always cite the exact source document and section/page from which you derived each point.
4. Flag any ambiguities, conflicting clauses, or conditions that mandate human specialist review.

Context:
{context}

Question:
{question}

Provide your response in this structured format:
### Summary Answer
[Clear, direct explanation of the policy or procedure]

### Required Documents / Applicable Rules
[List items or conditions explicitly mentioned]

### Source Citations
- Document: [Name] | Page/Section: [Number or Name]

### Human Review Advisory
[Specify if this query requires manual review or if the documentation has ambiguity/exclusions]
"""

class HealthcareRAGEngine:
    def __init__(self):
        self.embeddings = get_embedding_model()
        self.vector_store = Chroma(
            collection_name="healthcare_policies",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.TOP_K}
        )

        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.llm = None

    def retrieve_context(self, query: str):
        """Retrieves top-k relevant document chunks with metadata citations."""
        docs = self.retriever.invoke(query)
        formatted_context = ""
        citations = []

        for idx, doc in enumerate(docs):
            src = doc.metadata.get("source_file", "Unknown Document")
            page = doc.metadata.get("page", 1)
            citations.append({
                "source": src,
                "page": page,
                "content_preview": doc.page_content[:180] + "..."
            })
            formatted_context += f"\n--- Excerpt {idx+1} [Source: {src}, Page {page}] ---\n{doc.page_content}\n"

        return formatted_context, citations

    def query(self, question: str) -> Dict[str, Any]:
        """Runs the complete RAG pipeline or returns retrieved context fallback."""
        context, citations = self.retrieve_context(question)

        if not self.llm:
            # Fallback when no OpenAI API key is configured
            answer = (
                "### Retrieved Grounded Evidence\n"
                "The following excerpts were matched from the insurance policy database:\n\n"
                f"{context}\n\n"
                "*(Note: Set OPENAI_API_KEY in ai-service to enable LLM-generated synthesis.)*"
            )
            return {
                "answer": answer,
                "citations": citations,
                "requires_human_review": True
            }

        prompt = ChatPromptTemplate.from_template(HEALTHCARE_RAG_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        response_text = chain.invoke({"context": context, "question": question})

        requires_review = "human" in response_text.lower() or "review" in response_text.lower()

        return {
            "answer": response_text,
            "citations": citations,
            "requires_human_review": requires_review
        }

rag_engine = HealthcareRAGEngine()
