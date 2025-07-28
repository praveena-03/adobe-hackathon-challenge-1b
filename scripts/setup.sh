#!/bin/bash

# Adobe Hackathon Challenge 1b - Setup Script
# Multi-Collection PDF Analysis with Persona-Based Content Analysis

echo "Setting up Adobe Hackathon Challenge 1b environment..."

# Create necessary directories
mkdir -p /app/input
mkdir -p /app/output
mkdir -p /app/cache
mkdir -p /app/models
mkdir -p /app/logs

# Set permissions
chmod 755 /app/input
chmod 755 /app/output
chmod 755 /app/cache
chmod 755 /app/models
chmod 755 /app/logs

# Install system dependencies (if not already installed)
echo "Installing system dependencies..."

# Update package list
apt-get update

# Install required system packages
apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libreoffice \
    pandoc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Create virtual environment
echo "Creating Python virtual environment..."
python3.10 -m venv /opt/venv

# Activate virtual environment
source /opt/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create sample configuration
echo "Creating sample configuration..."
cat > /app/config.json << EOF
{
    "processing": {
        "max_file_size_mb": 50,
        "max_processing_time_seconds": 60,
        "max_concurrent_processes": 4,
        "enable_ocr": true,
        "enable_cross_analysis": true
    },
    "personas": {
        "default_persona": "researcher",
        "enable_custom_keywords": true,
        "enable_complexity_assessment": true
    },
    "performance": {
        "enable_monitoring": true,
        "monitoring_interval_seconds": 5,
        "max_history_size": 1000,
        "cleanup_interval_hours": 24
    },
    "output": {
        "format": "json",
        "include_metadata": true,
        "include_structure": true,
        "include_persona_analysis": true,
        "include_cross_analysis": true
    }
}
EOF

# Create sample persona configurations
echo "Creating sample persona configurations..."
cat > /app/personas.json << EOF
{
    "researcher": {
        "persona_type": "researcher",
        "focus_areas": ["methodology", "analysis", "results"],
        "expertise_level": "advanced",
        "analysis_depth": "detailed",
        "custom_keywords": ["hypothesis", "p-value", "correlation"]
    },
    "student": {
        "persona_type": "student",
        "focus_areas": ["key_concepts", "study_materials"],
        "expertise_level": "beginner",
        "analysis_depth": "standard",
        "custom_keywords": ["learning", "education", "assignment"]
    },
    "business_analyst": {
        "persona_type": "business_analyst",
        "focus_areas": ["strategy", "metrics", "performance"],
        "expertise_level": "intermediate",
        "analysis_depth": "standard",
        "custom_keywords": ["ROI", "KPI", "market_analysis"]
    }
}
EOF

echo "Setup completed successfully!"
echo "Environment is ready for Adobe Hackathon Challenge 1b"
echo ""
echo "To start the application:"
echo "  docker run -p 8000:8000 adobe-hackathon-1b"
echo ""
echo "To process a single PDF:"
echo "  curl -X POST http://localhost:8000/process-single -F 'file=@your_file.pdf'"
echo ""
echo "To process a collection:"
echo "  curl -X POST http://localhost:8000/process-collection -H 'Content-Type: application/json' -d '{\"collection_path\": \"/path/to/collection\"}'" 