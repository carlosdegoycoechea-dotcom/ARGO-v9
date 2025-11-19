# ARGO v9.0 - Architecture & Data Flow

## Overview

ARGO v9.0 is an Enterprise PMO Platform built with Clean Architecture principles, featuring unified data management, intelligent RAG (Retrieval-Augmented Generation), and multi-model LLM routing.

---

## System Components

### Core Layer
- **bootstrap.py** - System initialization orchestrator
- **config.py** - Configuration management
- **unified_database.py** - Single source of truth for all data
- **model_router.py** - Intelligent LLM routing (GPT-4 ↔ Claude)
- **llm_provider.py** - OpenAI & Anthropic client management
- **rag_engine.py** - Advanced RAG with HyDE + Reranking
- **library_manager.py** - Global knowledge library
- **logger.py** - Centralized logging

### Application Layer
- **app/ui.py** - Streamlit professional UI
- **app/panels/analytics_panel.py** - Analytics dashboard

### Tools Layer
- **tools/extractors.py** - Document text extraction (PDF, DOCX, XLSX, etc.)
- **tools/google_drive_sync.py** - Google Drive integration

---

## 1. System Initialization Flow

```mermaid
graph TD
    A[User starts: streamlit run app/ui.py] --> B[UI imports bootstrap]
    B --> C[ARGOBootstrap.initialize]
    C --> D[Phase 1: Load Configuration]
    D --> E[Phase 2: Initialize Logging]
    E --> F[Phase 3: Create UnifiedDatabase]
    F --> G[Phase 4: Initialize ModelRouter]
    G --> H[Phase 5: Initialize LibraryManager]
    H --> I[Phase 6: Ensure Project Exists]
    I --> J[Phase 7: Create Project Components]
    J --> K[Create Vectorstore ChromaDB]
    J --> L[Create RAG Engine]
    J --> M[Initialize Watchers Optional]
    L --> N[System Ready]
    K --> N
    M --> N
    N --> O[Return ARGO dict with all components]
    O --> P[UI loads session_state]
```

**Key Objects Created:**
- `config` - Configuration manager
- `unified_db` - SQLite database with all tables
- `model_router` - LLM routing intelligence
- `vectorstore` - ChromaDB for embeddings (per project)
- `rag_engine` - RAG search orchestrator
- `library_manager` - Global knowledge base

---

## 2. User Query Flow (Complete End-to-End)

```mermaid
graph TD
    A[User types message in Chat] --> B[st.chat_input captures prompt]
    B --> C[Append to session_state.messages]
    C --> D[Get search_settings from sidebar]
    D --> E[Call rag_engine.search]

    E --> F[RAG Engine Processing]
    F --> G{use_hyde enabled?}
    G -->|Yes| H[Generate hypothetical document]
    G -->|No| I[Use original query]
    H --> I

    I --> J[Search Project Vectorstore]
    I --> K[Search Library Vectorstore]

    J --> L[Get top-k results with scores]
    K --> L

    L --> M{use_reranker enabled?}
    M -->|Yes| N[Rerank results by relevance]
    M -->|No| O[Use original scores]
    N --> O

    O --> P[Format context from results]
    P --> Q[Update st.session_state.last_sources]

    Q --> R[Build system prompt with context]
    R --> S[Prepare messages array]
    S --> T[Call model_router.run]

    T --> U{override_provider set?}
    U -->|Yes| V[Use specified provider]
    U -->|No| W[Smart routing by task_type]

    V --> X[Select model and parameters]
    W --> X

    X --> Y{Provider?}
    Y -->|openai| Z[ChatOpenAI with httpx clients]
    Y -->|anthropic| AA[ChatAnthropic]

    Z --> AB[Call OpenAI API]
    AA --> AC[Call Anthropic API]

    AB --> AD[Log API usage to unified_db]
    AC --> AD

    AD --> AE[Return LLMResponse object]
    AE --> AF[Extract response.content]

    AF --> AG[Calculate confidence score]
    AG --> AH[Extract sources metadata]
    AH --> AI[Display response in chat]

    AI --> AJ[Append assistant message to session_state]
    AJ --> AK[Auto-save conversation to unified_db]
    AK --> AL[Update Active Sources panel]
    AL --> AM[Show confidence indicator]
    AM --> AN[Display feedback buttons]
```

