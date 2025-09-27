import streamlit as st
from io import StringIO
from docx import Document
import PyPDF2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
import os
# Create a folder for nltk data
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)

# Download punkt if not already present
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_dir)

# Add this folder to nltk paths so Sumy can find it
nltk.data.path.append(nltk_data_dir)

# Extract text from different file typess
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

# Summarize text fast using chunks
def summarize_text(text, sentences_per_chunk=3):
    summarizer = LexRankSummarizer()
    words = text.split()
    chunk_size = 1000  # words per chunk
    summary = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        parser = PlaintextParser.from_string(chunk, Tokenizer("english"))
        chunk_summary = summarizer(parser.document, sentences_per_chunk)
        summary.extend([str(sentence) for sentence in chunk_summary])

    return " ".join(summary)

# Streamlit UI
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
                summary = summarize_text(text, sentences_per_chunk=3)  # adjust per chunk
            st.subheader("Summary")
            st.text_area("Summary", summary, height=200)
    else:
        st.error("Unsupported file type or failed to extract text.")
