import os
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
 
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.readers.joiner import JoinDocuments
from haystack.components.embedders import SentenceTransformersTextEmbedder
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
EMBED_MODEL = os.getenv("EMBED_MODEL")



document_store = QdrantDocumentStore(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    collection_name=os.getenv("QDRANT_COLLECTION"),
    recreate_index=False,  # Set to True only when re-embedding
    embedding_dim=384,     # Depends on the model
)
retriever = QdrantEmbeddingRetriever(
    document_store=document_store,
    embedder=Sentence_transformersTextEmbedder(model=EMBED_MODEL),
    top_k=3
)

builder = AnswerBuilder()
joiner = JoinDocuments()

class RAGPipeline:
    def run(self, query: str):
        results = retriever.run(query=query)
        top_docs = results["documents"]
        if not top_docs:
            return "No relevant content found."
        joined = joiner.run(documents=top_docs)
        final = builder.run(documents=joined["documents"])
        return final["answers"][0].data if final["answers"] else "No answer found."

rag_pipeline = RAGPipeline()
