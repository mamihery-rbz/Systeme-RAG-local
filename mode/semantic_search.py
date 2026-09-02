# Interroge la base vectorielle et retourne les chunks les plus proches sans passer par un LLM.
def search_documents(vector_store, question, k=4):
    
    if vector_store is None:
        return []

    results = vector_store.similarity_search(question, k=k)

    formatted_results = []
    for doc in results:
        formatted_results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Fichier inconnu"),
        })

    return formatted_results

# Met en forme les résultats de search_documents() pour un affichage
# Streamlit propre
def format_results_as_markdown(results):
   
    if not results:
        return "Aucun extrait pertinent trouvé pour cette question."

    blocks = []
    for i, result in enumerate(results, start=1):
        blocks.append(
            f"**Extrait {i}** — *source : {result['source']}*\n\n"
            f"> {result['content']}"
        )

    return "\n\n---\n\n".join(blocks)