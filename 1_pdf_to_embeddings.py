#################################################################################################################################################################
###############################   1.  IMPORTING MODULES AND INITIALIZING VARIABLES   ############################################################################
#################################################################################################################################################################

import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

###############################   INITIALIZE EMBEDDINGS MODEL  #################################################################################################

# Initialize configurable embedding model
embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
embeddings = OllamaEmbeddings(
    model=embedding_model,
)
print(f"🔍 Using embedding model: {embedding_model}")

###############################   DELETE CHROMA DB IF EXISTS AND INITIALIZE   ##################################################################################

if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

vector_store = Chroma(
    collection_name="petroleum_docs",
    embedding_function=embeddings,
    persist_directory="chroma_db", 
)

###############################   INITIALIZE TEXT SPLITTER   ###################################################################################################

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

#################################################################################################################################################################
###############################   2.  PROCESSING THE PDF FILES   ################################################################################################
#################################################################################################################################################################

pdf_files = glob.glob("data/*.pdf")

for pdf_file in pdf_files:
    print(pdf_file)
    
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()
    
    texts = text_splitter.split_documents(documents)
    
    uuids = [str(uuid4()) for _ in range(len(texts))]
    
    vector_store.add_documents(documents=texts, ids=uuids) 