---

## 3. Document Upload & Indexing Flow

```mermaid
graph TD
    A[User uploads file via sidebar] --> B[st.file_uploader captures file]
    B --> C[Save to temp directory]
    C --> D[Call get_file_info]
    D --> E[Calculate hash, size, type]

    E --> F[Call extract_and_chunk]
    F --> G{File Type?}
    G -->|PDF| H[PyPDF2 extraction]
    G -->|DOCX| I[python-docx extraction]
    G -->|XLSX| J[openpyxl extraction]
    G -->|TXT| K[Direct read]

    H --> L[RecursiveCharacterTextSplitter]
    I --> L
    J --> L
    K --> L

    L --> M[Create chunks with metadata]
    M --> N[Return list of chunk dicts]

    N --> O[Index in Vectorstore]
    O --> P[vectorstore.add_texts]
    P --> Q[OpenAI Embeddings API]
    Q --> R[Store in ChromaDB]

    R --> S[Register in UnifiedDatabase]
    S --> T[unified_db.register_file]
    T --> U[INSERT into indexed_files table]

    U --> V[Update UI with success message]
    V --> W[Show chunk count and file size]
```

---

## 4. RAG Search Deep Dive

```mermaid
graph TD
    A[rag_engine.search called] --> B[Receive query and settings]

    B --> C{HyDE enabled?}
    C -->|Yes| D[Generate hypothetical answer]
    C -->|No| E[Use original query]

    D --> F[Embed hypothetical document]
    E --> F[Embed original query]

    F --> G[Check SemanticCache]
    G --> H{Cache hit?}
    H -->|Yes| I[Return cached results]
    H -->|No| J[Perform fresh search]

    J --> K[_search_project vectorstore]
    J --> L[_search_library vectorstore]

    K --> M[similarity_search_with_score]
    L --> M

    M --> N[Combine results]
    N --> O[Apply library boost factor]

    O --> P{Reranker enabled?}
    P -->|Yes| Q[Load Cohere/Cross-Encoder model]
    P -->|No| R[Skip reranking]

    Q --> S[Rerank results]
    S --> T[Update scores]

    T --> U[Sort by final score]
    R --> U

    U --> V[Take top-k results]
    V --> W[Create SearchResult objects]
    W --> X[Store in cache]
    X --> Y[Return results + metadata]
```

---

## 5. Model Routing Logic

```mermaid
graph TD
    A[model_router.run called] --> B{override_provider?}
    B -->|Set| C[Use specified provider]
    B -->|None| D[Smart routing by task_type]

    D --> E{task_type?}
    E -->|chat| F[GPT-4o default]
    E -->|analysis| G[Claude Sonnet]
    E -->|code| H[GPT-4o]
    E -->|creative| I[Claude Sonnet]
    E -->|summarization| J[GPT-4o-mini]

    C --> K[Load model config]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K --> L[Get optimal parameters]
    L --> M[temperature, max_tokens, etc.]

    M --> N{Provider?}
    N -->|openai| O[Create ChatOpenAI]
    N -->|anthropic| P[Create ChatAnthropic]

    O --> Q[Add httpx clients]
    Q --> R[Set model_kwargs]

    P --> S[Set anthropic_kwargs]

    R --> T[Call LLM API]
    S --> T

    T --> U[Log to unified_db.log_api_usage]
    U --> V[Track tokens, cost, model, provider]
    V --> W[Return LLMResponse]
```

---

## 6. Data Storage Architecture

