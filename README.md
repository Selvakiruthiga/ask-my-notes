ask-my-notes 📚

A Retrieval-Augmented Generation (RAG) system that lets you upload PDF documents and ask questions about them. The system uses hybrid retrieval (BM25 + semantic embeddings) and Google Gemini to provide accurate, source-backed answers.

Features
📄 PDF Document Upload - Extract and process PDF documents
🔍 Hybrid Retrieval - Combines keyword matching (BM25) and semantic search (embeddings)
🎯 RRF Fusion - Reciprocal Rank Fusion for optimal result ranking
🤖 AI-Powered Answers - Google Gemini generates context-aware responses
💯 Confidence Scoring - Includes confidence percentage for each answer
📝 Source Attribution - Shows which document chunks were used for the answer
🌐 Web Interface - Simple and intuitive UI for interaction
How It Works
1. UPLOAD (document_processor.py)
   └─ PDF → extracted text → split into chunks

2. STORE (vector_store.py)
   └─ Each chunk → converted to embedding → saved with pickle

3. RETRIEVAL (retriever.py)
   ├─ BM25 finds keyword matches
   ├─ Embeddings find meaning matches
   └─ RRF fuses both into final top-5 chunks

4. AUGMENTATION (generator.py → build_prompt)
   └─ Top-5 chunks + your question combined into one prompt

5. GENERATION (generator.py → generate_answer)
   └─ Gemini reads the prompt and writes the answer

6. DISPLAY (main.py → script.js)
   └─ Answer + confidence % + source chunks shown to user
Project Structure
ask-my-notes/
├── document_processor.py    # PDF extraction and chunking
├── vector_store.py          # Embedding storage and management
├── retriever.py             # Hybrid search (BM25 + embeddings + RRF)
├── generator.py             # Prompt building and answer generation
├── main.py                  # Flask/FastAPI backend
├── script.js                # Frontend JavaScript
├── README.md
├── requirements.txt
└── venv/                    # Virtual environment
Installation
Clone the repository
bash
git clone https://github.com/Selvakiruthiga/ask-my-notes.git
cd ask-my-notes
Create virtual environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies
bash
pip install -r requirements.txt
Set up API keys Create a .env file in the project root:
env
GOOGLE_API_KEY=your_gemini_api_key_here
Usage
Start the application
bash
python main.py
Open in browser Navigate to http://localhost:5000 (or your configured port)
Upload a PDF
Click "Upload PDF" and select your document
Wait for processing to complete
Ask Questions
Type your question in the input field
Get instant answers with confidence scores and sources
Technologies Used
Python - Core language
Flask/FastAPI - Backend server
Google Gemini - LLM for answer generation
Sentence Transformers - Semantic embeddings
BM25 - Keyword-based retrieval
JavaScript - Frontend interactivity
Pickle - Vector storage
Requirements

See requirements.txt for full dependency list. Key requirements:

Python 3.8+
Google Gemini API key
Required Python packages (see requirements.txt)
Future Improvements
 Support for multiple document formats (DOCX, TXT, etc.)
 Multi-language support
 Batch processing for large documents
 Chat history and conversation context
 Advanced filtering and search options
 Database integration for scalability
Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

License

This project is open source and available under the MIT License.

Author

Selvakiruthiga

Support

If you encounter any issues, please open an issue in the repository or contact the author.

Note: Make sure you have a valid Google Gemini API key before running the application.
