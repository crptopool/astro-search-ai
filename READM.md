# Quran RAG Backend – Haystack + Qdrant

This backend powers the multilingual QA chatbot for Quran content using MDX files.
It uses Haystack + sentence-transformers + Qdrant for Retrieval-Augmented Generation (RAG).

---

## 🏗️ Architecture Decision: Why Haystack + Custom Qdrant Retriever?

### **The Question: Why Use Haystack When We Can Search Directly in Qdrant?**

This is a critical architectural consideration. Our implementation uses a **hybrid approach** that combines the best of both worlds.

#### **🔍 Direct Qdrant vs. Haystack Comparison:**

| Approach | Latency | Code Complexity | Maintainability | Extensibility |
|----------|---------|-----------------|-----------------|---------------|
| Direct Qdrant | Lower | Lower | Medium | Lower |
| Haystack Pipeline | Slightly Higher | Medium | Higher | Much Higher |
| **Our Hybrid** | **Medium** | **Medium** | **High** | **High** |

#### **✅ Why We Chose Hybrid Architecture:**

**1. Pipeline Orchestration Benefits:**
```python
# Without Haystack (manual chaining):
embedding = embedder.encode(query)
results = qdrant_client.search(...)
prompt = f"Context: {results}\nQuestion: {query}"
response = openai.chat.completions.create(...)

# With Haystack (automatic flow):
result = rag_pipeline.run({
    "embedder": {"text": query},
    "prompt_builder": {"query": query}
})
```

**2. Production-Ready Features:**
- **Error Handling**: Graceful component failure management
- **State Management**: Automatic data flow between components
- **Extensibility**: Easy to add re-rankers, evaluators, multi-retrievers
- **Monitoring**: Built-in metrics and debugging capabilities

**3. Custom Control Where Needed:**
- **CustomQdrantRetriever**: Direct Qdrant client for field mapping control
- **Debugging**: Direct search validation alongside pipeline execution
- **Performance**: Bypass Haystack limitations while keeping orchestration benefits

#### **🎯 When to Use Each Approach:**

**✅ Use Direct Qdrant When:**
- Simple vector search only
- Performance-critical applications (minimal latency)
- Custom retrieval logic that doesn't fit standard patterns
- Debugging and validation (as we do)

**✅ Use Haystack When:**
- Complex RAG patterns (multi-step retrieval, re-ranking)
- Production systems requiring monitoring and evaluation
- Team development with standardized patterns
- A/B testing different components
- Planning to scale with additional RAG features

**✅ Use Hybrid (Our Approach) When:**
- Need custom control over specific components
- Want production orchestration benefits
- Require debugging capabilities
- Planning future enhancements

#### **🚀 Future Enhancement Roadmap:**
Our hybrid architecture enables easy addition of:
- **Document Re-ranker**: Cross-encoder for better relevance
- **Multi-language Support**: Different embedders for Arabic/English
- **Citation Tracking**: Automatic verse reference extraction
- **Evaluation Pipeline**: Answer quality testing
- **Multiple Retrievers**: Combine different search strategies
- **Caching Layer**: Performance optimization

---

## 🔧 Files Overview

