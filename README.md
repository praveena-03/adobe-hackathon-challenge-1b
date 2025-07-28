# Adobe India Hackathon 2025 - Challenge 1b

## 🎯 Universal PDF Analysis Solution

A comprehensive PDF analysis system that intelligently processes any type of PDF document and generates structured, meaningful output with automatic persona detection and content enhancement.

## 🚀 Features

### **Universal Compatibility**
- ✅ Works with **any PDF type** (technical, travel, business, academic, legal, medical, etc.)
- ✅ **Intelligent content analysis** that adapts to document type
- ✅ **Automatic persona detection** based on content analysis
- ✅ **Smart section title enhancement** for meaningful output

### **Advanced Processing**
- **Multi-library PDF extraction** (PyMuPDF, PyPDF2, pdfplumber)
- **Intelligent content refinement** with context-aware analysis
- **Cross-document analysis** for collections
- **Performance monitoring** and optimization

### **Perfect Output Format**
- **Exact JSON structure** matching challenge requirements
- **Concise section titles** (max 30 characters)
- **Enhanced content analysis** with meaningful descriptions
- **Proper persona formatting** (e.g., "Travel Planner" instead of "Travel_Planner")

## 📋 Requirements

- Python 3.10+
- FastAPI
- PyMuPDF, PyPDF2, pdfplumber
- Additional dependencies in `requirements.txt`

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd adobe-hackathon-1b

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### **Start the Server**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### **API Endpoints**

#### **Process Single PDF**
```
POST /process-pdf
```

#### **Process PDF Collection**
```
POST /process-collection
```

### **Access API Documentation**
Open your browser and go to: `http://localhost:8000/docs`

## 📊 Output Format

The solution produces output in the exact format required by Adobe Hackathon Challenge 1b:

```json
{
  "metadata": {
    "input_documents": ["document1.pdf", "document2.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-28T20:35:56.817700"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "section_title": "Fill and sign PDF forms",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "document1.pdf",
      "refined_text": "Interactive forms contain fields that you can select and fill in. Use the Fill & Sign tool to complete PDF forms efficiently.",
      "page_number": 1
    }
  ]
}
```

## 🎯 Supported Document Types

### **Technical Documents**
- **Persona**: Technical Writer / HR Professional
- **Features**: API guides, software documentation, technical manuals

### **Travel Documents**
- **Persona**: Travel Planner
- **Features**: Travel guides, destination information, activity recommendations

### **Business Documents**
- **Persona**: Business Analyst
- **Features**: Financial reports, business plans, market analysis

### **Academic Documents**
- **Persona**: Researcher
- **Features**: Research papers, academic studies, methodology documents

### **Legal Documents**
- **Persona**: Legal Professional
- **Features**: Contracts, legal agreements, compliance documents

### **Medical Documents**
- **Persona**: Medical Professional
- **Features**: Medical reports, patient information, clinical studies

## 🔧 Architecture

```
src/
├── main.py                 # FastAPI application entry point
├── pdf_processor.py        # Multi-library PDF content extraction
├── persona_analyzer.py     # Intelligent persona detection
├── output_formatter.py     # Human-like content enhancement
├── collection_manager.py   # Multi-document processing
└── performance_monitor.py  # Performance optimization
```

## 🏆 Key Achievements

1. **Universal Compatibility**: Works with any PDF type without hardcoded mappings
2. **Human-Like Analysis**: Produces output as if analyzed by a human expert
3. **Perfect Format Match**: Exact JSON structure required by the challenge
4. **Intelligent Enhancement**: Context-aware content refinement
5. **Production Ready**: Robust error handling and performance optimization

## 📝 License

This project is developed for Adobe India Hackathon 2025 - Challenge 1b.

## 👨‍💻 Author

Developed for Adobe India Hackathon 2025 