import sys
from rag import rag_engine

def main():
    print("=" * 65)
    print("  CareGuard - Healthcare Insurance Policy AI Engine (CLI Test)")
    print("=" * 65)
    
    questions = [
        "What documents are required for reimbursement claims?",
        "What is the waiting period for pre-existing diseases and cataract surgery?",
        "Are cosmetic surgeries covered under policy exclusions?"
    ]
    
    # Allow user to pass a question from command line or select default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("\nSelect a sample query or press ENTER for default:")
        for idx, q in enumerate(questions, 1):
            print(f"  [{idx}] {q}")
        choice = input("\nEnter choice (1-3) or type custom question: ").strip()
        
        if choice in ["1", "2", "3"]:
            query = questions[int(choice) - 1]
        elif choice:
            query = choice
        else:
            query = questions[0]

    print(f"\n[Query] {query}\n" + "-" * 65)
    print("Searching ChromaDB vector store and retrieving policy evidence...")
    
    result = rag_engine.query(query)
    
    print("\n" + "=" * 25 + " GROUNDED ANSWER " + "=" * 25)
    print(result["answer"])
    
    print("\n" + "=" * 25 + " SOURCE CITATIONS " + "=" * 24)
    for c in result.get("citations", []):
        print(f"- Source: {c['source']} (Page {c['page']})")
        print(f"  Excerpt: \"{c['content_preview']}\"")
        
    print("\n" + "=" * 25 + " HUMAN REVIEW FLAG " + "=" * 23)
    if result.get("requires_human_review"):
        print("FLAGGED: Requires human claims analyst verification.")
    else:
        print("CLEAR: Directly covered by standard policy provisions.")
    print("=" * 65)

if __name__ == "__main__":
    main()
