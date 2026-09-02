from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

from mode.semantic_search import search_documents


RAG_PROMPT_TEMPLATE = """Tu es un assistant qui répond aux questions UNIQUEMENT
à partir du contexte fourni ci-dessous, extrait des documents de l'utilisateur.

Règles strictes :
- Si la réponse ne se trouve pas dans le contexte, dis clairement
  "Je ne trouve pas cette information dans les documents fournis."
- Ne fabrique jamais d'information qui n'est pas dans le contexte.
- Réponds de façon claire et concise, en français.

Contexte :
{context}

Question : {question}

Réponse :"""

# Construction du prompt
def build_prompt_template():
    
    return PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE,
    )

# pipeline RAG complet.
def generate_rag_answer(vector_store, question, model_name="mistral", k=4):
    
    # Récupération des extraits pertinents 
    results = search_documents(vector_store, question, k=k)

    if not results:
        return {
            "answer": "Aucun extrait pertinent n'a été trouvé dans les documents indexés.",
            "sources": [],
        }

    # On assemble les extraits en un seul bloc de texte pour le {context}
    context_text = "\n\n".join(
        f"[Source : {r['source']}]\n{r['content']}" for r in results
    )

    # Construction du prompt final (instructions + contexte + question)
    prompt_template = build_prompt_template()
    final_prompt = prompt_template.format(context=context_text, question=question)

    # Appel au LLM local via Ollama 
    llm = Ollama(model=model_name)
    answer = llm.invoke(final_prompt)

    return {
        "answer": answer.strip(),
        "sources": results,
    }