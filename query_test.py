from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Initialize the same embedding model used during ingestion
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

def search_knowledge_base(user_query: str):
    # Load FAISS index
    db = FAISS.load_local(
        "faiss_index",
        embeddings_model,
        allow_dangerous_deserialization=True
    )

    # Retrieve top 5 matches with similarity scores
    docs_with_scores = db.similarity_search_with_score(
        user_query,
        k=5
    )

    # #     docs = db.max_marginal_relevance_search(
# #     user_query,
# #     k=5,
# #     fetch_k=20
# # )

    print(f"\n🔍 Query: {user_query}")
    print("=" * 80)

    for i, (doc, score) in enumerate(docs_with_scores, start=1):
        print(f"\nMatch #{i}")
        print(f"📄 Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"📊 Similarity Score: {score}")
        print("-" * 80)
        print(doc.page_content)  # Show first 500 chars
        print("-" * 80)

if __name__ == "__main__":
    search_knowledge_base(
        "What is Linear Regression?"
    )