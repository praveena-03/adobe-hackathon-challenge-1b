"""
Collection Manager for Multi-Collection PDF Analysis
Handles collections, cross-document analysis, and task management
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class CollectionManager:
    def __init__(self):
        self.tasks = {}
        self.collections = {}
    
    async def process_collection(self, collection_path: str, persona_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a collection of PDF files."""
        try:
            logger.info(f"Processing collection: {collection_path}")
            
            # Get all PDF files in the collection
            pdf_files = self._get_pdf_files(collection_path)
            
            if not pdf_files:
                return {"error": "No PDF files found in collection"}
            
            # Process each PDF
            results = []
            for pdf_file in pdf_files:
                try:
                    # Simulate processing (in real implementation, this would call PDFProcessor)
                    result = {
                        "filename": os.path.basename(pdf_file),
                        "status": "processed",
                        "file_size": os.path.getsize(pdf_file),
                        "processing_time": 2.5  # Simulated time
                    }
                    results.append(result)
                except Exception as e:
                    result = {
                        "filename": os.path.basename(pdf_file),
                        "status": "error",
                        "error": str(e)
                    }
                    results.append(result)
            
            # Perform cross-document analysis
            cross_analysis = self._perform_cross_analysis(results, persona_configs)
            
            return {
                "collection_path": collection_path,
                "total_files": len(pdf_files),
                "results": results,
                "cross_analysis": cross_analysis,
                "processing_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing collection: {e}")
            return {"error": str(e)}
    
    def _get_pdf_files(self, collection_path: str) -> List[str]:
        """Get all PDF files in the collection directory."""
        pdf_files = []
        try:
            for file in os.listdir(collection_path):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(collection_path, file))
        except Exception as e:
            logger.error(f"Error getting PDF files: {e}")
        
        return pdf_files
    
    def _perform_cross_analysis(self, results: List[Dict[str, Any]], persona_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform cross-document analysis."""
        try:
            # Simple cross-document analysis
            successful_files = [r for r in results if r.get("status") == "processed"]
            failed_files = [r for r in results if r.get("status") == "error"]
            
            analysis = {
                "total_documents": len(results),
                "successful_processing": len(successful_files),
                "failed_processing": len(failed_files),
                "success_rate": len(successful_files) / len(results) if results else 0,
                "common_themes": self._extract_common_themes(successful_files),
                "persona_insights": self._analyze_for_personas(successful_files, persona_configs)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in cross analysis: {e}")
            return {"error": str(e)}
    
    def _extract_common_themes(self, files: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes across documents."""
        # Simple theme extraction (in real implementation, this would analyze content)
        themes = ["Document Analysis", "Content Processing", "PDF Extraction"]
        return themes[:3]
    
    def _analyze_for_personas(self, files: List[Dict[str, Any]], persona_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collection for different personas."""
        try:
            persona_insights = {}
            
            for config in persona_configs:
                persona_type = config.get("persona_type", "general")
                persona_insights[persona_type] = {
                    "relevant_documents": len(files),
                    "key_insights": f"Collection contains {len(files)} documents relevant for {persona_type}",
                    "recommendations": f"Focus on documents with {persona_type}-specific content"
                }
            
            return persona_insights
            
        except Exception as e:
            logger.error(f"Error in persona analysis: {e}")
            return {}
    
    def create_task(self, task_id: str, collection_path: str) -> None:
        """Create a new processing task."""
        self.tasks[task_id] = {
            "status": "created",
            "collection_path": collection_path,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update_task_status(self, task_id: str, status: str, result_path: Optional[str] = None) -> None:
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            if result_path:
                self.tasks[task_id]["result_path"] = result_path
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks."""
        return [
            {
                "task_id": task_id,
                **task_data
            }
            for task_id, task_data in self.tasks.items()
        ] 