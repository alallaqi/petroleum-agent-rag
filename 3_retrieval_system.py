#################################################################################################################################################################
###############################   1.  IMPORTING MODULES AND INITIALIZING VARIABLES   ############################################################################
#################################################################################################################################################################

import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 Starting Petroleum Retrieval System...")

###############################   INITIALIZE MODELS   ###########################################################################################################

# Initialize configurable models
embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:latest")

# Initialize embeddings (same as used for PDF processing)
embeddings = OllamaEmbeddings(
    model=embedding_model,
)

# Initialize LLM for query enhancement
llm = OllamaLLM(
    model=llm_model,
    temperature=0.3
)

print(f"🔍 Using embedding model: {embedding_model}")
print(f"🤖 Using LLM model: {llm_model}")

###############################   LOAD CHROMADB   ############################################################################################################

# Load the existing ChromaDB with your petroleum PDFs
vector_db = Chroma(
    collection_name="petroleum_docs",
    persist_directory="./chroma_db",
    embedding_function=embeddings,
)

print(f"📚 Loaded ChromaDB with {vector_db._collection.count()} chunks")

###############################   QUERY ENHANCEMENT   #######################################################################################################

query_enhancement_prompt = PromptTemplate.from_template("""
You are a petroleum engineering expert. Enhance this query for better petroleum knowledge retrieval by adding technical synonyms and related concepts.

Return ONLY the enhanced query text, no explanations.

Query: {original_query}

Enhanced query:""")

def enhance_query(user_query: str) -> str:
    """
    Enhance a user query for better petroleum knowledge retrieval.
    """
    try:
        formatted_prompt = query_enhancement_prompt.format(original_query=user_query)
        enhanced_query = llm.invoke(formatted_prompt)
        return enhanced_query.strip()
    except Exception as e:
        print(f"Error enhancing query: {e}")
        return user_query  # Return original if enhancement fails

###############################   RETRIEVAL FUNCTION   ######################################################################################################

def search_petroleum_knowledge(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Search petroleum knowledge base and return relevant chunks with metadata.
    
    Args:
        query (str): User's question
        k (int): Number of results to return
        
    Returns:
        List[Dict]: Relevant documents with content, source, and relevance score
    """
    
    print(f"\n🔍 Original query: {query}")
    
    # Step 1: Enhance the query
    enhanced_query = enhance_query(query)
    print(f"🚀 Enhanced query: {enhanced_query}")
    
    # Step 2: Search ChromaDB with enhanced query
    try:
        search_results = vector_db.similarity_search_with_score(
            enhanced_query, 
            k=k
        )
        
        # Step 3: Format results with relevance scores
        formatted_results = []
        for doc, score in search_results:
            result = {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "relevance_score": float(1 - score),  # Convert distance to similarity
                "chunk_info": f"Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')}"
            }
            formatted_results.append(result)
            
        print(f"✅ Found {len(formatted_results)} relevant chunks")
        return formatted_results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

###############################   TESTING THE RETRIEVAL SYSTEM   ############################################################################################

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING PETROLEUM RETRIEVAL SYSTEM")
    print("="*80)
    
    # Test queries related to your PDFs
    test_queries = [
        "What is hydraulic fracturing?",
        "How does oil drilling work?",
        "Explain gas production methods",
        "What are unconventional reservoirs?",
        "Tell me about well completion"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 QUERY: {query}")
        print('='*60)
        
        results = search_petroleum_knowledge(query, k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n📄 RESULT {i} (Score: {result['relevance_score']:.3f})")
                print(f"Source: {result['chunk_info']}")
                print(f"Content: {result['content'][:200]}...")
                print("-" * 40)
        else:
            print("❌ No results found")
        
        print("\n" + "🔄" * 30) 