```mermaid
graph TD
    A[UnifiedDatabase SQLite] --> B[Projects Table]
    A --> C[Indexed Files Table]
    A --> D[Conversations Table]
    A --> E[Notes Table]
    A --> F[API Usage Table]
    A --> G[Library Documents Table]
    A --> H[Library Categories Table]

    B --> I[Project metadata, Drive config]
    C --> J[File hashes, chunk counts]
    D --> K[Session messages JSON]
    E --> L[User notes with tags]
    F --> M[Token usage, costs, timestamps]
    G --> N[Global knowledge base]
    H --> O[Category organization]

    P[ChromaDB Vectorstores] --> Q[Project Vectorstore]
    P --> R[Library Vectorstore]

    Q --> S[Document embeddings]
    Q --> T[Chunk metadata]
    R --> U[Library embeddings]
    R --> V[Category metadata]
```

---

## 7. UI State Management

```mermaid
graph TD
    A[st.session_state] --> B[argo_initialized]
    A --> C[argo dict]
    A --> D[config]
    A --> E[messages array]
    A --> F[session_id]
    A --> G[last_sources array]
    A --> H[search_settings dict]

    C --> I[unified_db]
    C --> J[model_router]
    C --> K[rag_engine]
    C --> L[vectorstore]
    C --> M[project dict]

    E --> N[User messages]
    E --> O[Assistant messages]
    E --> P[Metadata sources, confidence]

    H --> Q[use_hyde]
    H --> R[use_reranker]
    H --> S[include_library]
    H --> T[override_provider]
```

---

## 8. Complete Request-Response Cycle

### Step-by-Step Flow

#### **1. Initialization (Once per session)**
```
User → streamlit run app/ui.py
  ↓
UI checks st.session_state.argo_initialized
  ↓
ARGOBootstrap.initialize() called
  ↓
Configuration loaded from config.yaml + .env
  ↓
UnifiedDatabase created (SQLite)
  ↓
ModelRouter initialized (GPT-4 + Claude)
  ↓
Project loaded/created
  ↓
Vectorstore created (ChromaDB)
  ↓
RAG Engine initialized
  ↓
All components stored in st.session_state.argo
  ↓
UI renders with sidebar + main area
```

#### **2. User Query (Each message)**
```
User types "What is the project budget?"
  ↓
UI appends {'role': 'user', 'content': '...'} to messages
  ↓
Gets search_settings from sidebar
  ↓
Calls rag_engine.search(query, settings)
  ↓
RAG Engine:
  - Generates HyDE hypothetical (if enabled)
  - Embeds query → OpenAI Embeddings API
  - Searches project vectorstore (ChromaDB)
  - Searches library vectorstore (ChromaDB)
  - Reranks results (if enabled)
  - Returns top 5 SearchResult objects
  ↓
UI stores sources in st.session_state.last_sources
  ↓
Formats context from results
  ↓
Builds system prompt with context
  ↓
Calls model_router.run(messages, override_provider)
  ↓
ModelRouter:
  - Checks override_provider (from sidebar)
  - If None, routes by task_type (chat → GPT-4)
  - Creates ChatOpenAI with httpx clients
  - Calls OpenAI API
  - Logs usage to unified_db
  - Returns LLMResponse
  ↓
UI displays response
  ↓
Calculates confidence score
  ↓
Shows sources in expander
  ↓
Shows confidence indicator (High/Med/Low)
  ↓
Shows feedback buttons (Helpful/Not Helpful)
  ↓
Appends assistant message to messages
  ↓
Auto-saves conversation to unified_db
  ↓
Updates Active Sources panel in sidebar
```

#### **3. Document Upload**
```
User uploads document.pdf
  ↓
UI saves to temp directory
  ↓
Calls get_file_info() → hash, size, type
  ↓
Calls extract_and_chunk()
  ↓
Extractor:
  - Detects PDF type
  - Uses PyPDF2 to extract text
  - Splits into chunks (RecursiveCharacterTextSplitter)
  - Returns list of {content, metadata} dicts
  ↓
UI indexes in vectorstore:
  - Calls vectorstore.add_texts(texts, metadatas)
  - OpenAI Embeddings API called for each chunk
  - Embeddings stored in ChromaDB
  ↓
UI registers in database:
  - Calls unified_db.register_file()
  - INSERT into indexed_files table
  ↓
UI shows success message with chunk count
```

