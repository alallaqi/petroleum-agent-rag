#################################################################################################################################################################
###############################   1.  IMPORTING MODULES AND INITIALIZING VARIABLES   ############################################################################
#################################################################################################################################################################

import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 Starting Query Rewriter...")

###############################   INITIALIZE CHAT MODEL   #######################################################################################################

# Initialize Ollama LLM with configurable model
llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:latest")
llm = OllamaLLM(
    model=llm_model,  # Using configurable model
    temperature=0.3
)
print(f"🤖 Using LLM model: {llm_model}")

###############################   DEFINE QUERY ENHANCEMENT PROMPT   #############################################################################################

query_enhancement_prompt = PromptTemplate.from_template("""
You are a petroleum engineering expert. Enhance this query for better petroleum knowledge retrieval by adding technical synonyms and related concepts.

Return ONLY the enhanced query text, no explanations.

Query: {original_query}

Enhanced query:""")

###############################   QUERY ENHANCEMENT FUNCTION   ##################################################################################################

def enhance_query(user_query: str) -> str:
    """
    Enhance a user query for better petroleum knowledge retrieval.
    
    Args:
        user_query (str): Original user query
        
    Returns:
        str: Enhanced query with petroleum-specific terms and synonyms
    """
    try:
        # Create the prompt
        formatted_prompt = query_enhancement_prompt.format(original_query=user_query)
        
        # Get enhanced query from LLM
        enhanced_query = llm.invoke(formatted_prompt)
        
        print(f"Original: {user_query}")
        print(f"Enhanced: {enhanced_query}")
        
        return enhanced_query.strip()
        
    except Exception as e:
        print(f"Error enhancing query: {e}")
        return user_query  # Return original if enhancement fails

###############################   TESTING THE QUERY REWRITER   ##################################################################################################

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING PETROLEUM QUERY REWRITER")
    print("="*80)
    
    # Test queries
    test_queries = [
        "fracking",
        "oil drilling",
        "gas production",
        "well completion",
        "reservoir engineering"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        enhanced = enhance_query(query)
        print(f"✅ Result: '{enhanced}'")
        print("-" * 60) 