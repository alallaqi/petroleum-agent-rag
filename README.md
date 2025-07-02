# 🛢️ Petroleum Agent RAG System

A comprehensive **Retrieval-Augmented Generation (RAG)** system for petroleum engineering knowledge, built with **Python**, **LangChain**, **Ollama**, **ChromaDB**, and **Streamlit**.

## 📋 **What This System Does**

- **📚 Document Processing**: Converts petroleum engineering PDFs into searchable knowledge base
- **🔄 Smart Query Enhancement**: Automatically improves user questions with technical petroleum terms
- **🤖 AI-Powered Responses**: Uses local Ollama models for intelligent answers
- **🔍 Semantic Search**: Finds relevant information using vector embeddings
- **💬 Chat Interface**: Clean Streamlit web interface for easy interaction
- **🏢 Company Intelligence**: Answers questions about company services, training, and expertise

## 🎯 **Key Features**

✅ **Local AI Processing** - No external API dependencies  
✅ **Multi-Document Support** - PDFs, company profiles, training materials  
✅ **Query Enhancement** - Automatically improves search queries  
✅ **Source Citations** - Shows relevance scores and document sources  
✅ **Web Interface** - Professional Streamlit chatbot  
✅ **Easy Setup** - Step-by-step installation for any platform  

---

## 🚀 **Quick Start**

### **Prerequisites**

- **Python 3.12+** (recommended)
- **Ollama** installed and running
- **Git** (for cloning)

### **📥 Installation**

#### **macOS/Linux (Terminal)**

```bash
# 1. Clone the repository
git clone https://github.com/alallaqi/petroleum-agent-rag.git
cd petroleum-agent-rag

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r Requirements.txt

# 4. Install Ollama models
ollama pull llama3.2:latest
ollama pull mxbai-embed-large

# 5. Create environment file
cp env-example.txt .env
# Edit .env file if needed (optional - defaults work fine)
```

#### **Windows (PowerShell)**

```powershell
# 1. Clone the repository
git clone https://github.com/alallaqi/petroleum-agent-rag.git
cd petroleum-agent-rag

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r Requirements.txt

# 4. Install Ollama models
ollama pull llama3.2:latest
ollama pull mxbai-embed-large

# 5. Create environment file
Copy-Item env-example.txt .env
# Edit .env file if needed (optional - defaults work fine)
```

---

## 📁 **Project Structure**

```
petroleum-agent-rag/
├── data/                          # 📄 PDF documents (add your PDFs here)
│   ├── hyfrac-book.pdf           # Hydraulic fracturing guide
│   ├── Int-to-Pet-Eng.pdf        # Introduction to petroleum engineering
│   ├── unconventionalgas.pdf     # Unconventional gas production
│   ├── Company_Profile.pdf       # Company information
│   └── Training_Materials.pdf    # Training documents
├── chroma_db/                     # 🗄️ Vector database (auto-generated)
├── venv/                          # 🐍 Python virtual environment
├── 1_pdf_to_embeddings.py        # 📚 PDF processing & vectorization
├── 2_query_rewriter.py           # 🔄 Query enhancement system
├── 3_retrieval_system.py         # 🔍 Semantic search engine
├── 4_chatbot.py                  # 💬 Streamlit web interface
├── 5_website_scraper.py          # 🕷️ Company website scraper
├── .env                          # 🔧 Environment configuration
├── env-example.txt               # 📝 Environment template
├── setup_windows.ps1             # 🪟 Windows PowerShell setup script
├── Requirements.txt              # 📦 Python dependencies
└── README.md                     # 📖 This file
```

---

## 🔧 **Usage**

### **Step 1: Process Your Documents**

Add your PDF files to the `data/` folder, then run:

#### **macOS/Linux:**
```bash
source venv/bin/activate
python 1_pdf_to_embeddings.py
```

#### **Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
python 1_pdf_to_embeddings.py
```

**Expected Output:**
```
data/Company_Profile.pdf
data/hyfrac-book.pdf
data/unconventionalgas.pdf
...
✅ Processing complete! ChromaDB created with 567 chunks
```

### **Step 2: Test Query Enhancement**

#### **macOS/Linux:**
```bash
python 2_query_rewriter.py
```

#### **Windows PowerShell:**
```powershell
python 2_query_rewriter.py
```

### **Step 3: Test Retrieval System**

#### **macOS/Linux:**
```bash
python 3_retrieval_system.py
```

#### **Windows PowerShell:**
```powershell
python 3_retrieval_system.py
```

### **Step 4: Add Company Website Content (Optional)**

#### **macOS/Linux:**
```bash
python 5_website_scraper.py
```

#### **Windows PowerShell:**
```powershell
python 5_website_scraper.py
```

**Expected Output:**
```
🕷️ Starting Website Scraper for Expert Petroleum...
🔍 Discovering relevant company pages...
📚 Successfully scraped 8 pages
✅ Website content successfully added to ChromaDB!
```

### **Step 5: Launch Web Interface**

#### **macOS/Linux:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
streamlit run 4_chatbot.py
```

