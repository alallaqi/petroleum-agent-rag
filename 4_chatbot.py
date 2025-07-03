import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our existing search function and user manager
import importlib.util
import sys

# Load the 3_retrieval_system.py module
spec = importlib.util.spec_from_file_location("retrieval_system", "3_retrieval_system.py")
retrieval_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retrieval_module)

# Load the user_manager.py module
spec_user = importlib.util.spec_from_file_location("user_manager", "user_manager.py")
user_module = importlib.util.module_from_spec(spec_user)
spec_user.loader.exec_module(user_module)

# Load the language_translator.py module
spec_translator = importlib.util.spec_from_file_location("language_translator", "language_translator.py")
translator_module = importlib.util.module_from_spec(spec_translator)
spec_translator.loader.exec_module(translator_module)

# Get the search function, user manager, and language translator
search_function = getattr(retrieval_module, 'search_petroleum_knowledge')
UserManager = getattr(user_module, 'UserManager')
LanguageTranslator = getattr(translator_module, 'LanguageTranslator')

# Initialize user manager
if "user_manager" not in st.session_state:
    st.session_state.user_manager = UserManager()
user_manager = st.session_state.user_manager

# Initialize language translator
if "language_translator" not in st.session_state:
    st.session_state.language_translator = LanguageTranslator()
language_translator = st.session_state.language_translator

# Initialize Ollama LLM for response generation
llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:latest")
llm = OllamaLLM(
    model=llm_model,
    temperature=0.7
)

# Response generation prompt template
response_prompt = PromptTemplate.from_template("""
You are an expert petroleum engineer. Based on the retrieved information below, provide a comprehensive and accurate answer to the user's question.

Context from petroleum knowledge base:
{context}

User Question: {question}

Please provide a detailed, technical answer based on the retrieved information. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide what information you can.

Answer:""")

def contains_arabic(text):
    """Check if text contains Arabic characters"""
    if not text:
        return False
    arabic_range = range(0x0600, 0x06FF + 1)  # Arabic Unicode range
    return any(ord(char) in arabic_range for char in text)

def get_text_direction_class(text):
    """Determine the appropriate CSS class for text direction"""
    if contains_arabic(text):
        return "arabic-content"
    return "ltr-text"

def format_search_results(results):
    """Format search results into a readable context string"""
    if not results:
        return "No relevant information found in the knowledge base."
    
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(f"Source {i} (Score: {result['relevance_score']:.3f}):")
        context_parts.append(f"From: {result['chunk_info']}")
        context_parts.append(f"Content: {result['content']}")
        context_parts.append("-" * 40)
    
    return "\n".join(context_parts)

def generate_response(question: str):
    """Generate AI response using retrieved petroleum knowledge with multilingual support"""
    try:
        # PREPROCESSING: Language detection and translation to English
        english_question, detected_language = language_translator.process_query(question)
        
        # Log language detection for user visibility
        language_info = {
            'original_question': question,
            'english_question': english_question,
            'detected_language': detected_language,
            'language_name': language_translator.supported_languages.get(detected_language, 'Unknown')
        }
        
        # Search the knowledge base with English question
        search_results = search_function(english_question, k=5)
        
        # Format context
        context = format_search_results(search_results)
        
        # Generate response in English
        formatted_prompt = response_prompt.format(
            context=context,
            question=english_question
        )
        
        english_response = llm.invoke(formatted_prompt)
        
        # POSTPROCESSING: Translate response back to original language
        final_response = language_translator.process_response(english_response, detected_language)
        
        return final_response, search_results, language_info
        
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I apologize, but I encountered an error while processing your question.", [], None

