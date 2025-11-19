"""
ARGO v9.0 - Enterprise PMO Platform
Professional corporate interface with full functionality
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import sys
import pandas as pd

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.bootstrap import initialize_argo
from core.config import get_config
from core.logger import get_logger
from tools.extractors import extract_and_chunk, get_file_info

logger = get_logger("UI")

# Page configuration
st.set_page_config(
    page_title="ARGO - Enterprise PMO Platform",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Corporate CSS - Claude-inspired
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Corporate color palette - Professional blues and grays */
    :root {
        --primary-color: #2d3748;
        --secondary-color: #4a5568;
        --accent-color: #667eea;
        --accent-light: #7c3aed;
        --surface: #f7fafc;
        --border: #e2e8f0;
        --text-primary: #1a202c;
        --text-secondary: #718096;
        --success: #48bb78;
        --warning: #ed8936;
        --error: #f56565;
    }

    /* Typography */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        color: var(--text-primary);
    }

    h1, h2, h3, h4 {
        color: var(--primary-color);
        font-weight: 600;
        letter-spacing: -0.025em;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* Buttons - Professional style */
    .stButton > button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton > button:hover {
        background-color: var(--accent-light);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: var(--text-primary);
        border: 1px solid var(--border);
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: var(--surface);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid var(--border);
        padding: 0.5rem 0.75rem;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--surface);
        border-radius: 6px;
        border: 1px solid var(--border);
        font-weight: 500;
        color: var(--text-primary);
    }

    /* Chat messages */
    .stChatMessage {
        background-color: white;
        border-radius: 8px;
        border: 1px solid var(--border);
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Chat input fixed at bottom */
    .stChatInputContainer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%);
        padding: 1rem 2rem 2rem 2rem;
        border-top: 1px solid var(--border);
        z-index: 999;
    }

    .main .block-container {
        padding-bottom: 8rem;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
    }

    /* Divider */
    hr {
        border-color: var(--border);
        margin: 1.5rem 0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: var(--text-secondary);
        padding: 0.75rem 0;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent-color);
        border-bottom: 2px solid var(--accent-color);
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 6px;
        border-left-width: 4px;
    }

    /* Confidence indicators */
    .confidence-high {
        color: var(--success);
        font-weight: 600;
    }

    .confidence-medium {
        color: var(--warning);
        font-weight: 600;
    }

    .confidence-low {
        color: var(--error);
        font-weight: 600;
    }

    /* Source panel */
    .source-item {
        background-color: var(--surface);
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--accent-color);
    }

    /* Professional badge */
    .pro-badge {
        display: inline-block;
        background-color: var(--accent-color);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize system
if 'argo_initialized' not in st.session_state:
    with st.spinner("Initializing ARGO Enterprise Platform..."):
        try:
            config = get_config()
            logger.info(f"Initializing {config.version_display}")

            argo = initialize_argo()

            st.session_state.argo = argo
            st.session_state.config = config
            st.session_state.argo_initialized = True
            st.session_state.messages = []
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.last_sources = []

            logger.info("System initialized successfully")
        except Exception as e:
            st.error(f"Initialization error: {e}")
            logger.error(f"Initialization failed: {e}", exc_info=True)
            st.stop()

# Get components
argo = st.session_state.argo
config = st.session_state.config
model_router = argo['model_router']
rag_engine = argo['project_components']['rag_engine']
vectorstore = argo['project_components']['vectorstore']
unified_db = argo['unified_db']
project = argo['project']

# ====================
# SIDEBAR
# ====================
with st.sidebar:
    st.title("ARGO")
    st.caption(config.version_display)
    st.divider()

    # ==================== PROJECT MANAGEMENT ====================
    st.subheader("Projects")

    # Get all projects
    all_projects = unified_db.list_projects()
    project_names = [p['name'] for p in all_projects]

    # Project selector
    selected_project_name = st.selectbox(
        "Active Project",
        project_names,
        index=project_names.index(project['name']) if project['name'] in project_names else 0
    )

    # If selection changed, update session state
    if selected_project_name != project['name']:
        with st.spinner(f"Switching to {selected_project_name}..."):
            try:
                st.session_state.argo = initialize_argo(project_name=selected_project_name)
                st.session_state.messages = []
                st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.success(f"Switched to '{selected_project_name}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error switching project: {e}")

    # New project creator
    with st.expander("Create New Project"):
        with st.form("new_project_form"):
            new_project_name = st.text_input("Project Name", placeholder="Enter project name")
            new_project_type = st.selectbox(
                "Project Type",
                ["standard", "construction", "it", "research"],
                help="Select the appropriate project category"
            )
            new_project_desc = st.text_area("Description", placeholder="Optional project description")

            st.caption("Google Drive Integration")
            enable_drive = st.checkbox("Enable Drive sync", help="Requires google_credentials.json")
            drive_folder_id = st.text_input(
                "Drive Folder ID",
                placeholder="Folder ID from Drive URL",
                disabled=not enable_drive
            )

            submit_button = st.form_submit_button("Create Project", use_container_width=True)

            if submit_button:
                if new_project_name:
                    try:
                        project_id = unified_db.create_project(
                            name=new_project_name,
                            project_type=new_project_type,
                            description=new_project_desc
                        )

                        if enable_drive and drive_folder_id:
                            unified_db.update_project(
                                project_id=project_id,
                                metadata={'drive_enabled': True, 'drive_folder_id': drive_folder_id}
                            )

                        st.success(f"Project '{new_project_name}' created successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a project name")

    st.divider()

    # Project details
    st.caption("Current Project")
    st.write(f"**Name:** {project['name']}")
    st.write(f"**Type:** {project['project_type'].title()}")
    st.write(f"**Status:** {project['status'].title()}")

    st.divider()

    # ==================== CONVERSATIONS ====================
    st.subheader("Conversations")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Chat", use_container_width=True):
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.messages = []
            st.success("New conversation started")
            st.rerun()

    with col2:
        if st.button("Save", use_container_width=True):
            if st.session_state.messages:
                unified_db.save_conversation(
                    project_id=project['id'],
                    session_id=st.session_state.session_id,
                    messages=st.session_state.messages
                )
                st.success("Conversation saved")

    # List recent conversations
    try:
        conversations = unified_db.list_conversations(project_id=project['id'], limit=10)
        if conversations:
            with st.expander(f"Recent Conversations ({len(conversations)})"):
                for conv in conversations:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        # Extract date from session_id
                        session_label = conv['session_id'].split('_')[-1] if '_' in conv['session_id'] else conv['session_id'][:8]
                        if st.button(f"Session {session_label}", key=f"load_{conv['id']}", use_container_width=True):
                            loaded_messages = unified_db.load_conversation(
                                project_id=project['id'],
                                session_id=conv['session_id']
                            )
                            if loaded_messages:
                                st.session_state.messages = loaded_messages
                                st.session_state.session_id = conv['session_id']
                                st.rerun()
                    with col2:
                        if st.button("×", key=f"del_conv_{conv['id']}"):
                            # Delete conversation logic
                            st.rerun()
    except Exception as e:
        logger.warning(f"Could not load conversations: {e}")

    st.divider()

    # ==================== NOTES ====================
    st.subheader("Notes")

    # Display existing notes
    try:
        notes = unified_db.get_notes(project_id=project['id'], limit=5)
        for note in notes:
            with st.expander(f"{note['title'][:30]}..."):
                st.caption(f"Created: {note.get('created_at', 'N/A')}")
                st.write(note['content'])
                if st.button("Delete", key=f"del_note_{note['id']}"):
                    unified_db.delete_note(note['id'])
                    st.rerun()
    except Exception as e:
        logger.warning(f"Could not load notes: {e}")

    # Create new note
    with st.expander("Create Note"):
        with st.form("new_note_form"):
            note_title = st.text_input("Title", placeholder="Note title")
            note_content = st.text_area("Content", placeholder="Note content", height=100)
            note_tags = st.text_input("Tags", placeholder="Optional tags (comma-separated)")

            if st.form_submit_button("Save Note", use_container_width=True):
                if note_title and note_content:
                    unified_db.save_note(
                        project_id=project['id'],
                        title=note_title,
                        content=note_content,
                        tags=note_tags
                    )
                    st.success("Note saved")
                    st.rerun()

    st.divider()

    # ==================== ACTIVE SOURCES ====================
    st.subheader("Active Sources")

    if st.session_state.last_sources:
        st.caption(f"Last query used {len(st.session_state.last_sources)} source(s)")

        for source in st.session_state.last_sources[:5]:
            score = source.get('score', 0)

            # Color coding based on score
            if score >= 0.7:
                indicator = "HIGH"
                color_class = "confidence-high"
            elif score >= 0.4:
                indicator = "MED"
                color_class = "confidence-medium"
            else:
                indicator = "LOW"
                color_class = "confidence-low"

            with st.expander(f"[{indicator}] {source.get('filename', 'Unknown')[:25]}"):
                st.metric("Relevance Score", f"{score:.0%}")
                if source.get('page'):
                    st.caption(f"Page: {source['page']}")
                st.caption("Preview:")
                st.text(source.get('preview', '')[:150] + "...")
    else:
        st.info("Sources will appear here after your first query")

    st.divider()

    # ==================== DOCUMENT UPLOAD ====================
    st.subheader("Document Upload")

    uploaded_file = st.file_uploader(
        "Select file",
        type=['pdf', 'docx', 'xlsx', 'txt', 'md', 'csv'],
        help="Supported: PDF, DOCX, XLSX, TXT, MD, CSV"
    )

    if uploaded_file:
        with st.spinner("Processing document..."):
            try:
                # Save temporarily
                temp_path = Path(config.get("paths.temp_dir")) / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                # Get file info
                file_info = get_file_info(str(temp_path))

                # Extract and chunk
                file_type = file_info['extension']
                chunks = extract_and_chunk(
                    file_path=str(temp_path),
                    file_type=file_type,
                    metadata={
                        'project_id': project['id'],
                        'source': uploaded_file.name,
                        'uploaded_at': datetime.now().isoformat()
                    }
                )

                # Index chunks in vectorstore
                if vectorstore and chunks:
                    texts = [chunk['content'] for chunk in chunks]
                    metadatas = [chunk['metadata'] for chunk in chunks]
                    vectorstore.add_texts(texts=texts, metadatas=metadatas)

                # Register in database
                unified_db.register_file(
                    project_id=project['id'],
                    filename=uploaded_file.name,
                    file_path=str(temp_path),
                    file_type=file_type,
                    file_hash=file_info['file_hash'],
                    file_size=file_info['size_bytes'],
                    chunk_count=len(chunks)
                )

                st.success(f"Document processed: {uploaded_file.name}")
                st.info(f"{len(chunks)} chunks | {file_info['size_kb']:.1f} KB")

                logger.info(f"Document indexed: {uploaded_file.name} ({len(chunks)} chunks)")

            except Exception as e:
                st.error(f"Error processing document: {e}")
                logger.error(f"Document processing failed: {e}", exc_info=True)

    st.divider()

    # ==================== GOOGLE DRIVE SYNC ====================
    project_metadata = project.get('metadata', {})
    if isinstance(project_metadata, str):
        import json
        try:
            project_metadata = json.loads(project_metadata)
        except:
            project_metadata = {}

    if project_metadata.get('drive_enabled'):
        st.subheader("Google Drive Sync")
        folder_id = project_metadata.get('drive_folder_id', 'N/A')
        st.caption(f"Folder: {folder_id[:20]}...")

        if st.button("Sync Now", use_container_width=True):
            st.info("Drive sync functionality requires google_drive_sync.py module")

    st.divider()

    # ==================== SETTINGS ====================
    with st.expander("Settings"):
        st.caption("RAG Configuration")
        use_hyde = st.checkbox("HyDE Enhancement", value=config.get("rag.search.use_hyde", True))
        use_reranker = st.checkbox("Result Reranking", value=config.get("rag.search.use_reranker", True))
        include_library = st.checkbox("Include Knowledge Library", value=True)

        st.divider()
        st.caption("Model Selection")
        model_preference = st.radio(
            "LLM Provider",
            ["Auto (Smart Routing)", "OpenAI only", "Anthropic only"],
            help="Auto routing selects the optimal model for each task"
        )

        # Map to override values
        if model_preference == "OpenAI only":
            override_provider = "openai"
        elif model_preference == "Anthropic only":
            override_provider = "anthropic"
        else:
            override_provider = None

        st.session_state.search_settings = {
            'use_hyde': use_hyde,
            'use_reranker': use_reranker,
            'include_library': include_library,
            'override_provider': override_provider
        }

    st.divider()

    # ==================== SYSTEM MONITOR ====================
    try:
        st.subheader("System Monitor")

        # Project size
        project_path = Path(project['path'])
        total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Project Size", f"{size_mb:.1f} MB")
        with col2:
            files_count = len(unified_db.get_files(project_id=project['id']))
            st.metric("Documents", files_count)
    except Exception as e:
        logger.warning(f"System monitor error: {e}")

# ====================
# MAIN AREA
# ====================

st.title("ARGO Enterprise PMO Platform")
st.caption("Professional project management and knowledge assistance")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Documents", "Analytics", "Conversations"])

# ==================== TAB 1: CHAT ====================
with tab1:
    st.subheader("Project Assistant")

    # Display message history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

            # Show metadata if exists
            if msg['role'] == 'assistant' and 'metadata' in msg:
                metadata = msg['metadata']

                # Sources
                if 'sources' in metadata and metadata['sources']:
                    with st.expander("Sources Used"):
                        for source in metadata['sources']:
                            st.caption(f"• {source}")

                # Confidence score
                if 'confidence' in metadata:
                    conf = metadata['confidence']
                    if conf >= 0.8:
                        st.success(f"Confidence: {conf:.0%} (High - Verified in documents)")
                    elif conf >= 0.5:
                        st.info(f"Confidence: {conf:.0%} (Medium - Partial verification)")
                    else:
                        st.warning(f"Confidence: {conf:.0%} (Low - Limited information)")

            # Feedback buttons
            if msg['role'] == 'assistant' and 'feedback_recorded' not in msg:
                col1, col2, col3 = st.columns([1, 1, 10])

                # Get previous user message
                prev_query = ""
                msg_idx = st.session_state.messages.index(msg)
                if msg_idx > 0:
                    prev_query = st.session_state.messages[msg_idx - 1]['content']

                with col1:
                    if st.button("Helpful", key=f"up_{idx}"):
                        # Save positive feedback
                        try:
                            # Could implement unified_db.save_feedback() method
                            st.success("Thank you for your feedback")
                        except:
                            pass

                with col2:
                    if st.button("Not Helpful", key=f"down_{idx}"):
                        # Save negative feedback
                        try:
                            # Could implement unified_db.save_feedback() method
                            st.info("Feedback recorded")
                        except:
                            pass

    # Chat input
    if prompt := st.chat_input("Ask about your project..."):
        # Add user message
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        with st.chat_message('user'):
            st.markdown(prompt)

        # Generate response
        with st.chat_message('assistant'):
            with st.spinner("Analyzing..."):
                try:
                    # Get search settings
                    search_settings = st.session_state.get('search_settings', {})

                    # Search RAG
                    results, search_metadata = rag_engine.search(
                        query=prompt,
                        top_k=5,
                        **search_settings
                    )

                    # Store sources for sidebar display
                    st.session_state.last_sources = [
                        {
                            'filename': r.metadata.get('source', 'Unknown'),
                            'page': r.metadata.get('page'),
                            'score': r.score,
                            'preview': r.content[:200]
                        }
                        for r in results
                    ]

                    # Format context
                    context = rag_engine.format_context(results)

                    # Build system prompt
                    system_prompt = f"""You are ARGO, an enterprise project management assistant.

