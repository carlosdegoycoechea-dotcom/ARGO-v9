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
from core.conversation_summarizer import ConversationSummarizer
from core.streaming_manager import StreamingManager, StreamlitStreamingHelper
from core.memory_manager import MemoryManager
from tools.extractors import extract_and_chunk, get_file_info

logger = get_logger("UI")

# Page configuration
st.set_page_config(
    page_title="ARGO - Enterprise PMO Platform",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Claude Code Dark Theme - No white backgrounds anywhere
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Dark theme color palette - Claude Code inspired */
    :root {
        --bg-primary: #1a1a1a;
        --bg-secondary: #242424;
        --bg-tertiary: #2d2d2d;
        --border-color: #3d3d3d;
        --text-primary: #e0e0e0;
        --text-secondary: #b0b0b0;
        --text-tertiary: #808080;
        --accent-color: #667eea;
        --accent-hover: #7c3aed;
        --success: #48bb78;
        --warning: #ed8936;
        --error: #f56565;
    }

    /* Main app background - DARK */
    .main, .block-container {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Typography - Light text on dark */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        color: var(--text-primary) !important;
        background-color: var(--bg-primary) !important;
    }

    h1, h2, h3, h4, p, span, div {
        color: var(--text-primary) !important;
    }

    /* Sidebar styling - Dark */
    [data-testid="stSidebar"] {
        background-color: var(--bg-primary) !important;
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary) !important;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--bg-secondary) !important;
    }

    /* Buttons - Dark theme */
    .stButton > button {
        background-color: var(--accent-color) !important;
        color: white !important;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: var(--accent-hover) !important;
        transform: translateY(-1px);
    }

    /* Input fields - Dark */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border-radius: 6px;
        border: 1px solid var(--border-color);
        padding: 0.5rem 0.75rem;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color);
        background-color: var(--bg-secondary) !important;
    }

    /* Expander - Dark */
    .streamlit-expanderHeader {
        background-color: var(--bg-tertiary) !important;
        border-radius: 6px;
        border: 1px solid var(--border-color);
        font-weight: 500;
        color: var(--text-primary) !important;
    }

    /* Chat messages - DARK BACKGROUNDS */
    .stChatMessage {
        background-color: var(--bg-secondary) !important;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: var(--text-primary) !important;
    }

    /* Chat input - Dark, ALWAYS at bottom */
    [data-testid="stChatInput"] {
        background-color: var(--bg-tertiary) !important;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 0.75rem 1rem;
        position: sticky !important;
        bottom: 0 !important;
        z-index: 100 !important;
    }

    [data-testid="stChatInput"] input {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-color);
        background-color: var(--bg-secondary) !important;
    }

    /* Ensure proper spacing */
    .main .block-container {
        padding-bottom: 2rem;
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

# Auto-scroll chat to bottom
st.markdown("""
<script>
    // Auto-scroll to bottom of chat on page load and after new messages
    function scrollToBottom() {
        const chatContainer = window.parent.document.querySelector('.main');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Scroll on load
    window.addEventListener('load', scrollToBottom);

    // Scroll when DOM changes (new messages)
    const observer = new MutationObserver(scrollToBottom);
    const config = { childList: true, subtree: true };

    window.addEventListener('load', function() {
        const targetNode = window.parent.document.querySelector('.main');
        if (targetNode) {
            observer.observe(targetNode, config);
        }
    });

    // Immediate scroll
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 500);
</script>
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

# Initialize conversation summarizer (once per session)
if 'conversation_summarizer' not in st.session_state:
    from openai import OpenAI
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    st.session_state.conversation_summarizer = ConversationSummarizer(
        llm=llm,
        threshold=15,  # Trigger summarization after 15 messages
        max_summary_tokens=500
    )
    logger.info("ConversationSummarizer initialized")

conversation_summarizer = st.session_state.conversation_summarizer

# Initialize streaming manager (once per session)
if 'streaming_manager' not in st.session_state:
    st.session_state.streaming_manager = StreamingManager(chunk_size=1)
    logger.info("StreamingManager initialized")

streaming_manager = st.session_state.streaming_manager

# Initialize memory manager (once per session)
if 'memory_manager' not in st.session_state:
    st.session_state.memory_manager = MemoryManager(unified_db)
    logger.info("MemoryManager initialized")

memory_manager = st.session_state.memory_manager

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
            if enable_drive:
                drive_folder_id = st.text_input(
                    "Drive Folder ID",
                    placeholder="Enter the folder ID from Google Drive URL",
                    help="Example: 1aBcD3FgH5iJkLmN6oPqRsTuVwXyZ"
                )
            else:
                drive_folder_id = ""

            submit_button = st.form_submit_button("Create Project", use_container_width=True)

            if submit_button:
                if new_project_name:
                    # Check if project already exists
                    if new_project_name in project_names:
                        st.error(f"Project '{new_project_name}' already exists. Please choose a different name.")
                    else:
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
                            st.error(f"Error creating project: {str(e)}")
                            logger.error(f"Project creation failed: {e}", exc_info=True)
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
                    # Check if this conversation is being renamed
                    rename_key = f"renaming_{conv['id']}"
                    is_renaming = st.session_state.get(rename_key, False)

                    if is_renaming:
                        # Show rename input
                        current_title = conv.get('title', '') or conv['session_id']
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            new_title = st.text_input(
                                "New title",
                                value=current_title,
                                key=f"rename_input_{conv['id']}",
                                label_visibility="collapsed"
                            )
                        with col2:
                            if st.button("Save", key=f"save_rename_{conv['id']}"):
                                try:
                                    unified_db.update_conversation_title(conv['id'], new_title)
                                    st.session_state[rename_key] = False
                                    st.success("Renamed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    else:
                        # Normal display with load, rename, and delete buttons
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            # Show title if available, otherwise session_id
                            display_title = conv.get('title', None)
                            if not display_title or display_title.strip() == '':
                                session_label = conv['session_id'].split('_')[-1] if '_' in conv['session_id'] else conv['session_id'][:8]
                                display_title = f"Session {session_label}"

                            if st.button(display_title, key=f"load_{conv['id']}", use_container_width=True):
                                loaded_messages = unified_db.load_conversation(
                                    project_id=project['id'],
                                    session_id=conv['session_id']
                                )
                                if loaded_messages:
                                    st.session_state.messages = loaded_messages
                                    st.session_state.session_id = conv['session_id']
                                    st.rerun()
                        with col2:
                            if st.button("R", key=f"rename_{conv['id']}"):
                                st.session_state[rename_key] = True
                                st.rerun()
                        with col3:
                            if st.button("X", key=f"del_conv_{conv['id']}"):
                                try:
                                    unified_db.delete_conversation(conv['id'])
                                    st.success("Deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
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
        st.caption("Web Search")
        enable_web_search = st.checkbox(
            "Enable Web Search",
            value=True,
            help="Automatically search web for current information"
        )

        if enable_web_search:
            web_provider = st.selectbox(
                "Search Provider",
                ["duckduckgo", "serper", "brave", "tavily"],
                help="DuckDuckGo is free (no API key). Others need API keys in .env"
            )
        else:
            web_provider = "duckduckgo"

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

        st.divider()
        st.caption("Conversation Management")

        # Display current message count
        current_msg_count = len(st.session_state.messages)
        needs_compression = conversation_summarizer.needs_summary(current_msg_count)

        st.metric(
            "Messages in History",
            current_msg_count,
            delta="Needs compression" if needs_compression else "Normal",
            delta_color="normal" if not needs_compression else "off"
        )

        summarization_threshold = st.slider(
            "Auto-compress after N messages",
            min_value=10,
            max_value=30,
            value=15,
            help="Automatically summarize conversations longer than this to prevent token limits"
        )

        # Update threshold if changed
        if conversation_summarizer.threshold != summarization_threshold:
            conversation_summarizer.threshold = summarization_threshold
            logger.info(f"Summarization threshold updated to {summarization_threshold}")

        st.divider()
        st.caption("Response Display")

        enable_streaming = st.checkbox(
            "Enable Streaming Responses",
            value=True,
            help="Show responses word-by-word in real-time (like ChatGPT)"
        )

        if not enable_streaming:
            st.info("Responses will appear all at once after processing")

        st.session_state.search_settings = {
            'use_hyde': use_hyde,
            'use_reranker': use_reranker,
            'include_library': include_library,
            'override_provider': override_provider,
            'enable_web_search': enable_web_search,
            'web_provider': web_provider,
            'enable_streaming': enable_streaming
        }

    st.divider()

    # ==================== SYSTEM MONITOR ====================
    try:
        st.subheader("System Monitor")

        # Project size
        try:
            # Get project path - construct if not directly available
            if 'path' in project and project['path']:
                project_path = Path(project['path'])
            else:
                # Construct from base_path if available
                base_path = Path(project.get('base_path', 'projects'))
                project_path = base_path / project['id']

            if project_path.exists():
                total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
            else:
                size_mb = 0.0
        except Exception as e:
            logger.warning(f"Could not calculate project size: {e}")
            size_mb = 0.0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Project Size", f"{size_mb:.1f} MB")
        with col2:
            files_count = len(unified_db.get_files(project_id=project['id']))
            st.metric("Documents", files_count)

        # Feedback statistics
        try:
            feedback_stats = unified_db.get_feedback_stats(project_id=project['id'])
            if feedback_stats.get('total', 0) > 0:
                st.divider()
                st.caption("User Feedback")

                col1, col2 = st.columns(2)
                with col1:
                    helpful_pct = (feedback_stats.get('helpful', 0) / feedback_stats['total'] * 100) if feedback_stats['total'] > 0 else 0
                    st.metric("Helpful", f"{helpful_pct:.0f}%")
                with col2:
                    st.metric("Total Feedback", feedback_stats['total'])
        except Exception as e:
            logger.warning(f"Feedback stats error: {e}")

    except Exception as e:
        logger.warning(f"System monitor error: {e}")

# ====================
# MAIN AREA
# ====================

st.title("ARGO Enterprise PMO Platform")
st.caption("Professional project management and knowledge assistance")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Chat", "Documents", "Analytics", "Conversations & Notes", "Project"])

# ==================== TAB 1: CHAT ====================
with tab1:
    # Show current project at the top
    st.subheader(f"{project['name']}")
    st.caption(f"Project Assistant • {project['project_type'].title()}")
    st.divider()

    # Display message history
    for idx, msg in enumerate(st.session_state.messages):
        # No avatars/emojis - clean text only
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

                # Extract metadata
                metadata = msg.get('metadata', {})
                sources = ", ".join(metadata.get('sources', [])) if metadata.get('sources') else None
                confidence = metadata.get('confidence')

                with col1:
                    if st.button("Helpful", key=f"up_{idx}"):
                        # Save positive feedback
                        try:
                            memory_manager.save_feedback(
                                project_id=project['id'],
                                session_id=st.session_state.session_id,
                                query=prev_query,
                                response=msg['content'],
                                rating=1,  # Helpful
                                sources=sources,
                                confidence=confidence
                            )
                            # Mark as recorded to prevent duplicate feedback
                            msg['feedback_recorded'] = True
                            st.success("Thank you for your feedback!")
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Failed to save feedback: {e}")
                            st.error("Failed to save feedback")

                with col2:
                    if st.button("Not Helpful", key=f"down_{idx}"):
                        # Save negative feedback
                        try:
                            memory_manager.save_feedback(
                                project_id=project['id'],
                                session_id=st.session_state.session_id,
                                query=prev_query,
                                response=msg['content'],
                                rating=-1,  # Not helpful
                                sources=sources,
                                confidence=confidence
                            )
                            # Mark as recorded
                            msg['feedback_recorded'] = True
                            st.info("Feedback recorded. We'll improve!")
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Failed to save feedback: {e}")
                            st.error("Failed to save feedback")

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

                    # Web search (ONLY if enabled and query needs current info)
                    web_context = ""
                    if search_settings.get('enable_web_search', False):
                        try:
                            from core.web_search import WebSearchEngine, should_use_web_search

                            # Only search if query indicates need for web info
                            if should_use_web_search(prompt):
                                try:
                                    web_engine = WebSearchEngine(
                                        provider=search_settings.get('web_provider', 'duckduckgo')
                                    )
                                    logger.info(f"Query requires web search - using provider: {search_settings.get('web_provider')}")

                                    web_results = web_engine.search(prompt, count=5)

                                    if web_results and len(web_results) > 0:
                                        web_context = web_engine.format_results_for_context(web_results)
                                        st.success(f"Web search: {len(web_results)} results")
                                        logger.info(f"Web search returned {len(web_results)} results")
                                    else:
                                        logger.info("Web search returned no results")
                                except Exception as e:
                                    logger.error(f"Web search failed: {e}", exc_info=True)
                            else:
                                logger.debug("Query does not require web search - using project documents only")
                        except ImportError as e:
                            logger.warning(f"WebSearchEngine not available: {e}")

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

                    # Format context (combine RAG + Web)
                    rag_context = rag_engine.format_context(results)

                    if web_context:
                        context = f"{rag_context}\n\n{web_context}"
                    else:
                        context = rag_context

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

                    # Prepare conversation history with automatic summarization
                    # This prevents token limit errors in long conversations
                    conversation_history = st.session_state.messages[:-1]  # Exclude current user message

                    if conversation_summarizer.needs_summary(len(conversation_history)):
                        # Compress long conversation history
                        summary, compressed_history = conversation_summarizer.compress_history(
                            messages=conversation_history,
                            keep_recent=6  # Keep last 6 messages intact
                        )
                        history_for_llm = compressed_history
                        logger.info(f"Conversation compressed: {len(conversation_history)} → {len(compressed_history)} messages")

                        # Show compression notification to user
                        compression_stats = conversation_summarizer.get_compression_stats(
                            conversation_history,
                            compressed_history
                        )
                        st.info(f"Long conversation detected. Compressed {compression_stats['original_message_count']} messages "
                                f"to {compression_stats['compressed_message_count']} "
                                f"(saved {compression_stats['compression_ratio']:.0f}% tokens)")
                    else:
                        history_for_llm = conversation_history

                    # Build messages array: system prompt + conversation history + current question
                    messages = [{"role": "system", "content": system_prompt}]
                    messages.extend(history_for_llm)
                    messages.append({"role": "user", "content": prompt})

                    # Determine provider to use
                    override_provider = search_settings.get('override_provider')

                    # Check if streaming is enabled
                    enable_streaming = search_settings.get('enable_streaming', True)

                    if enable_streaming:
                        # STREAMING MODE: Show responses word-by-word
                        placeholder = st.empty()
                        full_response = ""

                        try:
                            # Determine which API to use
                            if override_provider == "anthropic":
                                # Use Anthropic streaming
                                from anthropic import Anthropic
                                anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

                                stream_gen = streaming_manager.stream_anthropic(
                                    client=anthropic_client,
                                    messages=messages,
                                    model="claude-3-5-sonnet-20241022",
                                    max_tokens=4096
                                )
                            else:
                                # Use OpenAI streaming (default or explicit)
                                from openai import OpenAI
                                openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                                stream_gen = streaming_manager.stream_openai(
                                    client=openai_client,
                                    messages=messages,
                                    model="gpt-4o"
                                )

                            # Stream to placeholder
                            full_response = StreamlitStreamingHelper.stream_to_placeholder(
                                streaming_manager=streaming_manager,
                                stream_generator=stream_gen,
                                placeholder=placeholder,
                                delay=0.01  # Small delay for visual effect
                            )

                        except Exception as e:
                            logger.error(f"Streaming failed: {e}", exc_info=True)
                            placeholder.error(f"Streaming error: {e}")
                            full_response = "[Error during streaming]"

                        response_content = full_response

                    else:
                        # NON-STREAMING MODE: Traditional all-at-once response
                        response = model_router.run(
                            task_type="chat",
                            project_id=project['id'],
                            messages=messages,
                            override_provider=override_provider
                        )

                        # Display response
                        st.markdown(response.content)
                        response_content = response.content

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
                        'content': response_content
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
    st.subheader(f"{project['name']} - Documents")
    st.caption(f"Project Assistant • {project['project_type'].title()}")
    st.divider()

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
    st.subheader(f"{project['name']} - Analytics")
    st.caption(f"Project Assistant • {project['project_type'].title()}")
    st.divider()

    try:
        from app.panels.analytics_panel import render_analytics_panel
        render_analytics_panel(unified_db, config)
    except ImportError:

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

# ==================== TAB 4: CONVERSATIONS & NOTES ====================
with tab4:
    st.subheader(f"{project['name']} - Conversations & Notes")
    st.caption(f"Project Assistant • {project['project_type'].title()}")
    st.divider()

    try:
        all_conversations = unified_db.list_conversations(project_id=project['id'], limit=50)

        if all_conversations:
            for conv in all_conversations:
                # Get conversation display title
                display_title = conv.get('title', None)
                if not display_title or display_title.strip() == '':
                    session_label = conv['session_id'].split('_')[-1] if '_' in conv['session_id'] else conv['session_id'][:12]
                    display_title = f"Session {session_label}"

                created = conv.get('started_at', 'Unknown')
                message_count = conv.get('message_count', 0)

                # Check if this conversation is being renamed
                rename_key = f"renaming_tab4_{conv['id']}"
                is_renaming = st.session_state.get(rename_key, False)

                with st.expander(f"{display_title} • {created} • {message_count} messages"):
                    if is_renaming:
                        # Rename mode
                        st.write("**Rename Conversation**")
                        current_title = conv.get('title', '') or conv['session_id']
                        col1, col2, col3 = st.columns([4, 1, 1])
                        with col1:
                            new_title = st.text_input(
                                "New title",
                                value=current_title,
                                key=f"rename_input_tab4_{conv['id']}",
                                label_visibility="collapsed"
                            )
                        with col2:
                            if st.button("Save", key=f"save_rename_tab4_{conv['id']}"):
                                try:
                                    unified_db.update_conversation_title(conv['id'], new_title)
                                    st.session_state[rename_key] = False
                                    st.success("Renamed successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        with col3:
                            if st.button("Cancel", key=f"cancel_rename_tab4_{conv['id']}"):
                                st.session_state[rename_key] = False
                                st.rerun()
                    else:
                        # Normal mode - show conversation info and actions
                        if conv.get('summary'):
                            st.info(f"**Summary:** {conv['summary']}")

                        col1, col2, col3 = st.columns([2, 2, 2])

                        with col1:
                            if st.button("Load", key=f"load_full_{conv['id']}", use_container_width=True):
                                loaded_messages = unified_db.load_conversation(
                                    project_id=project['id'],
                                    session_id=conv['session_id']
                                )
                                if loaded_messages:
                                    st.session_state.messages = loaded_messages
                                    st.session_state.session_id = conv['session_id']
                                    st.success("Conversation loaded! Check the Chat tab.")
                                    st.rerun()
                                else:
                                    st.warning("No messages found")

                        with col2:
                            if st.button("Rename", key=f"rename_full_{conv['id']}", use_container_width=True):
                                st.session_state[rename_key] = True
                                st.rerun()

                        with col3:
                            if st.button("Delete", key=f"del_full_{conv['id']}", use_container_width=True):
                                try:
                                    unified_db.delete_conversation(conv['id'])
                                    st.success("Conversation deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting: {e}")
        else:
            st.info("No saved conversations yet. Start chatting to create your first conversation!")

    except Exception as e:
        st.error(f"Error loading conversations: {e}")
        logger.error(f"Tab 4 conversation error: {e}", exc_info=True)

# ==================== TAB 5: PROJECT ====================
with tab5:
    st.subheader(f"{project['name']} - Project Settings")
    st.caption(f"Project Assistant • {project['project_type'].title()}")
    st.divider()

    # ==================== PROJECT INFO ====================
    st.write("### Basic Information")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Project Name", project['name'])
        st.metric("Project Type", project['project_type'].title())
        st.metric("Status", project['status'].title())

    with col2:
        created_at = project.get('created_at', 'Unknown')
        st.metric("Created", created_at)

        # Count documents and chunks
        try:
            files = unified_db.get_files(project_id=project['id'])
            doc_count = len(files)

            # Count total chunks
            chunk_count = 0
            for file in files:
                chunk_count += file.get('chunk_count', 0)

            st.metric("Documents", doc_count)
            st.metric("Chunks", chunk_count)
        except Exception as e:
            logger.warning(f"Could not count docs/chunks: {e}")
            st.metric("Documents", "N/A")
            st.metric("Chunks", "N/A")

    st.divider()

    # ==================== GOOGLE DRIVE ====================
    st.write("### Google Drive Integration")

    # Get current metadata (now pre-parsed from database)
    metadata = project.get('metadata', {})
    drive_enabled = metadata.get('drive_enabled', False)
    current_drive_id = metadata.get('drive_folder_id', '')

    # Show current status
    col1, col2 = st.columns([2, 1])
    with col1:
        if drive_enabled and current_drive_id:
            st.success(f"Drive sync enabled: {current_drive_id}")
        else:
            st.info("Drive sync not configured")

    with col2:
        sync_status = metadata.get('sync_status', 'Not synced')
        last_sync = metadata.get('last_sync', 'Never')
        st.caption(f"Status: {sync_status}")
        st.caption(f"Last sync: {last_sync}")

    # Edit Drive configuration
    with st.expander("Configure Google Drive"):
        with st.form("drive_config_form"):
            enable_sync = st.checkbox("Enable Drive sync", value=drive_enabled)
            new_drive_id = st.text_input(
                "Drive Folder ID",
                value=current_drive_id,
                placeholder="Enter folder ID from Google Drive URL",
                help="Example: 1aBcD3FgH5iJkLmN6oPqRsTuVwXyZ"
            )

            if st.form_submit_button("Save Drive Configuration", use_container_width=True):
                try:
                    new_metadata = metadata.copy()
                    new_metadata['drive_enabled'] = enable_sync
                    new_metadata['drive_folder_id'] = new_drive_id if enable_sync else ''

                    unified_db.update_project(
                        project_id=project['id'],
                        metadata=new_metadata
                    )
                    st.success("Drive configuration updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating Drive config: {e}")
                    logger.error(f"Drive config update failed: {e}", exc_info=True)

    # Force sync button
    if drive_enabled and current_drive_id:
        if st.button("Force Synchronization", use_container_width=True):
            try:
                # Import and run drive sync
                from core.drive_manager import DriveManager
                drive_manager = DriveManager(credentials_path='config/google_credentials.json')

                st.info("Starting synchronization...")

                # Sync files
                files = drive_manager.sync_folder(
                    folder_id=current_drive_id,
                    project_id=project['id']
                )

                # Update metadata
                new_metadata = metadata.copy()
                new_metadata['sync_status'] = 'Synced'
                new_metadata['last_sync'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                unified_db.update_project(project_id=project['id'], metadata=new_metadata)

                st.success(f"Synchronized {len(files)} files successfully!")
                st.rerun()
            except ImportError:
                st.warning("Drive sync not available - DriveManager module not found")
            except Exception as e:
                st.error(f"Synchronization failed: {e}")
                logger.error(f"Drive sync failed: {e}", exc_info=True)

    st.divider()

    # ==================== EDIT PROJECT ====================
    st.write("### Edit Project")

    with st.expander("Edit Project Details"):
        with st.form("edit_project_form"):
            new_desc = st.text_area(
                "Description",
                value=project.get('description', ''),
                placeholder="Project description"
            )
            new_status = st.selectbox(
                "Status",
                options=['active', 'archived', 'completed'],
                index=['active', 'archived', 'completed'].index(project['status']) if project['status'] in ['active', 'archived', 'completed'] else 0
            )

            if st.form_submit_button("Save Changes", use_container_width=True):
                try:
                    unified_db.update_project(
                        project_id=project['id'],
                        description=new_desc,
                        status=new_status
                    )
                    st.success("Project updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating project: {e}")
                    logger.error(f"Project update failed: {e}", exc_info=True)

    st.divider()

    # ==================== DANGER ZONE ====================
    st.write("### Danger Zone")

    with st.expander("Delete Project", expanded=False):
        st.warning("This action cannot be undone. All project data, documents, conversations, and embeddings will be permanently deleted.")

        # Two-step confirmation
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False

        if not st.session_state.confirm_delete:
            if st.button("I want to delete this project", type="secondary"):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            st.error("Are you absolutely sure? This cannot be undone!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, DELETE permanently", type="primary"):
                    try:
                        # Delete project
                        unified_db.delete_project(project['id'])
                        st.success("Project deleted successfully")

                        # Clear session state
                        st.session_state.clear()

                        # Reload page
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting project: {e}")
                        logger.error(f"Project deletion failed: {e}", exc_info=True)

            with col2:
                if st.button("Cancel", type="secondary"):
                    st.session_state.confirm_delete = False
                    st.rerun()

# Footer
st.divider()
st.caption(f"{config.version_display} | Professional Project Management System")
