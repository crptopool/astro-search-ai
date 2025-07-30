# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from haystack import Pipeline

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.utils import Secret
import os
from dotenv import load_dotenv

load_dotenv()
# === ENVIRONMENT VARIABLES ===
 
QDRANT_HOST = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
EMBED_MODEL =  os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME =  os.getenv("QDRANT_COLLECTION")
# === FastAPI setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# === Qdrant Document Store ===
document_store = QdrantDocumentStore(
    url=QDRANT_HOST,
    api_key=Secret.from_token(QDRANT_API_KEY),
    index=COLLECTION_NAME,
    embedding_dim=384,
    recreate_index=False
)

# Debug: Test Qdrant connection and collection info
print(f"🔍 Testing Qdrant connection to collection '{COLLECTION_NAME}'...")
try:
    from qdrant_client import QdrantClient
    
    client = QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )
    
    collections = client.get_collections()
    print(f"Available collections: {[c.name for c in collections.collections]}")
    
    if COLLECTION_NAME in [c.name for c in collections.collections]:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' found!")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print(f"   Distance metric: {collection_info.config.params.vectors.distance}")
        
        count_result = client.count(collection_name=COLLECTION_NAME)
        print(f"   Document count: {count_result.count}")
        
        test_vector = [0.1] * 384
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=test_vector,
            limit=1
        )
        print(f"   Test search returned {len(search_result)} results")
        
    else:
        print(f"❌ Collection '{COLLECTION_NAME}' not found!")
        
except Exception as e:
    print(f"❌ Error connecting to Qdrant: {e}")

print("=" * 50)

# === RAG Pipeline ===
# Create the embedder
embedder = SentenceTransformersTextEmbedder(model=EMBED_MODEL)

# Warm up the embedder to load the model
print("🔄 Loading embedding model...")
embedder.warm_up()
print("✅ Embedding model loaded successfully!")

# === Custom Qdrant Retriever ===
from haystack import component
from haystack.dataclasses import Document
from typing import List
from qdrant_client import QdrantClient

@component
class CustomQdrantRetriever:
    """
    Custom retriever that uses direct Qdrant client instead of QdrantEmbeddingRetriever
    """
    
    def __init__(self, url: str, api_key: str, collection_name: str, top_k: int = 5):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.top_k = top_k
        print(f"🔧 CustomQdrantRetriever initialized for collection '{collection_name}' with top_k={top_k}")
    
    @component.output_types(documents=List[Document])
    def run(self, query_embedding: List[float]) -> dict:
        """Retrieve documents using direct Qdrant search"""
        print(f"🔍 CustomQdrantRetriever.run() called with embedding length: {len(query_embedding)}")
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=self.top_k,
                with_payload=True
            )
            
            print(f"✅ Custom retriever found {len(search_result)} results")
            
            documents = []
            for i, result in enumerate(search_result):
                # Create Haystack Document with content from payload['text']
                content = result.payload.get('text', '')
                doc = Document(
                    content=content,
                    meta={k: v for k, v in result.payload.items() if k != 'text'},
                    score=result.score
                )
                documents.append(doc)
                print(f"  Created doc {i+1}: Score={result.score:.4f}, Content length={len(content)}")
            
            print(f"✅ CustomQdrantRetriever returning {len(documents)} documents")
            return {"documents": documents}
            
        except Exception as e:
            print(f"❌ CustomQdrantRetriever failed: {e}")
            import traceback
            traceback.print_exc()
            return {"documents": []}

# Create the custom retriever instead of QdrantEmbeddingRetriever
custom_retriever = CustomQdrantRetriever(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
    collection_name=COLLECTION_NAME,
    top_k=5
)

# Create a prompt template for RAG
prompt_template = """
Given the following context verses, answer the question as accurately as possible.

Context:
{% for document in documents %}
Verse {{ document.meta['verse_number'] }} ({{ document.meta['heading'] }}): {{ document.content }}
{% endfor %}

Question: {{ query }}

Answer:
"""

# Create the prompt builder with required variables specified
prompt_builder = PromptBuilder(
    template=prompt_template,
    required_variables=["documents", "query"]
)

# Create the generator
generator = OpenAIGenerator(
    api_key=Secret.from_token(OPENAI_API_KEY),
    model="gpt-3.5-turbo"
)

