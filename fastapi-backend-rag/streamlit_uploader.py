import streamlit as st
import pandas as pd
from pathlib import Path
from data_loader1 import load_and_upload_mdx_files_to_qdrant

# App settings
st.set_page_config(page_title="Quran MDX Uploader", layout="wide")
st.title("📤 Quran MDX Streamlit Uploader")

# Qdrant connection configuration
QDRANT_URL = "https://6eead27a-8dd0-4a6f-8061-cada1c105bde.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.sdhAmXk-1tknFWteBcrN2DXWTegesOEayGQUfUb0Xmg"  # replace with your actual key
COLLECTION_NAME = "quran-mdx"

# mdx_files_path="D:\ASTROJSPROJECTS\astro-directus-project\astro-quran\src\content\docs\surahs"
# Input: Folder selector for MDX files
st.markdown("### 1️⃣ Select the folder containing your `.mdx` files")
# mdx_dir_path = st.text_input("MDX Folder Path", value=str(Path.cwd()))
mdx_dir_path = st.text_input(
    "MDX Folder Path",
    value="D:\\ASTROJSPROJECTS\\astro-directus-project\\astro-quran\\src\\content\\docs\\surahs"
)
# Add checkbox for test mode
test_mode = st.checkbox("Test mode: Only upload first 10 records (faster)")

# Upload button
if st.button("📤 Upload and Embed to Qdrant"):
    try:
        with st.spinner("Processing and uploading documents..."):
            docs = load_and_upload_mdx_files_to_qdrant(
                mdx_dir_path=mdx_dir_path,
                qdrant_url=QDRANT_URL,
                qdrant_api_key=QDRANT_API_KEY,
                collection_name=COLLECTION_NAME,
                max_records=10 if test_mode else None  # Pass limit if test mode
            )
        st.success(f"✅ Uploaded {len(docs)} chunks to Qdrant collection `{COLLECTION_NAME}`")
        st.session_state['uploaded_docs'] = docs
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Display uploaded document summary
if 'uploaded_docs' in st.session_state:
    st.markdown("### 2️⃣ Uploaded Chunk Summary")
    df = pd.DataFrame([
        {
            "Verse #": doc["metadata"].get("verse_number", ""),
            "Verse": doc["text"][:80] + "..." if len(doc["text"]) > 80 else doc["text"],
            "Tokens": doc["metadata"]["token_count"],
            "Topics": doc["metadata"]["topics"],
            "Surah": doc["metadata"]["heading"],
            "Source File": doc["metadata"]["source"]
        }
        for doc in st.session_state['uploaded_docs']
    ])
    st.dataframe(df, use_container_width=True)

    st.markdown("### 3️⃣ Keyword Filter")
    # Show available columns
    st.write("Available columns:", df.columns.tolist())

    # Normalize column names to lowercase (safely)
    df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]

    # Now safe to use
    if "topics" in df.columns:
        keywords = st.multiselect("Filter by topic keyword", options=df["topics"].dropna().unique())
        if keywords:
            filtered_df = df[df["topics"].isin(keywords)]
            st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("❌ 'topics' column not found in the uploaded chunk metadata.")
