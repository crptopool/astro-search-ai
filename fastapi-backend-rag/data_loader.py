import os
import frontmatter
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import uuid

# Qdrant Cloud config
QDRANT_URL = "https://6eead27a-8dd0-4a6f-8061-cada1c105bde.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.sdhAmXk-1tknFWteBcrN2DXWTegesOEayGQUfUb0Xmg"
COLLECTION_NAME = "quran-mdx"

# Load multilingual model
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Init Qdrant client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Recreate collection
if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
    client.delete_collection(collection_name=COLLECTION_NAME)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
)

from pathlib import Path

# Check if the updated path exists after kernel reset
mdx_dir = Path(r"D:\ASTROJSPROJECTS\astro-directus-project\astro-quran\src\content\docs\surahs")
# mdx_dir.exists()
# Load MDX files
# mdx_dir = Path("../astro-quran/src/content/docs/surahs")
documents = []

for mdx_file in mdx_dir.glob("*.mdx"):
    post = frontmatter.load(mdx_file)
    text = post.content
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for i, chunk in enumerate(paragraphs):
        # Generate a UUID string for the ID instead of using text-based format
        doc_id = str(uuid.uuid4())
        documents.append({
            "id": doc_id,
            "text": chunk,
            "metadata": {
                "source": mdx_file.name,
                "chunk_id": i,
                "original_id": f"{mdx_file.stem}-{i}"  # Keep original ID in metadata
            }
        })

# Embed and upload to Qdrant
for doc in tqdm(documents):
    embedding = model.encode(doc["text"]).tolist()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            rest.PointStruct(
                id=doc["id"],
                vector=embedding,
                payload={
                    "text": doc["text"],
                    "source": doc["metadata"]["source"],
                    "chunk_id": doc["metadata"]["chunk_id"],
                    "original_id": doc["metadata"]["original_id"]  # Include original ID in payload
                }
            )
        ]
    )

print(f"✅ Uploaded {len(documents)} chunks to Qdrant collection '{COLLECTION_NAME}'")