#### **4. Conversation Management**
```
User clicks "Save" button
  ↓
UI calls unified_db.save_conversation(
    project_id,
    session_id,
    messages array
)
  ↓
UnifiedDatabase:
  - Serializes messages to JSON
  - INSERT/UPDATE conversations table
  ↓
UI shows "Conversation saved" message

User clicks "New Chat"
  ↓
UI generates new session_id
  ↓
Clears st.session_state.messages
  ↓
Reloads UI with empty chat

User clicks "Load" on previous conversation
  ↓
UI calls unified_db.load_conversation(project_id, session_id)
  ↓
UnifiedDatabase:
  - SELECT messages_json from conversations
  - Deserialize JSON to list
  ↓
UI sets st.session_state.messages = loaded_messages
  ↓
UI reruns, showing old conversation
```

#### **5. Notes Management**
```
User creates note
  ↓
UI calls unified_db.save_note(project_id, title, content, tags)
  ↓
UnifiedDatabase:
  - INSERT into notes table
  ↓
UI reloads, shows note in sidebar

User deletes note
  ↓
UI calls unified_db.delete_note(note_id)
  ↓
UnifiedDatabase:
  - DELETE from notes WHERE id = ?
  ↓
UI reloads, note removed
```

---

## 9. External API Integrations

### OpenAI API
- **Used for:**
  - Embeddings (text-embedding-3-small)
  - Chat completion (gpt-4o, gpt-4o-mini)
- **Authentication:** API key in .env
- **Custom httpx clients:** Bypass proxy issues
- **Rate limiting:** Handled by provider
- **Cost tracking:** Logged to unified_db.api_usage

### Anthropic API
- **Used for:**
  - Chat completion (claude-3-5-sonnet)
- **Authentication:** API key in .env
- **Use cases:** Analysis, creative tasks
- **Cost tracking:** Logged to unified_db.api_usage

### Google Drive API (Optional)
- **Used for:**
  - Document sync
- **Authentication:** service_account credentials JSON
- **Sync direction:** Bidirectional
- **Status:** UI placeholder (requires google_drive_sync.py)

---

## 10. Error Handling & Logging

```mermaid
graph TD
    A[Any component encounters error] --> B[Catch exception]
    B --> C[logger.error with exc_info=True]
    C --> D[Write to logs/argo.log]
    D --> E{User-facing?}
    E -->|Yes| F[st.error with user-friendly message]
    E -->|No| G[Continue silently]
    F --> H[User sees error in UI]
    G --> I[Logged for debugging]
```

**Log Levels:**
- DEBUG: Detailed flow information
- INFO: System initialization, query processing
- WARNING: Non-critical issues (missing features)
- ERROR: Failures with stack traces
- CRITICAL: System-breaking errors

**Log Files:**
- `logs/argo.log` - Main application log
- `logs/rag_engine.log` - RAG search operations
- `logs/model_router.log` - LLM routing decisions
- `logs/unified_database.log` - Database operations

---

## 11. Performance Optimizations

### Caching
- **SemanticCache:** RAG search results (24h TTL)
- **Streamlit @st.cache_data:** UI data loading
- **Vectorstore persistence:** ChromaDB on disk

### Database
- **Indexes:** project_id, session_id, created_at
- **Prepared statements:** SQL injection prevention
- **Connection pooling:** Single database file

### API Efficiency
- **Batch embeddings:** Multiple chunks at once
- **Smart routing:** Cheaper models for simple tasks
- **Token limits:** Configurable max_tokens

---

## 12. Security Considerations

### Secrets Management
- ✅ API keys in `.env` (gitignored)
- ✅ Google credentials in `google_credentials.json` (gitignored)
- ✅ No secrets in code
- ✅ Environment variable validation

### Data Security
- ✅ SQLite file permissions
- ✅ No SQL injection (parameterized queries)
- ✅ File upload validation (type, size)
- ✅ Hash-based deduplication

### API Security
- ✅ Custom httpx clients (controlled proxies)
- ✅ Timeout limits (60s)
- ✅ Rate limiting awareness
- ✅ Error handling (no key exposure)

---

## 13. Deployment Architecture

