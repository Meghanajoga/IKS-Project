import streamlit as st
from docx import Document
import PyPDF2
from transformers import pipeline

# -------------------------------
# Load summarizer once (cached)
# -------------------------------
@st.cache_resource
def load_summarizer():
    # Using smaller, faster model
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = load_summarizer()

# -------------------------------
# Function to extract text
# -------------------------------
def extract_text(file):
    if file.type == "text/plain":
        return file.getvalue().decode("utf-8")
    elif file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        return None

# -------------------------------
# Split text into chunks
# -------------------------------
def split_text_into_chunks(text, chunk_size=2000):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 <= chunk_size:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk)
            current_chunk = para + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# -------------------------------
# Summarize text in chunks
# -------------------------------
def summarize_text(text):
    summary_text = ""
    chunks = split_text_into_chunks(text, chunk_size=2000)
    for chunk in chunks:
        summary = summarizer(
            chunk, max_length=130, min_length=50, do_sample=False
        )[0]['summary_text']
        summary_text += summary + " "
    return summary_text.strip()

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Summarization Assistant")
st.title("Summarization Assistant")

uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if text:
        st.subheader("Original Text")
        st.text_area("Content", text, height=300)

        if st.button("📝 Summarize"):
            with st.spinner("Summarizing..."):
                summary = summarize_text(text)
            st.subheader("Summary")
            st.text_area("Summary", summary, height=200)
    else:
        st.error("Unsupported file type or failed to extract text.")
