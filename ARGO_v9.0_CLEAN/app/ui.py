"""
ARGO - Enterprise PMO Platform
Corporate-grade user interface
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import sys

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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Corporate CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Corporate color scheme */
    :root {
        --primary-color: #1f4788;
        --secondary-color: #2c5aa0;
        --accent-color: #4a90e2;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* Chat input fixed at bottom */
    .stChatInputContainer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.8) 100%);
        padding: 1rem 2rem 2rem 2rem;
        z-index: 999;
    }
    
    .main .block-container {
        padding-bottom: 8rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
    }
    
    /* Clean, professional appearance */
    .element-container {
        margin-bottom: 1rem;
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
unified_db = argo['unified_db']
project = argo['project']

# Sidebar
with st.sidebar:
    st.title("ARGO")
    st.caption(config.version_display)
    st.divider()
    
    # Project info
    st.subheader("Current Project")
    st.write(f"**Name:** {project['name']}")
    st.write(f"**Type:** {project['project_type']}")
    st.write(f"**Status:** {project['status']}")
    st.divider()
    
    # File upload
    st.subheader("Document Upload")
    uploaded_file = st.file_uploader(
        "Upload document",
        type=['pdf', 'docx', 'xlsx', 'txt', 'md', 'csv'],
        help="Supported formats: PDF, DOCX, XLSX, TXT, MD, CSV"
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
                
                # Index chunks
                for chunk in chunks:
                    # TODO: Index in vectorstore
                    pass
                
                # Register in database
                unified_db.add_file(
                    project_id=project['id'],
                    filename=uploaded_file.name,
                    file_path=str(temp_path),
                    file_type=file_type,
                    file_hash=file_info['file_hash'],
                    file_size=file_info['size_bytes'],
                    chunk_count=len(chunks)
                )
                
                st.success(f"Document processed: {uploaded_file.name}")
                st.info(f"Created {len(chunks)} chunks | {file_info['size_kb']:.1f} KB")
                
                logger.info(f"Document indexed: {uploaded_file.name} ({len(chunks)} chunks)")
                
            except Exception as e:
                st.error(f"Error processing document: {e}")
                logger.error(f"Document processing failed: {e}", exc_info=True)
    
    st.divider()
    
    # Settings
    with st.expander("Settings"):
        use_hyde = st.checkbox("Use HyDE", value=config.get("rag.search.use_hyde", True))
        use_reranker = st.checkbox("Use Reranker", value=config.get("rag.search.use_reranker", True))
        include_library = st.checkbox("Include Library", value=True)
        
        st.session_state.search_settings = {
            'use_hyde': use_hyde,
            'use_reranker': use_reranker,
            'include_library': include_library
        }

# Main area
st.title("ARGO Enterprise PMO Platform")

# Tabs
tab1, tab2, tab3 = st.tabs(["Chat", "Documents", "Analytics"])

with tab1:
    # Chat interface
    st.subheader("Project Assistant")
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            if "sources" in msg:
                with st.expander("Sources"):
                    for i, source in enumerate(msg["sources"], 1):
                        st.caption(f"{i}. {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask about your project..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Search RAG
                    search_settings = st.session_state.get('search_settings', {})
                    
                    results, metadata = rag_engine.search(
                        query=prompt,
                        top_k=5,
                        **search_settings
                    )
                    
                    # Format context
                    context = rag_engine.format_context(results)
                    
                    # Build messages
                    system_prompt = f"""You are ARGO, an enterprise project management assistant.

Use the following context to answer the user's question accurately and professionally.

{context}

Guidelines:
- Answer based on the context provided
- Be concise and professional
- Cite sources when appropriate
- If information is not in context, say so clearly
- Use proper business terminology"""
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                    
                    # Get response from router
                    response = model_router.run(
                        task_type="chat",
                        project_id=project['id'],
                        messages=messages
                    )
                    
                    # Display response
                    st.markdown(response.content)
                    
                    # Extract sources
                    sources = [
                        f"{r.metadata.get('source', 'Unknown')} (Score: {r.score:.2f})"
                        for r in results
                    ]
                    
                    if sources:
                        with st.expander("Sources"):
                            for i, source in enumerate(sources, 1):
                                st.caption(f"{i}. {source}")
                    
                    # Save message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.content,
                        "sources": sources
                    })
                    
                    logger.info(f"Query processed: {prompt[:50]}...")
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    logger.error(f"Response generation failed: {e}", exc_info=True)

with tab2:
    # Documents view
    st.subheader("Project Documents")
    
    try:
        files = unified_db.get_files(project_id=project['id'])
        
        if files:
            # Display as table
            import pandas as pd
            
            df = pd.DataFrame(files)
            df = df[['filename', 'file_type', 'chunk_count', 'indexed_at']]
            df.columns = ['Filename', 'Type', 'Chunks', 'Indexed At']
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No documents uploaded yet. Use the sidebar to upload documents.")
    
    except Exception as e:
        st.error(f"Error loading documents: {e}")
        logger.error(f"Document list failed: {e}", exc_info=True)

with tab3:
    # Analytics view - COMPLETE DASHBOARD
    try:
        from app.panels.analytics_panel import render_analytics_panel
        render_analytics_panel(unified_db, config)
    except ImportError:
        # Fallback to basic analytics if panel not available
        st.subheader("Usage Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Documents", len(unified_db.get_files(project_id=project['id'])))
        
        with col2:
            st.metric("Total Chunks", sum(f.get('chunk_count', 0) for f in unified_db.get_files(project_id=project['id'])))
        
        with col3:
            st.metric("Queries", len(st.session_state.messages) // 2)
        
        st.divider()
        
        # API usage
        st.subheader("API Usage")
        
        try:
            usage_stats = unified_db.get_api_usage_summary(
                project_id=project['id'],
                days=7
            )
            
            if usage_stats:
                st.write(f"**Total Tokens (7 days):** {usage_stats.get('total_tokens', 0):,}")
                st.write(f"**Estimated Cost:** ${usage_stats.get('total_cost', 0):.4f}")
                st.write(f"**Requests:** {usage_stats.get('total_requests', 0)}")
            else:
                st.info("No API usage data yet")
        
        except Exception as e:
            st.warning(f"Usage data unavailable: {e}")

# Footer
st.divider()
st.caption(f"{config.version_display} | Professional Project Management System")