```
ARGO v9.0 Deployment

┌─────────────────────────────────────────────┐
│         User's Local Machine                │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │   Streamlit UI (Port 8501)            │ │
│  │   - Professional corporate interface  │ │
│  │   - Sidebar with all controls         │ │
│  │   - Chat, Documents, Analytics tabs   │ │
│  └───────────────┬───────────────────────┘ │
│                  │                           │
│  ┌───────────────▼───────────────────────┐ │
│  │   ARGO Bootstrap & Core               │ │
│  │   - ModelRouter                       │ │
│  │   - RAG Engine                        │ │
│  │   - UnifiedDatabase                   │ │
│  │   - LibraryManager                    │ │
│  └───────┬───────────────┬───────────────┘ │
│          │               │                   │
│  ┌───────▼──────┐ ┌─────▼──────────────┐   │
│  │  SQLite DB   │ │  ChromaDB          │   │
│  │  - Projects  │ │  - Embeddings      │   │
│  │  - Files     │ │  - Vectors         │   │
│  │  - Notes     │ │  - Metadata        │   │
│  │  - Convos    │ │                    │   │
│  │  - API Usage │ │                    │   │
│  └──────────────┘ └────────────────────┘   │
└─────────────┬───────────────┬───────────────┘
              │               │
      ┌───────▼─────┐  ┌──────▼─────────┐
      │  OpenAI API │  │ Anthropic API  │
      │  - GPT-4o   │  │ - Claude 3.5   │
      │  - Embeddings│ │                │
      └─────────────┘  └────────────────┘
              │
      ┌───────▼──────────┐
      │  Google Drive    │
      │  (Optional sync) │
      └──────────────────┘
```

---

## 14. Technology Stack

### Backend
- **Python 3.10+**
- **LangChain** - LLM orchestration
- **OpenAI SDK** - GPT-4 integration
- **Anthropic SDK** - Claude integration
- **ChromaDB** - Vector database
- **SQLite** - Relational database
- **httpx** - Custom HTTP clients

### Frontend
- **Streamlit** - Web UI framework
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation

### Document Processing
- **PyPDF2** - PDF extraction
- **python-docx** - Word documents
- **openpyxl** - Excel files
- **Markdown** - MD files

### Utilities
- **python-dotenv** - Environment variables
- **PyYAML** - Configuration files
- **hashlib** - File hashing

---

## 15. Key Design Patterns

### Clean Architecture
- **Separation of concerns:** Core, App, Tools layers
- **Dependency inversion:** Core doesn't depend on UI
- **Single responsibility:** Each module has one job

### Repository Pattern
- **UnifiedDatabase:** Single data access layer
- **Abstraction:** Business logic doesn't know SQLite details

### Strategy Pattern
- **ModelRouter:** Different routing strategies per task
- **Extractors:** Different extraction strategies per file type

### Factory Pattern
- **ARGOBootstrap:** Creates all system components
- **Model initialization:** Creates correct LLM client

### Observer Pattern
- **Watchers:** Monitor file system changes (optional)
- **Logging:** Centralized event tracking

---

## Summary

**ARGO v9.0 follows a clean, layered architecture:**

1. **User interacts with UI** → Streamlit professional interface
2. **UI calls Core modules** → Bootstrap, RAG, Router, Database
3. **Core processes requests** → Search, route, store
4. **External APIs queried** → OpenAI, Anthropic, Google Drive
5. **Results stored locally** → SQLite + ChromaDB
6. **Response returned to UI** → Formatted, with metadata
7. **User sees professional output** → Chat, sources, confidence, feedback

**Key strengths:**
- ✅ Single database (UnifiedDatabase)
- ✅ Intelligent routing (ModelRouter)
- ✅ Advanced RAG (HyDE + Reranking)
- ✅ Professional UI (No emojis, corporate CSS)
- ✅ Complete feature set (Conversations, Notes, Sources, Analytics)
- ✅ Clean architecture (Easy to extend)

**Current limitations:**
- Google Drive sync is placeholder (needs implementation)
- Web search not implemented
- Vision analysis not implemented
- Proactive suggestions not implemented

All data flows are logged, tracked, and stored for full transparency and auditability.