#### **Windows PowerShell:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1
streamlit run 4_chatbot.py
```

**🌐 Open browser to:** `http://localhost:8501`

---

## 🔄 **Query Enhancement/Prompt Optimizer**

The system includes a **smart query enhancement component** (`2_query_rewriter.py`) that automatically improves your questions before searching:

### **How It Works:**
- **📝 Simple Input**: You type basic questions like "fracking"
- **🧠 AI Enhancement**: System expands it with technical terms
- **🎯 Better Results**: Finds more relevant petroleum engineering content

### **Example Transformations:**
| **Your Question** | **Enhanced Query** |
|--|--|
| "fracking" | "hydraulic fracturing, well stimulation, proppant injection, reservoir permeability" |
| "oil drilling" | "petroleum drilling, wellbore construction, drilling fluids, completion techniques" |
| "gas production" | "natural gas extraction, hydrocarbon recovery, enhanced oil recovery methods" |

### **Benefits:**
✅ **Finds More Content** - Technical term expansion increases search hits  
✅ **Better Relevance** - Industry-specific terminology improves results  
✅ **Smarter Search** - Understands petroleum engineering context  
✅ **Seamless Operation** - Works automatically behind the scenes  

---

## 💬 **Using the Chatbot**

1. **📝 Type questions** in the chat input (the system automatically enhances them!)
2. **🤖 Get AI responses** based on your documents
3. **📚 View sources** in the expandable "Sources Used" section
4. **🔍 Try example questions** from the sidebar

### **Example Questions:**
- "What is hydraulic fracturing?"
- "What services does our company provide?"
- "How does horizontal drilling work?"
- "Explain unconventional gas reservoirs"
- "What training programs are available?"

---

## ⚙️ **Configuration**

### **Environment Variables**
Create a `.env` file in the project root using the provided template:

#### **macOS/Linux:**
```bash
cp env-example.txt .env
# Edit .env file with your preferred settings
```

#### **Windows PowerShell:**
```powershell
Copy-Item env-example.txt .env
# Edit .env file with your preferred settings
```

**Key Variables:**
- `COMPANY_WEBSITE_URL` - Your company website to scrape (default: https://expsdz.com/)
- `OLLAMA_LLM_MODEL` - LLM model for responses (default: llama3.2:latest)
- `OLLAMA_EMBEDDING_MODEL` - Embedding model for search (default: mxbai-embed-large)

### **Ollama Models**
- **LLM**: `llama3.2:latest` (for responses)
- **Embeddings**: `mxbai-embed-large` (for search)

### **ChromaDB Settings**
- **Collection**: `petroleum_docs`
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters

### **Streamlit Configuration**
- **Port**: 8501 (default)
- **Interface**: Chat-based with source citations

---

## 🔄 **Adding New Documents**

1. **📁 Add PDFs** to the `data/` folder
2. **🔄 Reprocess** the knowledge base:

#### **macOS/Linux:**
```bash
source venv/bin/activate
python 1_pdf_to_embeddings.py
```

#### **Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
python 1_pdf_to_embeddings.py
```

3. **🚀 Restart** the chatbot to use updated data

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **❌ "Command not found: ollama"**
- Install Ollama from: https://ollama.ai/
- Ensure it's in your PATH

#### **❌ "Command not found: streamlit"**
- Activate virtual environment first
- Reinstall: `pip install streamlit`

#### **❌ "ChromaDB empty (0 chunks)"**
- Check if PDFs are in `data/` folder
- Ensure collection name matches in `3_retrieval_system.py`
- Rerun `1_pdf_to_embeddings.py`

#### **❌ Windows PowerShell Execution Policy**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Performance Tips**

- **🔥 GPU**: Enable GPU acceleration in Ollama for faster responses
- **💾 Memory**: 8GB+ RAM recommended for larger document collections
- **⚡ SSD**: Use SSD storage for faster ChromaDB operations

---

## 📦 **Dependencies**

- **langchain** - LLM framework
- **langchain-community** - Community integrations
- **langchain-chroma** - ChromaDB integration
- **langchain-ollama** - Ollama integration
- **streamlit** - Web interface
- **chromadb** - Vector database
- **pypdf** - PDF processing
- **ollama** - Local LLM runtime

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Add your improvements
4. Test thoroughly
5. Submit pull request

---

## 📄 **License**

This project is licensed under the MIT License.

---

## 🙋 **Support**

For questions or issues:
1. Check the troubleshooting section above
2. Review the example questions in the sidebar
3. Ensure all dependencies are properly installed
4. Verify Ollama models are downloaded

---

**🛢️ Built with ❤️ for Petroleum Engineering** 