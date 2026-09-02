import os
import tempfile

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Extraction
def extract_documents(uploaded_files):
    all_documents = []

    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()

        # Écriture temporaire sur disque
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            if suffix == ".pdf":
                loader = PyMuPDFLoader(tmp_path)
            elif suffix in (".txt", ".md"):
                loader = TextLoader(tmp_path, encoding="utf-8")
            else:
                continue

            documents = loader.load()

            # On force le nom du fichier ORIGINAL (pas le nom temporaire)
            # dans les métadonnées, pour l'affichage des sources plus tard.
            for doc in documents:
                doc.metadata["source"] = uploaded_file.name

            all_documents.extend(documents)

        finally:
            # on supprime le fichier temporaire dans tous les cas
            os.remove(tmp_path)

    return all_documents

# Chunking (découpage).
def chunk_documents(documents, chunk_size=800, chunk_overlap=150):
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return chunks


# Vectorisation + stockage.
def create_vector_store(chunks, persist_directory="chroma_db"):
   
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    return vector_store