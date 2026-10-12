import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from config import settings

def get_embedding_model():
    """Returns the configured embedding model."""
    if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        # Default local open-source embedding model
        return HuggingFaceEmbeddings(
            model_name=settings.HUGGINGFACE_EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

def load_documents(directory: str):
    """Loads all PDF and TXT documents from the target directory."""
    documents = []
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return documents

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = filename
            documents.extend(docs)
        elif filename.endswith(".txt") or filename.endswith(".md"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = filename
                doc.metadata["page"] = 1
            documents.extend(docs)
    return documents

def create_sample_policies_if_empty(directory: str):
    """Generates synthetic healthcare insurance policy data for instant testing."""
    os.makedirs(directory, exist_ok=True)
    sample_file = os.path.join(directory, "health_policy_comprehensive_2025.txt")
    if not os.path.exists(sample_file):
        content = """# COMPREHENSIVE HEALTHCARE INSURANCE POLICY MANUAL (v2025.1)
SECTION 1: INPATIENT HOSPITALIZATION COVERAGE
1.1 Room Rent & ICU Limits:
- Normal Room Rent is capped at 1% of the Sum Insured per day.
- Intensive Care Unit (ICU) charges are capped at 2% of the Sum Insured per day.
- If the insured selects a room category higher than eligibility, proportional deduction applies to associated medical charges.

SECTION 2: PRE-EXISTING DISEASES (PED) AND WAITING PERIODS
2.1 Initial Waiting Period:
- A 30-day waiting period applies from policy inception for all claims, except accidental injuries.
2.2 Pre-Existing Conditions:
- Pre-existing diseases (PED) are covered only after a continuous waiting period of 36 months (3 years) of active coverage.
2.3 Specific Illness Waiting Period:
- Cataract, Hernia, Joint Replacement, and Hysterectomy carry a mandatory 24-month waiting period.

SECTION 3: CLAIMS PROCEDURES & DOCUMENTATION CHECKLIST
3.1 Cashless Claims:
- Pre-authorization request must be submitted 48 hours prior to planned admission, or within 24 hours in case of emergency admission.
3.2 Reimbursement Claims Checklist:
To file a reimbursement claim, the following mandatory documents must be submitted within 30 days of hospital discharge:
1. Duly filled and signed Claim Form Part A (Insured) and Part B (Hospital).
2. Original Discharge Summary mentioning clinical diagnosis, treatment given, and date of admission/discharge.
3. Original Itemized Final Hospital Bill with detailed breakup and payment receipts.
4. All diagnostic test reports (ECG, Blood reports, Radiology) supporting the treatment.
5. Original Pharmacy bills accompanied by treating physician's prescription.
6. Copy of Insured KYC (Aadhaar / Passport / Voter ID) and cancelled cheque with bank account details for NEFT reimbursement.

SECTION 4: PERMANENT EXCLUSIONS
- Cosmetic or aesthetic treatments, plastic surgery unless reconstructive surgery following accidental trauma.
- Routine outpatient consultations, external vitamins/tonics unless part of prescribed inpatient medication.
- Self-inflicted injuries, treatment arising from substance/alcohol abuse.
- Investigational, experimental, or unproven therapies.
"""
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[Ingestion] Generated initial sample policy at {sample_file}")

def ingest_documents():
    """Main ingestion pipeline: chunks documents and stores them in ChromaDB."""
    create_sample_policies_if_empty(settings.DATA_DIR)
    print(f"[Ingestion] Loading documents from {settings.DATA_DIR}...")
    docs = load_documents(settings.DATA_DIR)

    if not docs:
        print("[Ingestion] No documents found to ingest.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\nSECTION", "\n## ", "\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"[Ingestion] Generated {len(chunks)} text chunks.")

    embeddings = get_embedding_model()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        collection_name="healthcare_policies"
    )
    print(f"[Ingestion] Vector database successfully created at {settings.CHROMA_PERSIST_DIR}")
    return vector_store

if __name__ == "__main__":
    ingest_documents()
