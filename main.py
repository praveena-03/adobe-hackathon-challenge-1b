"""
Adobe India Hackathon Challenge 1b - Multi-Collection PDF Analysis
Advanced persona-based content analysis with offline processing capabilities
"""

import os
import time
import asyncio
import tempfile
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger

from src.pdf_processor import PDFProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.collection_manager import CollectionManager
from src.performance_monitor import PerformanceMonitor
from src.output_formatter import OutputFormatter
from src.models import ProcessingRequest, ProcessingResponse, PersonaConfig

# Initialize FastAPI app
app = FastAPI(
    title="Adobe Hackathon Challenge 1b - PDF Analysis",
    description="Multi-Collection PDF Analysis with Persona-Based Content Analysis",
    version="1.0.0"
)

# Initialize components
pdf_processor = PDFProcessor()
persona_analyzer = PersonaAnalyzer()
collection_manager = CollectionManager()
performance_monitor = PerformanceMonitor()
output_formatter = OutputFormatter()

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PROCESSING_TIME = 60  # 60 seconds

# Create directories if they don't exist
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("cache", exist_ok=True)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        memory_usage = performance_monitor.get_memory_usage()
        cpu_usage = performance_monitor.get_cpu_usage()
        active_processes = performance_monitor.get_active_processes()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "active_processes": active_processes
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-single", response_model=ProcessingResponse)
async def process_single_pdf(
    file: UploadFile = File(...),
    persona_config: Optional[str] = None
):
    """Process a single PDF file"""
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE/1024/1024}MB limit")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='input') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        start_time = time.time()
        
        # Process PDF
        config = {"persona_type": "auto"}  # Auto-detect persona
        if persona_config and persona_config.strip():
            try:
                import json
                config = json.loads(persona_config)
            except:
                config = {"persona_type": "auto"}
        
        result = await asyncio.wait_for(
            process_pdf_file(temp_path, config),
            timeout=MAX_PROCESSING_TIME
        )
        processing_time = time.time() - start_time

        # Format output according to Challenge 1b specifications
        formatted_output = output_formatter.format_single_pdf_output(
            filename=file.filename,
            processing_time=processing_time,
            file_size=file.size,
            metadata=result.get("metadata", {}),
            structure=result.get("structure", {}),
            content=result.get("content", {}),
            persona_config=config
        )

        # Save output to file
        output_filename = f"{file.filename.replace('.pdf', '')}_analysis_{int(time.time())}.json"
        output_formatter.save_output(formatted_output, output_filename)

        # Clean up
        os.remove(temp_path)

        return ProcessingResponse(
            success=True,
            filename=file.filename,
            processing_time=processing_time,
            file_size=file.size,
            result=formatted_output
        )
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Processing timeout exceeded")
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_pdf_file(file_path: str, config: dict) -> dict:
    """Process a PDF file and return results"""
    try:
        # Process PDF
        result = pdf_processor.process_pdf(file_path)
        
        # Analyze content with persona
        if result.get("content", {}).get("text_content"):
            persona_analysis = persona_analyzer.analyze_content(
                result["content"]["text_content"],
                config.get("persona_type", "general")
            )
            result["persona_analysis"] = persona_analysis
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_pdf_file: {e}")
        raise

@app.post("/process-collection")
async def process_collection_async(
    files: List[UploadFile] = File(..., description="Multiple PDF files to process")
):
    """Process a collection of PDF files"""
    try:
        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
            
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {file.size} exceeds size limit")
        
        # Generate task ID
        task_id = f"task_{int(time.time())}"
        
        # Create collection directory
        collection_path = f"input/collection_{task_id}"
        os.makedirs(collection_path, exist_ok=True)
        
        # Save files and process them
        results = []
        for file in files:
            try:
                # Save file
                file_path = os.path.join(collection_path, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Process the file
                config = {"persona_type": "auto"}  # Auto-detect persona
                result = await process_pdf_file(file_path, config)
                
                # Debug logging
                logger.info(f"Processing {file.filename}:")
                logger.info(f"  - Has structure: {'structure' in result}")
                logger.info(f"  - Has content: {'content' in result}")
                if 'structure' in result:
                    logger.info(f"  - Sections count: {len(result['structure'].get('sections', []))}")
                if 'content' in result:
                    logger.info(f"  - Text content count: {len(result['content'].get('text_content', []))}")
                
                results.append({
                    "filename": file.filename,
                    "status": "processed",
                    "file_size": file.size,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        # Perform cross-document analysis
        cross_analysis = {
            "total_documents": len(results),
            "successful_processing": len([r for r in results if r.get("status") == "processed"]),
            "failed_processing": len([r for r in results if r.get("status") == "error"]),
            "success_rate": len([r for r in results if r.get("status") == "processed"]) / len(results) if results else 0,
            "common_themes": ["Document Analysis", "Content Processing", "PDF Extraction"],
            "persona_insights": {
                "general": {
                    "relevant_documents": len(results),
                    "key_insights": f"Collection contains {len(results)} documents",
                    "recommendations": "Focus on documents with general content"
                }
            }
        }
        
        # Format output according to Challenge 1b specifications
        summary = {
            "total_files": len(results),
            "successful": len([r for r in results if r.get("status") == "processed"]),
            "failed": len([r for r in results if r.get("status") == "error"])
        }
        
        formatted_output = output_formatter.format_collection_output(
            task_id=task_id,
            collection_path=collection_path,
            results=results,
            cross_analysis=cross_analysis,
            summary=summary,
            persona_config={"persona_type": "general"}
        )
        
        # Save results
        output_filename = f"collection_{task_id}_analysis_{int(time.time())}.json"
        output_path = output_formatter.save_output(formatted_output, output_filename)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "message": f"Processed {len(files)} files",
            "files": [f.filename for f in files],
            "output_file": output_filename,
            "result": formatted_output
        }
        
    except Exception as e:
        logger.error(f"Error processing collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a processing task"""
    try:
        status = collection_manager.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        return status
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections():
    """List all collections"""
    try:
        return collection_manager.list_tasks()
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personas")
async def list_personas():
    """List available personas"""
    try:
        return {
            "personas": [
                {"type": "researcher", "description": "Academic researcher focused on methodology and findings"},
                {"type": "student", "description": "Student seeking educational content"},
                {"type": "business_analyst", "description": "Business professional analyzing market trends"},
                {"type": "technical_writer", "description": "Technical writer focused on documentation"},
                {"type": "legal_professional", "description": "Legal professional analyzing legal documents"},
                {"type": "medical_professional", "description": "Medical professional analyzing clinical content"}
            ]
        }
    except Exception as e:
        logger.error(f"Error listing personas: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 