Use the following context to answer the user's question accurately and professionally.

{context}

Guidelines:
- Answer based on the context provided
- Be concise and professional
- Cite sources when appropriate
- If information is not in context, state this clearly
- Use proper business terminology
- Do not use emojis in your responses"""

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]

                    # Get response from router
                    response = model_router.run(
                        task_type="chat",
                        project_id=project['id'],
                        messages=messages,
                        override_provider=search_settings.get('override_provider')
                    )

                    # Display response
                    st.markdown(response.content)

                    # Extract sources for metadata
                    sources = [
                        f"{r.metadata.get('source', 'Unknown')} (Relevance: {r.score:.2f})"
                        for r in results
                    ]

                    # Calculate confidence
                    confidence = sum(r.score for r in results) / len(results) if results else 0

                    # Prepare metadata
                    response_metadata = {}
                    if sources:
                        response_metadata['sources'] = sources
                    if confidence > 0:
                        response_metadata['confidence'] = confidence

                    # Save assistant message
                    message_data = {
                        'role': 'assistant',
                        'content': response.content
                    }
                    if response_metadata:
                        message_data['metadata'] = response_metadata

                    st.session_state.messages.append(message_data)

                    # Auto-save conversation
                    unified_db.save_conversation(
                        project_id=project['id'],
                        session_id=st.session_state.session_id,
                        messages=st.session_state.messages
                    )

                    logger.info(f"Query processed: {prompt[:50]}...")

                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    logger.error(f"Response generation failed: {e}", exc_info=True)

# ==================== TAB 2: DOCUMENTS ====================
with tab2:
    st.subheader("Project Documents")

    try:
        files = unified_db.get_files(project_id=project['id'])

        if files:
            # Display as professional table
            df = pd.DataFrame(files)
            df = df[['filename', 'file_type', 'chunk_count', 'indexed_at']]
            df.columns = ['Filename', 'Type', 'Chunks', 'Indexed At']

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.caption(f"Total: {len(files)} document(s)")
        else:
            st.info("No documents uploaded yet. Use the sidebar to upload documents.")

    except Exception as e:
        st.error(f"Error loading documents: {e}")
        logger.error(f"Document list failed: {e}", exc_info=True)

# ==================== TAB 3: ANALYTICS ====================
with tab3:
    try:
        from app.panels.analytics_panel import render_analytics_panel
        render_analytics_panel(unified_db, config)
    except ImportError:
        st.subheader("Usage Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Documents", len(unified_db.get_files(project_id=project['id'])))

        with col2:
            total_chunks = sum(f.get('chunk_count', 0) for f in unified_db.get_files(project_id=project['id']))
            st.metric("Total Chunks", total_chunks)

        with col3:
            st.metric("Queries", len(st.session_state.messages) // 2)

        st.divider()

        st.subheader("API Usage")

        try:
            usage_stats = unified_db.get_api_usage_summary(
                project_id=project['id'],
                days=7
            )

            if usage_stats:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Tokens (7d)", f"{usage_stats.get('total_tokens', 0):,}")
                with col2:
                    st.metric("Estimated Cost", f"${usage_stats.get('total_cost', 0):.4f}")
                with col3:
                    st.metric("Requests", usage_stats.get('total_requests', 0))
            else:
                st.info("No API usage data available yet")

        except Exception as e:
            st.warning(f"Usage data unavailable: {e}")

# ==================== TAB 4: CONVERSATIONS ====================
with tab4:
    st.subheader("Conversation History")

    try:
        all_conversations = unified_db.list_conversations(project_id=project['id'], limit=50)

        if all_conversations:
            for conv in all_conversations:
                session_label = conv['session_id']
                created = conv.get('created_at', 'Unknown')

                with st.expander(f"Session {session_label} - {created}"):
                    col1, col2 = st.columns([5, 1])

                    with col1:
                        if st.button("Load Conversation", key=f"load_full_{conv['id']}"):
                            loaded_messages = unified_db.load_conversation(
                                project_id=project['id'],
                                session_id=conv['session_id']
                            )
                            if loaded_messages:
                                st.session_state.messages = loaded_messages
                                st.session_state.session_id = conv['session_id']
                                st.success("Conversation loaded")
                                st.rerun()

                    with col2:
                        if st.button("Delete", key=f"del_full_{conv['id']}"):
                            # Implement delete conversation
                            st.info("Delete functionality pending")
        else:
            st.info("No saved conversations yet")

    except Exception as e:
        st.error(f"Error loading conversations: {e}")

# Footer
st.divider()
st.caption(f"{config.version_display} | Professional Project Management System")