# Streamlit App Configuration
st.set_page_config(
    page_title="🛢️ Petroleum Engineering Assistant",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: #ff4b4b;
        color: white;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #e0e4e8;
    }
    .user-info {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e0e4e8;
    }
    .user-info h4 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        color: #262730;
    }
    .user-info p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #262730;
    }
    .user-switching {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e0e4e8;
    }
    .user-switching h4 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        color: #262730;
    }
    .user-switching p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #262730;
    }
    .sidebar-section {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e0e4e8;
    }
    .sidebar-section h4 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        color: #262730;
    }
    .sidebar-section p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #262730;
    }
    .sidebar-section ul {
        margin: 1rem 0;
        padding-left: 1.2rem;
    }
    .sidebar-section li {
        margin: 0.5rem 0;
        color: #262730;
        font-size: 0.9rem;
    }
    .sidebar-section em {
        color: #666;
        font-style: italic;
    }
    .keyword-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #dee2e6;
        border: 1px solid #e9ecef;
        color: #6c757d;
    }
    
    /* RTL Support for Arabic Text */
    .rtl-text {
        direction: rtl;
        text-align: right;
        unicode-bidi: embed;
        font-family: 'Segoe UI', 'Arial Unicode MS', 'Tahoma', sans-serif;
    }
    
    .ltr-text {
        direction: ltr;
        text-align: left;
        unicode-bidi: embed;
    }
    
    /* Arabic text styling */
    .arabic-content {
        direction: rtl;
        text-align: right;
        unicode-bidi: embed;
        font-family: 'Segoe UI', 'Arabic UI', 'Tahoma', sans-serif;
        line-height: 1.6;
        font-size: 1.1em;
    }
    
    /* Mixed content container */
    .mixed-content {
        direction: ltr; /* Default direction */
        text-align: left;
    }
    
    .mixed-content .arabic-text {
        direction: rtl;
        text-align: right;
        unicode-bidi: embed;
        display: inline-block;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🛢️ Petroleum Engineering AI Assistant</h1>
    <p>Intelligent keyword-based usage system for fair access to petroleum expertise</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Sidebar for user management
with st.sidebar:
    st.markdown("### 👤 User Management")
    
    # Get current user info with fresh stats
    current_user = user_manager.get_current_user()
    fresh_user_stats = user_manager.get_user_stats()  # Always get fresh stats
    
    if current_user:
        st.markdown(f"""
        <div class="user-info">
            <h4>🔑 {current_user['name']}</h4>
            <p><strong>Type:</strong> {current_user['user_type'].title()}</p>
            <p><strong>Daily Limit:</strong> {fresh_user_stats['daily_keyword_limit']} keywords</p>
            <p><strong>Used Today:</strong> {fresh_user_stats['current_keyword_usage']}</p>
            <p><strong>Remaining:</strong> {fresh_user_stats['keywords_remaining']}</p>
            <p><strong>Queries:</strong> {fresh_user_stats['total_queries_today']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User switching section
        all_users = user_manager.get_all_users()
        user_options = {user['name']: user['user_id'] for user in all_users}
        
        st.markdown("""
        <div class="user-switching">
            <h4>🔄 Switch User</h4>
            <p>Select a different user profile:</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected_user_name = st.selectbox(
            "Select User:",
            options=list(user_options.keys()),
            index=list(user_options.values()).index(current_user['user_id']),
            label_visibility="collapsed"
        )
        
        # Only show switch button if different user is selected
        if selected_user_name != current_user['name']:
            if st.button("🔀 Switch User", use_container_width=True):
                selected_user_id = user_options[selected_user_name]
                if user_manager.switch_user(selected_user_id):
                    # Update session state to persist the change
                    st.session_state.user_manager = user_manager
                    st.success(f"✅ Switched to {selected_user_name}")
                    st.rerun()
                else:
                    st.error("❌ Failed to switch user")
    
    # Multilingual support info
    st.markdown("""
    <div class="sidebar-section">
        <h4>🌍 Multilingual Support</h4>
        <p><strong>Ask questions in:</strong></p>
        <ul>
            <li>🇺🇸 <strong>English:</strong> What is hydraulic fracturing?</li>
            <li>🇸🇦 <strong>Arabic:</strong> ما هو التكسير الهيدروليكي؟</li>
            <li>🇫🇷 <strong>French:</strong> Qu'est-ce que la fracturation?</li>
            <li>🇩🇪 <strong>German:</strong> Was ist hydraulisches Fracking?</li>
        </ul>
        <p><em>AI automatically detects and translates!</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Translation monitoring stats
    if 'language_translator' in st.session_state:
        translator = st.session_state.language_translator
        config = translator.get_configuration()
        monitoring_stats = translator.get_monitoring_stats()
        
        st.markdown("""
        <div class="sidebar-section">
            <h4>📊 Translation Monitoring</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key metrics
        performance = monitoring_stats['performance']
        language_usage = monitoring_stats['language_usage']
        
        # Metrics in compact format
        col_trans1, col_trans2 = st.columns(2)
        with col_trans1:
            st.metric("Queries", performance['total_queries_processed'])
            st.metric("Success Rate", f"{performance['success_rate_percentage']:.1f}%")
        with col_trans2:
            st.metric("Translations", performance['total_translations_performed'])
            st.metric("Avg Time", f"{performance['average_translation_time_seconds']:.2f}s")
        
        # Language distribution
        if language_usage['queries_by_language']:
            st.markdown("**Language Distribution:**")
            for lang, count in language_usage['queries_by_language'].items():
                lang_name = translator.supported_languages.get(lang, lang)
                percentage = (count / performance['total_queries_processed'] * 100) if performance['total_queries_processed'] > 0 else 0
                st.write(f"{lang_name}: {count} ({percentage:.1f}%)")
    
    else:
        st.markdown("""
        <div class="sidebar-section">
            <h4>⚠️ Translation Status</h4>
            <p><em>Translator not initialized</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Keyword extraction info
    st.markdown("""
    <div class="sidebar-section">
        <h4>📊 How Keywords Work</h4>
        <p><strong>Petroleum keywords include:</strong></p>
        <ul>
            <li>🔧 <strong>Drilling:</strong> drilling, wellbore, casing</li>
            <li>💥 <strong>Fracking:</strong> hydraulic, fracturing, proppant</li>
            <li>⛽ <strong>Production:</strong> oil, gas, reservoir</li>
            <li>🏔️ <strong>Geology:</strong> shale, formation, rock</li>
        </ul>
        <p><em>Non-petroleum questions are FREE!</em></p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Ask Your Questions")
    
    # Example questions in a more compact layout
    with st.expander("💡 **Try These Example Questions**", expanded=False):
        st.markdown("**Click any question to ask it:**")
        
        # Better example questions (including multilingual examples)
        example_questions = [
            "What is hydraulic fracturing?",
            "How does oil drilling work?", 
            "Explain reservoir engineering basics",
            "ما هو التكسير الهيدروليكي؟",  # Arabic: What is hydraulic fracturing?
            "Qu'est-ce que la fracturation hydraulique?",  # French: What is hydraulic fracturing?
            "Was ist hydraulisches Fracking?"  # German: What is hydraulic fracking?
        ]
        
        # Display in 2 columns for better layout
        col_a, col_b = st.columns(2)
        for i, question in enumerate(example_questions):
            with col_a if i % 2 == 0 else col_b:
                if st.button(f"🔍 {question}", key=f"example_{i}", use_container_width=True):
                    st.session_state.example_query = question

with col2:
    st.markdown("### 📈 Usage Statistics")
    
    # Create a placeholder for stats that can update without full refresh
    stats_placeholder = st.empty()
    
    if current_user:
        # Get fresh stats in case they were just updated
        fresh_stats = user_manager.get_user_stats()
        
        # Progress bar for keyword usage
        usage_percentage = (fresh_stats['current_keyword_usage'] / fresh_stats['daily_keyword_limit']) * 100 if fresh_stats['daily_keyword_limit'] > 0 else 0
        
        with stats_placeholder.container():
            st.metric(
                label="Keywords Used Today",
                value=f"{fresh_stats['current_keyword_usage']}/{fresh_stats['daily_keyword_limit']}",
                delta=f"{usage_percentage:.1f}% of daily limit"
            )
            
            st.progress(usage_percentage / 100)
            
            if fresh_stats['keywords_remaining'] == 0:
                st.error("🚫 Daily limit reached!")
            elif fresh_stats['keywords_remaining'] <= 2:
                st.warning("⚠️ Low on keywords!")
            else:
                st.success("✅ Good to go!")

# Chat input
query = st.chat_input("🔍 Ask your petroleum engineering question...", key="main_input")

# Handle example question selection
if hasattr(st.session_state, 'example_query'):
    query = st.session_state.example_query
    del st.session_state.example_query

# Process query
if query:
    # Check keyword limits before processing
    can_use, keywords_needed, keywords_remaining = user_manager.can_use_keywords(query)
    extracted_keywords = user_manager.extract_keywords(query)
    
    # Display keyword information
    if extracted_keywords or keywords_needed > 0:
        st.markdown(f"""
        <div class="keyword-info">
            <strong>🔍 Detected Keywords:</strong> {', '.join(extracted_keywords) if extracted_keywords else 'None'}
            <br><strong>📊 Keywords Needed:</strong> {keywords_needed}
            <br><strong>⚡ Keywords Remaining:</strong> {keywords_remaining if keywords_remaining != float('inf') else 'Unlimited'}
        </div>
        """, unsafe_allow_html=True)
    
    if not can_use:
        st.error(f"""
        ❌ **Keyword Limit Exceeded!**
        
        - You need **{keywords_needed} keywords** for this query
        - You only have **{keywords_remaining} keywords** remaining today
        - Your daily limit resets at midnight UTC
        
        💡 **Try asking simpler questions** with fewer petroleum terms, or switch to a user with higher limits.
        """)
    else:
        # Use keywords and process query
        if user_manager.use_keywords(query):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response with multilingual support
            with st.spinner("🔍 Searching petroleum knowledge base..."):
                response, search_results, language_info = generate_response(query)
            
            # Show language detection info if available
            if language_info and language_info['detected_language'] != 'en':
                # Create info message with proper text direction for original query
                original_query = language_info['original_question']
                query_direction_class = get_text_direction_class(original_query)
                
                st.info(f"""
                🌍 **Language Detected:** {language_info['language_name']} ({language_info['detected_language']})
                
                *(Your question was translated to English for processing, and the response was translated back)*
                """)
                
                # Show original query with proper text direction if it's Arabic
                if contains_arabic(original_query):
                    st.markdown(f"""
                    <div style="background: #e7f3ff; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0;">
                        <strong>Your original question:</strong><br>
                        <div class="{query_direction_class}" style="margin-top: 0.5rem;">
                            {original_query}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add assistant response to chat
            full_response = response
            if search_results:
                full_response += f"\n\n**Sources Found:** {len(search_results)} relevant documents"
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "search_results": search_results,
                "language_info": language_info
            })
            
            # Trigger a rerun to show the updated conversation and stats
            st.rerun()
        else:
            st.error("❌ Failed to process query due to keyword limit.")

# Display chat history
if st.session_state.messages:
    st.markdown("### 💬 Conversation")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if message content contains Arabic and apply appropriate styling
            content = message["content"]
            text_direction_class = get_text_direction_class(content)
            
            if contains_arabic(content):
                # Display Arabic content with RTL styling
                st.markdown(f"""
                <div class="{text_direction_class}">
                    {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Display regular content normally
                st.write(content)
            
            # Show language info if available (for assistant messages)
            if message["role"] == "assistant" and "language_info" in message and message["language_info"]:
                lang_info = message["language_info"]
                if lang_info['detected_language'] != 'en':
                    st.caption(f"🌍 Translated from {lang_info['language_name']} ({lang_info['detected_language']})")
            
            # Show search results if available (for assistant messages)
            if message["role"] == "assistant" and "search_results" in message and message["search_results"]:
                search_results = message["search_results"]
                with st.expander(f"📖 **View Source Documents** ({len(search_results)} found)"):
                    for i, result in enumerate(search_results, 1):
                        st.markdown(f"""
                        **Source {i}** (Relevance: {result['relevance_score']:.1%})
                        
                        📄 **{result['chunk_info']}**
                        
                        {result['content'][:300]}{'...' if len(result['content']) > 300 else ''}
                        
                        ---
                        """)

# Clear chat button
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem; padding: 1rem;">
    🛢️ <strong>Petroleum Engineering AI Assistant</strong><br>
    Powered by Ollama + ChromaDB + Streamlit<br>
    <em>Keyword-based usage limits ensure fair access to AI resources</em>
</div>
""", unsafe_allow_html=True) 