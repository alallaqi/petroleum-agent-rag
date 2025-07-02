#################################################################################################################################################################
###############################   1.  IMPORTING MODULES AND INITIALIZING VARIABLES   ############################################################################
#################################################################################################################################################################

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🕷️  Starting Website Scraper for Expert Petroleum...")

###############################   INITIALIZE MODELS AND VARIABLES   ############################################################################

# Initialize the same embedding model used for PDFs
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
)

# Initialize text splitter with same settings as PDF processing
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Company website URL from environment
base_url = os.getenv("COMPANY_WEBSITE_URL", "https://expsdz.com/")
print(f"🌐 Target website: {base_url}")

#################################################################################################################################################################
###############################   2.  WEBSITE SCRAPING FUNCTIONS   ############################################################################################
#################################################################################################################################################################

def get_page_content(url, timeout=10):
    """Scrape content from a single webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"📡 Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return None

def discover_company_pages(base_url, max_pages=10):
    """Discover relevant company pages to scrape"""
    pages_to_scrape = [base_url]
    
    try:
        # Get main page first
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find relevant internal links
        relevant_keywords = ['services', 'about', 'company', 'profile', 'expertise', 'petroleum', 'drilling', 'training', 'certification']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                
                # Check if it's an internal link and contains relevant keywords
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    link_text = link.get_text().lower()
                    href_lower = href.lower()
                    
                    if any(keyword in link_text or keyword in href_lower for keyword in relevant_keywords):
                        if full_url not in pages_to_scrape and len(pages_to_scrape) < max_pages:
                            pages_to_scrape.append(full_url)
                            print(f"🔗 Found relevant page: {full_url}")
        
    except Exception as e:
        print(f"⚠️  Could not discover additional pages: {str(e)}")
    
    return pages_to_scrape

#################################################################################################################################################################
###############################   3.  MAIN SCRAPING AND PROCESSING   ##########################################################################################
#################################################################################################################################################################

def scrape_company_website():
    """Main function to scrape company website and add to ChromaDB"""
    
    print("🚀 Starting Expert Petroleum website scraping...")
    
    # Discover pages to scrape
    print("🔍 Discovering relevant company pages...")
    pages_to_scrape = discover_company_pages(base_url, max_pages=15)
    
    print(f"📄 Found {len(pages_to_scrape)} pages to scrape:")
    for page in pages_to_scrape:
        print(f"   • {page}")
    
    # Scrape all pages
    all_documents = []
    
    for i, url in enumerate(pages_to_scrape, 1):
        print(f"\n📡 Scraping page {i}/{len(pages_to_scrape)}: {url}")
        
        content = get_page_content(url)
        if content and len(content.strip()) > 100:  # Only process pages with substantial content
            
            # Create document
            doc = Document(
                page_content=content,
                metadata={
                    "source": url,
                    "type": "website",
                    "company": "Expert Petroleum Services",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            
            all_documents.append(doc)
            print(f"✅ Scraped {len(content)} characters from {url}")
        
        # Be respectful - small delay between requests
        time.sleep(1)
    
    if not all_documents:
        print("❌ No content was successfully scraped!")
        return
    
    print(f"\n📚 Successfully scraped {len(all_documents)} pages")
    
    # Split documents into chunks
    print("✂️  Splitting website content into chunks...")
    website_chunks = text_splitter.split_documents(all_documents)
    
    print(f"📄 Created {len(website_chunks)} chunks from website content")
    
    # Load existing ChromaDB and add website content
    print("💾 Adding website content to existing ChromaDB...")
    
    vector_db = Chroma(
        collection_name="petroleum_docs",
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )
    
    # Add website chunks to existing database
    vector_db.add_documents(website_chunks)
    
    print("✅ Website content successfully added to ChromaDB!")
    
    # Test the updated database
    print("\n🧪 Testing updated knowledge base...")
    test_query = "Expert Petroleum services"
    results = vector_db.similarity_search(test_query, k=3)
    
    print(f"\n🔍 Test search for '{test_query}':")
    for i, result in enumerate(results, 1):
        source = result.metadata.get('source', 'Unknown')
        content_type = result.metadata.get('type', 'Unknown')
        print(f"\n{i}. Source: {source} ({content_type})")
        print(f"   Content: {result.page_content[:200]}...")

if __name__ == "__main__":
    scrape_company_website() 