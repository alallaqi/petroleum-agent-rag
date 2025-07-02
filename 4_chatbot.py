import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our existing search function
import importlib.util
import sys

# Load the 3_retrieval_system.py module
spec = importlib.util.spec_from_file_location("retrieval_system", "3_retrieval_system.py")
retrieval_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retrieval_module)

# Get the search function
search_petroleum_knowledge = retrieval_module.search_petroleum_knowledge

#################################################################################################################################################################
###############################   STREAMLIT PETROLEUM AI CHATBOT   ############################################################################################
#################################################################################################################################################################

st.set_page_config(
    page_title="Petroleum Engineering AI Assistant",
    page_icon="🛢️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        text-align: left;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 0.5rem;
        border: 1px solid #444;
        background-color: #1f2937;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #374151;
        border-color: #6b7280;
        transform: translateY(-1px);
    }
    .knowledge-base-item {
        padding: 0.3rem 0;
        font-size: 0.9rem;
    }
    .stats-container {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🛢️ Petroleum Engineering AI Assistant")
st.markdown("Ask questions about petroleum engineering, drilling, hydraulic fracturing, and more!")
st.markdown('</div>', unsafe_allow_html=True)

###############################   INITIALIZE OLLAMA FOR RESPONSE GENERATION   ###############################################################################

@st.cache_resource
def load_llm():
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:latest")
    return OllamaLLM(
        model=llm_model,
        temperature=0.7
    )

llm = load_llm()

###############################   RESPONSE GENERATION PROMPT   ##############################################################################################

response_prompt = PromptTemplate.from_template("""
You are a petroleum engineering expert. Answer the user's question using the provided context from petroleum engineering documents.

Context from documents:
{context}

User Question: {question}

Provide a comprehensive answer based on the context. If the context doesn't contain enough information, mention what you know and suggest where to find more details.

Answer:""")

###############################   MAIN CHAT INTERFACE   ######################################################################################################

def generate_response(question: str, search_results: list) -> str:
    """Generate a comprehensive response using search results as context."""
    
    if not search_results:
        return "I couldn't find relevant information in the petroleum engineering documents. Please try rephrasing your question or ask about topics covered in hydraulic fracturing, drilling, or unconventional gas production."
    
    # Combine search results into context
    context_parts = []
    for i, result in enumerate(search_results[:3], 1):  # Use top 3 results
        context_parts.append(f"Source {i} ({result['chunk_info']}):\n{result['content'][:300]}...")
    
    context = "\n\n".join(context_parts)
    
    # Generate response
    try:
        formatted_prompt = response_prompt.format(context=context, question=question)
        response = llm.invoke(formatted_prompt)
        return response
    except Exception as e:
        return f"Error generating response: {e}"

def process_question(question: str):
    """Process a question and generate response"""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Search for relevant information
    search_results = search_petroleum_knowledge(question, k=5)
    
    # Generate AI response
    response = generate_response(question, search_results)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "search_results": search_results
    })

###############################   SESSION STATE INITIALIZATION   #########################################################################################

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize flag for example question clicks
if "process_example" not in st.session_state:
    st.session_state.process_example = None

###############################   SIDEBAR WITH EXAMPLE QUESTIONS   #######################################################################################

with st.sidebar:
    st.header("🔍 Example Questions")
    st.markdown("Click any question to try it:")
    
    example_questions = [
        "What is hydraulic fracturing?",
        "How does horizontal drilling work?",
        "Explain unconventional gas reservoirs",
        "What are the steps in well completion?",
        "Tell me about shale gas production",
        "What is the role of proppants in fracking?",
        "How do you prevent formation damage?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{question}"):
            st.session_state.process_example = question
            st.rerun()
    
    st.divider()
    
    # Knowledge base info with better styling
    st.markdown("**📊 Knowledge Base:**")
    with st.container():
        st.markdown('<div class="knowledge-base-item">• Hydraulic Fracturing Guide</div>', unsafe_allow_html=True)
        st.markdown('<div class="knowledge-base-item">• Introduction to Petroleum Engineering</div>', unsafe_allow_html=True)
        st.markdown('<div class="knowledge-base-item">• Unconventional Gas Production</div>', unsafe_allow_html=True)
        st.markdown('<div class="knowledge-base-item">• Company Services & Training</div>', unsafe_allow_html=True)
        st.markdown('<div class="knowledge-base-item">• Website Content</div>', unsafe_allow_html=True)
    
    # Stats container
    st.markdown("""
    <div class="stats-container">
        <strong>📈 Knowledge Base Stats:</strong><br>
        📄 609 document chunks<br>
        🔍 8 PDF documents<br>
        🌐 Website content included
    </div>
    """, unsafe_allow_html=True)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

###############################   PROCESS EXAMPLE QUESTION IF CLICKED   ##################################################################################

# Handle example question clicks
if st.session_state.process_example:
    question = st.session_state.process_example
    st.session_state.process_example = None  # Reset the flag
    
    # Process the example question
    with st.spinner("Searching petroleum knowledge base..."):
        process_question(question)
    st.rerun()

###############################   DISPLAY CHAT HISTORY   #################################################################################################

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources for assistant messages
        if message["role"] == "assistant" and "search_results" in message:
            search_results = message["search_results"]
            if search_results:
                with st.expander("📚 View Sources"):
                    for i, result in enumerate(search_results, 1):
                        st.write(f"**Source {i}** (Relevance: {result['relevance_score']:.3f})")
                        st.write(f"📄 {result['chunk_info']}")
                        st.write(f"📝 Content: {result['content'][:200]}...")
                        if i < len(search_results):
                            st.divider()

###############################   USER INPUT   ###########################################################################################################

# User input
if prompt := st.chat_input("Ask about petroleum engineering..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching petroleum knowledge base..."):
            # Search for relevant information
            search_results = search_petroleum_knowledge(prompt, k=5)
            
            # Generate AI response
            response = generate_response(prompt, search_results)
            
            st.markdown(response)
            
            # Show sources in an expander
            if search_results:
                with st.expander("📚 View Sources"):
                    for i, result in enumerate(search_results, 1):
                        st.write(f"**Source {i}** (Relevance: {result['relevance_score']:.3f})")
                        st.write(f"📄 {result['chunk_info']}")
                        st.write(f"📝 Content: {result['content'][:200]}...")
                        if i < len(search_results):
                            st.divider()
    
    # Add messages to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "search_results": search_results
    })

###############################   FOOTER   ################################################################################################################

st.markdown("---")
st.markdown("🛢️ **Petroleum Engineering AI Assistant** | Powered by Ollama + ChromaDB + LangChain") 