import os
import uuid
from pathlib import Path
import frontmatter
from markdown import markdown
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import nltk

# === Config ===
QDRANT_URL = "https://6eead27a-8dd0-4a6f-8061-cada1c105bde.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"  # Replace with your actual key
COLLECTION_NAME = "quran-mdx"
MDX_DIR = Path(r"D:\ASTROJSPROJECTS\astro-directus-project\astro-quran\src\content\docs\surahs")

# === Initialize Qdrant ===
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Delete and recreate the collection
if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
    client.delete_collection(collection_name=COLLECTION_NAME)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
)

# === Load embedding model ===
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# === Optional: NLTK tokenizer for token count ===
nltk.download('punkt')
from nltk.tokenize import word_tokenize

# === Markdown → Semantic Chunk Extractor ===
def extract_chunks_from_mdx(mdx_text):
    html = markdown(mdx_text)
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    current_section = {"heading": "Introduction", "content": []}

    for elem in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if elem.name in ['h1', 'h2', 'h3']:
            if current_section["content"]:
                sections.append(current_section)
            current_section = {
                "heading": elem.get_text().strip(),
                "content": []
            }
        elif elem.name == 'p':
            current_section["content"].append(elem.get_text().strip())

    if current_section["content"]:
        sections.append(current_section)

    return sections

# === Parse and Chunk ===
documents = []

for mdx_file in MDX_DIR.glob("*.mdx"):
    post = frontmatter.load(mdx_file)
    sections = extract_chunks_from_mdx(post.content)

    for i, section in enumerate(sections):
        combined_text = "\n".join(section["content"]).strip()
        if not combined_text:
            continue

        token_count = len(word_tokenize(combined_text))
        doc_id = str(uuid.uuid4())

        documents.append({
            "id": doc_id,
            "text": combined_text,
            "metadata": {
                "source": mdx_file.name,
                "heading": section["heading"],
                "section_index": i,
                "token_count": token_count
            }
        })

print(f"📄 Extracted {len(documents)} chunks from {len(list(MDX_DIR.glob('*.mdx')))} MDX files")

# === Embed and Upload to Qdrant ===
for doc in tqdm(documents, desc="Uploading to Qdrant"):
    embedding = model.encode(doc["text"]).tolist()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            rest.PointStruct(
                id=doc["id"],
                vector=embedding,
                payload={
                    "text": doc["text"],
                    **doc["metadata"]
                }
            )
        ]
    )

print(f"✅ Uploaded {len(documents)} documents to Qdrant collection '{COLLECTION_NAME}'")
