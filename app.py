# =============================================================================
# app.py
# TP RAG Local - Clone de NotebookLM
# Interface Streamlit uniquement : affichage, état de session, réaction aux clics.
# =============================================================================
#
# La logique de traitement (extraction, chunking, vectorisation) vit dans
# ingestion.py, importée ci-dessous. Ça garde ce fichier concentré sur
# l'interface, plus facile à lire et à maintenir.
# =============================================================================

import streamlit as st
from ingestion import extract_documents, chunk_documents, create_vector_store
from mode.semantic_search import search_documents, format_results_as_markdown
from mode.rag_complete import generate_rag_answer

# -----------------------------------------------------------------------------
# Configuration générale de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Clone NotebookLM - RAG Local",
    page_icon="📚",
    layout="wide",
)

# -----------------------------------------------------------------------------
# État de session (mémoire de l'appli entre les interactions)
# -----------------------------------------------------------------------------
# Streamlit ré-exécute tout le script à chaque interaction utilisateur.
# st.session_state permet de conserver des valeurs (historique, index, etc.)
# d'une exécution à l'autre, tant que la page n'est pas rechargée.

if "chat_history" not in st.session_state:
    # Liste de dicts : {"role": "user"/"assistant", "content": "texte"}
    st.session_state.chat_history = []

if "documents_indexed" not in st.session_state:
    st.session_state.documents_indexed = False

if "vector_store" not in st.session_state:
    # Contiendra la base vectorielle Chroma une fois l'indexation faite
    st.session_state.vector_store = None


# sidebar
with st.sidebar:
    st.title("📁 Documents")
    st.caption("Charge tes fichiers, indexe-les, puis discute avec eux.")

    st.divider()

    # --- upload de fichiers -------------------------------------------
    uploaded_files = st.file_uploader(
        label="Charger des documents",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
        help="Formats acceptés : PDF, Markdown, TXT",
    )

    if uploaded_files:
        st.write(f"**{len(uploaded_files)} fichier(s) chargé(s) :**")
        for f in uploaded_files:
            st.write(f"- {f.name}")

    st.divider()

    # --- Bouton d'indexation ---------------------------------------------------
    index_button = st.button(
        "🔎 Indexer les documents",
        use_container_width=True,
        disabled=(not uploaded_files),
    )

    if index_button:
        # Les 3 etapes du pipeline
        with st.spinner("Extraction du texte des documents..."):
            documents = extract_documents(uploaded_files)

        if not documents:
            st.error("Aucun texte n'a pu être extrait des fichiers fournis.")
        else:
            with st.spinner(f"Découpage en chunks ({len(documents)} document(s))..."):
                chunks = chunk_documents(documents)

            with st.spinner(f"Calcul des embeddings ({len(chunks)} chunks)..."):
                vector_store = create_vector_store(chunks)

            # Base vectorielle en memoire
            st.session_state.vector_store = vector_store
            st.session_state.documents_indexed = True

            st.success(
                f"✅ {len(documents)} document(s) indexé(s) "
                f"en {len(chunks)} chunks."
            )

    if st.session_state.documents_indexed:
        st.info("✅ Documents indexés et prêts pour la recherche.")
    else:
        st.warning("⚠️ Aucun document indexé pour l'instant.")

    st.divider()

    # Toggle activation LLM
    use_llm = st.toggle(
        "🤖 Assistant RAG complet (LLM)",
        value=False,
        help=(
            "Désactivé : recherche sémantique pure, affiche les extraits bruts.\n"
            "Activé : le LLM local génère une réponse à partir des extraits."
        ),
    )

    mode_label = "Assistant RAG complet" if use_llm else "Recherche sémantique pure"
    st.caption(f"Mode actif : **{mode_label}**")


# interface conversationnelle
st.title("📚 Clone NotebookLM — RAG 100% local")
st.caption("On utilise Ollama.")

# Affichage de l'historique de conversation 
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message.get("sources"):
            with st.expander("Voir les extraits utilisés comme contexte"):
                for i, src in enumerate(message["sources"], start=1):
                    st.markdown(f"**Extrait {i}** — *source : {src['source']}*")
                    st.markdown(f"> {src['content']}")

# Zone de saisie utilisateur
user_question = st.chat_input("Pose une question sur tes documents...")

if user_question:
    # Afficher et enregistrer le message utilisateur
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Generer une réponse selon le mode actif
    sources = None  
    if not st.session_state.documents_indexed:
        response = "⚠️ Merci d'indexer au moins un document avant de poser une question."

    elif use_llm:
        with st.spinner("Recherche du contexte puis génération de la réponse..."):
            result = generate_rag_answer(st.session_state.vector_store, user_question)
        response = result["answer"]
        sources = result["sources"]

    else:
        # Mode Recherche semantique pure
        # on affiche directement les extraits bruts trouvés dans Chroma.
        results = search_documents(st.session_state.vector_store, user_question)
        response = format_results_as_markdown(results)

    # Enregistrer et afficher la réponse (+ extraits si mode RAG complet)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "sources": sources,
    })
    with st.chat_message("assistant"):
        st.markdown(response)
        if sources:
            with st.expander("Voir les extraits utilisés comme contexte"):
                for i, src in enumerate(sources, start=1):
                    st.markdown(f"**Extrait {i}** — *source : {src['source']}*")
                    st.markdown(f"> {src['content']}")