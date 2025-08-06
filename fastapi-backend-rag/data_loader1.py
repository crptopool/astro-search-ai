import os
import re
import uuid
from pathlib import Path
import frontmatter
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer
from nltk.tokenize import word_tokenize
import nltk

# Download punkt tokenizer if not already available
nltk.download('punkt', quiet=True)

# Load keyword list from file and normalize to lowercase
TOPIC_KEYWORDS_PATH = Path(__file__).parent / "cleaned_words_list.txt"
with open(TOPIC_KEYWORDS_PATH, "r", encoding="utf-8") as f:
    TOPIC_KEYWORDS = [line.strip().lower() for line in f if line.strip()]

def load_and_upload_mdx_files_to_qdrant(
    mdx_dir_path: str,
    qdrant_url: str,
    qdrant_api_key: str,
    collection_name: str,
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    max_records: int = None
):
    mdx_dir = Path(mdx_dir_path)
    if not mdx_dir.exists():
        raise FileNotFoundError(f"Directory not found: {mdx_dir_path}")

    # Initialize model and Qdrant client
    model = SentenceTransformer(model_name)
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Recreate collection if it exists
    existing_collections = [c.name for c in client.get_collections().collections]
    if collection_name in existing_collections:
        client.delete_collection(collection_name=collection_name)

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
    )

    documents = []
    record_count = 0

    verse_pattern = re.compile(
        r'<VerseCard\s+verseNumber=\{(\d+)\}\s+chapterNumber=\{(\d+)\}\s+arabicText=".*?"\s+translation="(.*?)"\s+transliteration=".*?"\s*/>',
        re.DOTALL
    )

    for mdx_file in mdx_dir.glob("*.mdx"):
        post = frontmatter.load(mdx_file)
        title = post.get("title", "Unknown Surah")
        content = post.content

        verses = verse_pattern.findall(content)
        for i, (verse_number, chapter_number, translation) in enumerate(verses):
            clean_text = translation.strip()
            if not clean_text:
                continue

            token_count = len(word_tokenize(clean_text))
            lower_text = clean_text.lower()
            matched_topics = [kw for kw in TOPIC_KEYWORDS if kw in lower_text]
            topic_str = ",".join(sorted(set(matched_topics)))
            documents.append({
                "id": str(uuid.uuid4()),
                "text": clean_text,
                "metadata": {
                    "verse_number": int(verse_number),
                    "chapter_number": int(chapter_number),
                    "source": mdx_file.name,
                    "heading": title,
                    "section_index": i,
                    "token_count": token_count,
                    "topics": topic_str  # Reserved for future keyword tagging
                }
            })

            record_count += 1
            if max_records is not None and record_count >= max_records:
                break

        if max_records is not None and record_count >= max_records:
            break

    for doc in documents:
        embedding = model.encode(doc["text"]).tolist()
        client.upsert(
            collection_name=collection_name,
            points=[
                rest.PointStruct(
                    id=doc["id"],
                    vector=embedding,
                    payload={"text": doc["text"], **doc["metadata"]}
                )
            ]
        )

    return documents