# 📚 Clone NotebookLM — Système RAG 100% Local

Conception d'un système RAG (Retrieval-Augmented Generation) entièrement local, permettant d'interagir intelligemment avec ses propres documents, sans aucun appel à une API externe.

---

## 🎯 Objectif

L'objectif est de concevoir et développer de A à Z un système RAG **entièrement local**, un clone simplifié de NotebookLM.

L'application permet à un utilisateur de charger ses propres documents (PDF, Markdown, TXT) et d'interagir avec eux de manière intelligente, tout en garantissant la **confidentialité totale des données** : aucun appel à une API externe (OpenAI, Claude, Gemini...), tout tourne sur la machine de l'utilisateur.

Deux modes de fonctionnement sont proposés, activables via un bouton toggle dans l'interface :

1. **Recherche sémantique pure** — sans génération LLM, affiche les extraits bruts retrouvés dans les documents. Sert à vérifier que la partie "recherche" du RAG fonctionne correctement.
2. **Assistant RAG complet** — génération LLM contrainte par les documents fournis, avec affichage des sources utilisées (transparence).

### Ce que le TP permet de comprendre concrètement

| Notion | Où elle intervient dans le projet |
|---|---|
| **Ingestion / Chunking / Embeddings** | `ingestion.py` — traitement des documents uploadés |
| **Base vectorielle** | ChromaDB — stockage et recherche par similarité |
| **Recherche sémantique** | `mode/semantic_search.py` — retrieval sans LLM |
| **RAG complet** | `mode/rag_complete.py` — retrieval + prompt + génération LLM |
| **LLM local** | Ollama — aucune donnée ne quitte la machine |
| **Framework d'orchestration** | LangChain — connecte les briques entre elles |

---

## 🗂️ Structure du projet

```
rag-local-tp/
├── app.py                     # Interface Streamlit (affichage, état de session)
├── ingestion.py                # Pipeline d'ingestion (extraction, chunking, vectorisation)
├── requirements.txt             # Dépendances Python
├── mode/
│   ├── __init__.py
│   ├── semantic_search.py       # Mode 1 : recherche sémantique pure (sans LLM)
│   └── rag_complete.py           # Mode 2 : RAG complet (contexte + LLM local)
└── chroma_db/                    # Base vectorielle générée automatiquement (créée à l'usage)
```

### Rôle de chaque outil utilisé

| Outil | Catégorie | Rôle |
|---|---|---|
| **LangChain** | Framework | Fournit les briques prêtes à l'emploi (DocumentLoaders, TextSplitter, wrapper Chroma) et les connecte entre elles |
| **PyMuPDF** | Extraction | Lit le contenu réel des fichiers PDF |
| **sentence-transformers** | Embeddings | Transforme un texte en vecteur numérique représentant son sens, calculé localement |
| **ChromaDB** | Base vectorielle | Stocke les vecteurs et retrouve les passages les plus proches d'une question |
| **Ollama** | LLM local | Fait tourner le modèle de langage (Mistral, Qwen...) directement sur la machine |
| **Streamlit** | Interface | Interface web du chat et de l'upload de documents |

---

## ⚙️ Installation (Windows / PowerShell)

### 1. Créer le dossier du projet et un environnement virtuel

```powershell
mkdir rag-local-tp
cd rag-local-tp
python -m venv venv
```

### 2. Activer l'environnement virtuel

```powershell
.\venv\Scripts\Activate.ps1
```

> Si une erreur de type *"l'exécution de scripts est désactivée"* apparaît :
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Tu dois voir `(venv)` apparaître au début de la ligne de commande.

### 3. Installer les dépendances Python

```powershell
pip install -r requirements.txt
```

Ou manuellement :

```powershell
pip install langchain langchain-community chromadb sentence-transformers streamlit pymupdf pypdf
```

*(installation assez longue : chromadb et sentence-transformers sont volumineux)*

### 4. Installer et lancer Ollama

Ollama fait tourner le LLM local (aucune donnée envoyée sur Internet).

1. Télécharger Ollama pour Windows : **https://ollama.com/download**
2. Installer (suivant → suivant → terminer). Ollama tourne ensuite automatiquement en arrière-plan (icône dans la barre système).
3. Télécharger un modèle, dans un terminal PowerShell :

```powershell
ollama pull mistral
```

*(alternative plus légère/rapide : `ollama pull qwen2.5-coder`)*

4. Vérifier que le modèle fonctionne :

```powershell
ollama run mistral
```

Discuter directement dans le terminal pour tester, puis `/bye` pour quitter. Ollama continue de tourner en fond, prêt à être appelé par l'application.

### 5. Vérifier que tout est prêt

```powershell
python -c "import streamlit, langchain, chromadb; print('OK')"
```

Si `OK` s'affiche sans erreur : l'installation est complète.

---

## ▶️ Lancer l'application

Depuis le dossier `rag-local-tp` (venv activé, Ollama démarré) :

```powershell
streamlit run app.py
```

L'interface s'ouvre automatiquement dans le navigateur sur `http://localhost:8501`.

### Utilisation

1. **Charger des documents** — glisser un ou plusieurs fichiers PDF / MD / TXT dans la barre latérale
2. **Indexer** — cliquer sur "🔎 Indexer les documents" (extraction → chunking → embeddings → stockage Chroma)
3. **Choisir un mode** :
   - Toggle **désactivé** → recherche sémantique pure, extraits bruts avec source
   - Toggle **activé** → réponse rédigée par le LLM local, avec un menu déroulant "📎 Voir les extraits utilisés" pour la transparence
4. **Poser une question** dans la zone de chat en bas de l'écran

---

## 🧠 Fonctionnement interne (résumé)

```
Documents uploadés
    ↓ extraction (PyMuPDF / TextLoader)
    ↓ chunking (découpage en segments)
    ↓ embeddings (sentence-transformers, en local)
    ↓ stockage (ChromaDB)

Question posée
    ↓ recherche des passages les plus proches (similarité vectorielle)
    ↓ [Mode recherche pure] → affichage direct des extraits
    ↓ [Mode RAG complet] → extraits + question envoyés au LLM (Ollama)
    ↓ réponse générée, contrainte au contexte fourni
```

**Règle de sécurité appliquée dans le prompt du mode RAG complet :** le LLM reçoit l'instruction stricte de ne répondre qu'à partir du contexte fourni, et de dire clairement quand une information n'y figure pas — afin de limiter les hallucinations.

---

## 📦 Fichiers de rendu

- Code source complet : `app.py`, `ingestion.py`, `mode/semantic_search.py`, `mode/rag_complete.py`
- `requirements.txt` pour l'installation des dépendances
- Ce `README.md`

---

## 🔒 Confidentialité

Aucune donnée (document, question, réponse) ne quitte la machine locale : l'extraction, les embeddings et la génération LLM tournent tous entièrement en local via Ollama et sentence-transformers.