### 1. `data_loader.py`
- **Purpose**: Extracts content from MDX files, chunks it, generates embeddings, and uploads to Qdrant vector DB.
- **Steps**:
  - Loads `.mdx` files from `astro-quran/src/content/docs/surahs`.
  - Extracts frontmatter and content using `python-frontmatter`.
  - Uses `sentence-transformers` (multilingual) for embeddings.
  - Stores data in `quran-mdx` collection on [Qdrant Cloud](https://cloud.qdrant.io).

---

### 2. `main.py` (FastAPI RAG Backend)
- **Purpose**: Exposes a FastAPI `/ask` endpoint for question answering with custom retrieval pipeline.
- **Architecture**: **Hybrid Haystack 2 + Direct Qdrant** for optimal control and orchestration.

#### **Key Components:**

**🔍 CustomQdrantRetriever (Hybrid Solution)**
- **Problem Solved**: Standard `QdrantEmbeddingRetriever` had field mapping issues (documents retrieved with `None` content)
- **Solution**: Custom Haystack component using direct `qdrant-client` calls
- **Benefits**: 
  - Direct control over Qdrant queries and result processing
  - Proper field mapping from Qdrant `text` field to Haystack `content` field
  - Maintains Haystack component interface for pipeline integration
  - Detailed logging and error handling

**🔄 Pipeline Workflow (Hybrid Architecture):**
1. **SentenceTransformersTextEmbedder**: Converts query to 384-dim multilingual embeddings
2. **CustomQdrantRetriever**: Direct Qdrant search + Haystack Document formatting
3. **PromptBuilder**: Haystack component for context-aware prompt creation
4. **OpenAIGenerator**: Haystack component for response generation

**🐛 Debugging & Validation:**
- **Dual Search**: Direct Qdrant search alongside pipeline execution for validation
- **Component Testing**: Individual component testing during startup
- **Pipeline Inspection**: `include_outputs_from` for intermediate result analysis
- **Performance Monitoring**: Response time and document retrieval metrics

#### **Technical Implementation Details:**
```python
@component
class CustomQdrantRetriever:
    """
    Hybrid component: Direct Qdrant client + Haystack interface
    - Uses qdrant-client for reliable search
    - Converts payload['text'] to Document.content
    - Preserves metadata (source, chunk_id, original_id)
    - Maintains Haystack component compatibility
    """
```

**🔧 Configuration & Performance:**
- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Collection**: `quran-mdx` (6,236 documents)
- **Retrieval**: Top-5 most relevant verses
- **Response Generation**: OpenAI GPT-3.5-turbo with Quran context
- **Performance**: ~2-3 seconds per query (embedding + retrieval + generation)

---

## 🌐 Qdrant Cloud Setup

- **Cluster ID**: `6eead27a-8dd0-4a6f-8061-cada1c105bde`
- **Endpoint**: `https://6eead27a-8dd0-4a6f-8061-cada1c105bde.europe-west3-0.gcp.cloud.qdrant.io`
- **Collection**: `quran-mdx`
- **Document Structure**:
  ```json
  {
    "text": "Verse content in markdown format",
    "source": "surah-097.mdx", 
    "chunk_id": 1,
    "original_id": "surah-097-1"
  }
  ```

---

## 🔤 Embeddings

- Model used: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Supports: English, Arabic, Urdu, Hindi, and other major languages.
- Dimensions: 384
- Distance Metric: Cosine similarity

---

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
pip install haystack-ai qdrant-client sentence-transformers openai fastapi uvicorn
```

### Step 2: Start RAG Backend Server
```bash
uvicorn main:app --port 8000 --reload
```

### Step 3: Test the API
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the Night of Decree?"}'
```

**Expected Response:**
```json
{
  "answer": "Generated response based on Quran verses...",
  "source": "qdrant_collection",
  "documents_found": 5,
  "collection_name": "quran-mdx"
}
```

---

## 📊 Pipeline Performance

✅ **Successful Metrics:**
- **Document Retrieval**: 5 relevant verses per query
- **Response Time**: ~2-3 seconds (including embedding + retrieval + generation)
- **Accuracy**: Responses based on actual Quran content, not general AI knowledge
- **Coverage**: 6,236 verses across all 114 surahs

**🔍 Debug Output Example:**
```
Direct Qdrant search returned 5 results
CustomQdrantRetriever found 5 results
Pipeline final documents: 5 from Qdrant collection 'quran-mdx'
Generated response length: 178 characters
```

---

## 🔎 Search Logic and Field Handling (2025 Update)

### Streamlit Uploader (`streamlit_uploader.py` & `data_loader1.py`)
- **Verse Extraction:**
  - Uses improved regex to extract both verse number and verse text from MDX files.
  - Stores verse number as `verse_number` and text as `text` in Qdrant payload.
- **Metadata:**
  - Each document now includes: `verse_number`, `heading` (surah title), `section_index`, `token_count`, `topics` (matched keywords from `cleaned_words_list.txt`), and `source` (filename).
- **Topic Extraction:**
  - For each verse, checks for presence of any keyword from the topic list (case-insensitive) and stores as a comma-separated string in `topics`.
- **Test Mode:**
  - UI checkbox allows uploading only the first 10 records for fast testing, or all records for full upload.

### Backend API (`main.py`)
- **Prompt Template:**
  - Now includes verse number and surah in the context for the LLM:
    ```
    Verse {{ document.meta['verse_number'] }} ({{ document.meta['heading'] }}): {{ document.content }}
    ```
- **API Response:**
  - Returns a `verses` array with each supporting verse, including:
    - `verse_number`, `surah`, `section_index`, `token_count`, `topics`, `source_file`, `content`
  - Example:
    ```json
    {
      "answer": "...",
      "verses": [
        {
          "verse_number": "39",
          "surah": "Surah 11 - Hud (Hud)",
          "section_index": 38,
          "tokens": 37,
          "topics": "ear,earth,hereafter",
          "source_file": "surah-011.mdx",
          "content": "(39) And you are going to know who will get a punishment..."
        },
        ...
      ]
    }
    ```

### Astro Frontend (`CustomSearchImpl.tsx`)
- **FlexSearch Index:**
  - Loads `flexsearch-index.json` containing all surahs and verses.
  - Indexes both `title` and `content` fields for fast search.
- **Search Results:**
  - When a user types a query, searches both surah titles and verse content.
  - Combines, deduplicates, and displays up to 10 relevant results.
  - Each result links to the surah page and shows the surah title.
- **Field Consistency:**
  - The search index and all backend/frontend logic now use the same field names as the Qdrant collection and uploader pipeline.

---

## Example Search Flow
1. **User uploads MDX files via Streamlit uploader.**
   - Verses and metadata are extracted and uploaded to Qdrant.
2. **User asks a question via chat or search.**
   - Backend retrieves relevant verses, including all metadata.
   - Frontend displays summary and an ordered list of supporting verses with surah, verse number, and content.
3. **User searches via Astro search bar.**
   - FlexSearch returns matching surahs/verses, linking to the correct docs page.

---

**All components are now aligned for robust, metadata-rich Quranic search and retrieval!**

---

## 🧠 Future Enhancements

- Support Arabic question input
- Multi-language response generation
- Citation tracking with verse references
- Add OCR from scanned PDFs
- Integration with Directus CMS
- Caching layer for improved performance

---

## ✅ Troubleshooting

**Common Issues Resolved:**
1. **Field Mapping**: Custom retriever handles Qdrant payload structure properly
2. **Pipeline Outputs**: Uses `include_outputs_from` for intermediate component results
3. **Document Content**: Converts Qdrant `text` field to Haystack Document `content` field
4. **Embedding Compatibility**: Embedder warm-up before pipeline execution
5. **Architecture Decision**: Hybrid approach balances control and orchestration benefits

**🔍 Debugging Approach:**
```bash
# Server logs show dual validation:
Direct Qdrant search returned 5 results  # Proves retrieval works
CustomQdrantRetriever found 5 results    # Proves component works
Pipeline final documents: 5              # Proves integration works
```

---

## 🎯 Architectural Benefits Achieved

**✅ Production Ready:**
- Error handling and graceful degradation
- Comprehensive logging and monitoring
- Easy testing and validation

**✅ Developer Friendly:**
- Clear component separation
- Easy debugging and troubleshooting
- Standardized Haystack patterns where beneficial

**✅ Performance Optimized:**
- Direct Qdrant client for optimal retrieval
- Minimal overhead from Haystack orchestration
- Efficient embedding and response generation

**✅ Future Proof:**
- Easy to add new components (re-rankers, evaluators)
- Simple migration to different LLMs or vector stores
- Scalable architecture for additional features

---

Created by: Your Astro-Quran Project ✨