# Build the pipeline with the custom retriever (no document fixer needed)
rag_pipeline = Pipeline()
rag_pipeline.add_component("embedder", embedder)
rag_pipeline.add_component("custom_retriever", custom_retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("generator", generator)

# Connect the components directly (no document fixer needed)
rag_pipeline.connect("embedder.embedding", "custom_retriever.query_embedding")
rag_pipeline.connect("custom_retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "generator.prompt")

# Debug: Print pipeline configuration
print("🔍 Pipeline configuration:")
print(f"   Components: {list(rag_pipeline.graph.nodes.keys())}")
print(f"   Connections: {list(rag_pipeline.graph.edges())}")

# Test the pipeline connections
print("🔍 Testing pipeline components individually...")
try:
    # Test embedding
    test_embedding_result = embedder.run(text="test")
    print(f"✅ Embedder test: {len(test_embedding_result['embedding'])} dims")
    
    # Test custom retriever directly
    test_docs = custom_retriever.run(query_embedding=test_embedding_result['embedding'])
    print(f"✅ Custom retriever test: {len(test_docs['documents'])} docs")
    
    # Test prompt builder directly
    test_prompt = prompt_builder.run(documents=test_docs['documents'], query="test")
    print(f"✅ Prompt builder test: prompt length {len(test_prompt['prompt'])}")
    
except Exception as e:
    print(f"❌ Component test failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

# === API Route ===
@app.post("/ask")
async def ask_question(payload: QueryRequest):
    query = payload.query
    try:
        # Debug: Test the embedder directly
        print(f"\n🔍 Debugging query: '{query}'")
        
        # Test embedding generation
        embedding_result = embedder.run(text=query)
        query_embedding = embedding_result["embedding"]
        print(f"Generated embedding vector length: {len(query_embedding)}")
        print(f"First 5 embedding values: {query_embedding[:5]}")
        
        # Test direct Qdrant search with the generated embedding
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)
            
            direct_search = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=5,
                with_payload=True
            )
            print(f"Direct Qdrant search returned {len(direct_search)} results")
            for i, result in enumerate(direct_search):
                print(f"  Result {i+1}: Score={result.score:.4f}, Text preview: {str(result.payload.get('text', ''))[:100]}...")
                
        except Exception as e:
            print(f"❌ Direct Qdrant search failed: {e}")
        
        # Run the pipeline with correct input format for Haystack 2
        result = rag_pipeline.run(
            {
                "embedder": {"text": query},
                "prompt_builder": {"query": query}
            },
            include_outputs_from={"custom_retriever", "prompt_builder", "generator"}
        )

        # Debug: Check what documents were retrieved at each stage
        custom_retriever_docs = result.get("custom_retriever", {}).get("documents", [])
        prompt_builder_docs = result.get("prompt_builder", {}).get("documents", [])
        
        print(f"Custom retriever stage: {len(custom_retriever_docs)} documents")
        print(f"Prompt builder stage: {len(prompt_builder_docs)} documents")
        
        # Use the documents from custom_retriever stage, or fall back to checking other locations
        retrieved_docs = custom_retriever_docs
        
        # If still no documents, let's check if there's an issue with the pipeline execution
        if not retrieved_docs and prompt_builder_docs:
            retrieved_docs = prompt_builder_docs
            print("Using documents from prompt_builder s    tage instead")

        print(f"Pipeline final documents: {len(retrieved_docs)} from Qdrant collection '{COLLECTION_NAME}':")
        
        for i, doc in enumerate(retrieved_docs):
            print(f"  Doc {i+1}: Score={doc.score:.4f}")
            print(f"    Verse #: {doc.meta.get('verse_number', '')}")
            print(f"    Surah: {doc.meta.get('heading', '')}")
            print(f"    Section Index: {doc.meta.get('section_index', '')}")
            print(f"    Tokens: {doc.meta.get('token_count', '')}")
            print(f"    Topics: {doc.meta.get('topics', '')}")
            print(f"    Source File: {doc.meta.get('source', '')}")
            print(f"    Content preview: {doc.content[:200]}...")
        
        # Check if any documents were retrieved
        if not retrieved_docs:
            print("⚠️  WARNING: No documents retrieved from Qdrant! Response will be based on OpenAI's general knowledge only.")
            return {"answer": "No relevant documents found in the knowledge base.", "source": "no_documents"}

        # Extract the generated response
        replies = result.get("generator", {}).get("replies", [])
        if not replies:
            return {"answer": "Sorry, I couldn't generate a response.", "source": "generation_failed"}
        
        print(f"Generated response length: {len(replies[0])} characters")
        print("=== END DEBUG ===\n")
        
        return {
            "answer": replies[0],
            "source": "qdrant_collection",
            "documents_found": len(retrieved_docs),
            "collection_name": COLLECTION_NAME,
            "verses": [
                {
                    "verse_number": doc.meta.get("verse_number", ""),
                    "surah": doc.meta.get("heading", ""),
                    "section_index": doc.meta.get("section_index", ""),
                    "tokens": doc.meta.get("token_count", ""),
                    "topics": doc.meta.get("topics", ""),
                    "source_file": doc.meta.get("source", ""),
                    "content": doc.content
                }
                for doc in retrieved_docs
            ]
        }
    except Exception as e:
        print(f"Error during pipeline execution: {str(e)}")
        return {"answer": f"Sorry, an error occurred: {str(e)}", "source": "error"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
