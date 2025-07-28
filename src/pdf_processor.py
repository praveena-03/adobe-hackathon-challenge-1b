"""
PDF Processing Module using Unstructured Library
Advanced PDF analysis with structured extraction
"""

import os
import fitz  # PyMuPDF
import PyPDF2
import pdfplumber
from typing import Dict, List, Any, Optional
from loguru import logger
import re
import tempfile

class PDFProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_retries = 3

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file and extract structured information with robust error handling."""
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                return self._create_error_result("File not found")
            
            if not os.access(file_path, os.R_OK):
                return self._create_error_result("File not readable")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return self._create_error_result("Empty file")
            
            # Try multiple PDF processing methods for maximum compatibility
            result = self._process_with_fallback(file_path)
            
            # Ensure we always return a valid structure
            if not result:
                result = self._create_error_result("Processing failed")
            
            return result

        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return self._create_error_result(str(e))

    def _process_with_fallback(self, file_path: str) -> Dict[str, Any]:
        """Try multiple PDF processing methods for maximum compatibility."""
        
        # Method 1: Try PyMuPDF (fitz) - most robust
        try:
            result = self._process_with_fitz(file_path)
            if result and not result.get("error"):
                return result
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")
        
        # Method 2: Try PyPDF2 - good for metadata
        try:
            result = self._process_with_pypdf2(file_path)
            if result and not result.get("error"):
                return result
        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")
        
        # Method 3: Try pdfplumber - good for text extraction
        try:
            result = self._process_with_pdfplumber(file_path)
            if result and not result.get("error"):
                return result
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        
        # Method 4: Basic file analysis as last resort
        try:
            result = self._process_basic(file_path)
            if result and not result.get("error"):
                return result
        except Exception as e:
            logger.warning(f"Basic processing failed: {e}")
        
        return self._create_error_result("All processing methods failed")

    def _process_with_fitz(self, file_path: str) -> Dict[str, Any]:
        """Process using PyMuPDF (fitz) - most comprehensive method."""
        try:
            doc = fitz.open(file_path)
            
            # Check if PDF is encrypted
            if doc.needs_pass:
                doc.close()
                return self._create_error_result("Password-protected PDF")
            
            # Extract metadata
            metadata = self._extract_metadata_fitz(doc)
            
            # Extract structure
            structure = self._extract_structure_fitz(doc)
            
            # Extract content
            content = self._extract_content_fitz(doc)
            
            doc.close()
            
            return {
                "metadata": metadata,
                "structure": structure,
                "content": content,
                "processing_method": "PyMuPDF"
            }
            
        except Exception as e:
            logger.error(f"PyMuPDF processing error: {e}")
            return self._create_error_result(f"PyMuPDF error: {str(e)}")

    def _process_with_pypdf2(self, file_path: str) -> Dict[str, Any]:
        """Process using PyPDF2 - good for metadata and basic text."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    return self._create_error_result("Password-protected PDF")
                
                metadata = self._extract_metadata_pypdf2(pdf_reader)
                structure = self._extract_structure_pypdf2(pdf_reader)
                content = self._extract_content_pypdf2(pdf_reader)
                
                return {
                    "metadata": metadata,
                    "structure": structure,
                    "content": content,
                    "processing_method": "PyPDF2"
                }
                
        except Exception as e:
            logger.error(f"PyPDF2 processing error: {e}")
            return self._create_error_result(f"PyPDF2 error: {str(e)}")

    def _process_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Process using pdfplumber - excellent for text extraction."""
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = self._extract_metadata_pdfplumber(pdf)
                structure = self._extract_structure_pdfplumber(pdf)
                content = self._extract_content_pdfplumber(pdf)
                
                return {
                    "metadata": metadata,
                    "structure": structure,
                    "content": content,
                    "processing_method": "pdfplumber"
                }
                
        except Exception as e:
            logger.error(f"pdfplumber processing error: {e}")
            return self._create_error_result(f"pdfplumber error: {str(e)}")

    def _process_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic file analysis as last resort."""
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            return {
                "metadata": {
                    "title": filename,
                    "author": "Unknown",
                    "subject": "PDF Document",
                    "creator": "Unknown",
                    "producer": "Unknown",
                    "pages": 1,
                    "file_size": file_size
                },
                "structure": {
                    "sections": [{"title": "Document Content", "page": 1, "font_size": 12}],
                    "total_pages": 1
                },
                "content": {
                    "text_content": [{"text": "PDF content could not be extracted", "page": 1}],
                    "total_paragraphs": 1
                },
                "processing_method": "Basic",
                "warning": "Limited content extraction"
            }
            
        except Exception as e:
            logger.error(f"Basic processing error: {e}")
            return self._create_error_result(f"Basic processing error: {str(e)}")

    def _extract_metadata_fitz(self, doc) -> Dict[str, Any]:
        """Extract metadata using PyMuPDF."""
        try:
            metadata = doc.metadata
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "pages": len(doc),
                "file_size": os.path.getsize(doc.name) if hasattr(doc, 'name') else 0
            }
        except:
            return self._get_default_metadata()

    def _extract_metadata_pypdf2(self, pdf_reader) -> Dict[str, Any]:
        """Extract metadata using PyPDF2."""
        try:
            info = pdf_reader.metadata or {}
            return {
                "title": info.get('/Title', ''),
                "author": info.get('/Author', ''),
                "subject": info.get('/Subject', ''),
                "creator": info.get('/Creator', ''),
                "producer": info.get('/Producer', ''),
                "pages": len(pdf_reader.pages),
                "file_size": 0  # Will be set by caller
            }
        except:
            return self._get_default_metadata()

    def _extract_metadata_pdfplumber(self, pdf) -> Dict[str, Any]:
        """Extract metadata using pdfplumber."""
        try:
            return {
                "title": "PDF Document",
                "author": "Unknown",
                "subject": "PDF Content",
                "creator": "pdfplumber",
                "producer": "Unknown",
                "pages": len(pdf.pages),
                "file_size": 0
            }
        except:
            return self._get_default_metadata()

    def _extract_structure_fitz(self, doc) -> Dict[str, Any]:
        """Extract structure using PyMuPDF."""
        try:
            sections = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text and len(text) > 5:  # Potential section header
                                    font_size = span["size"]
                                    if font_size > 11:  # Likely a header
                                        sections.append({
                                            "title": text[:100],  # Limit length
                                            "page": page_num + 1,
                                            "font_size": font_size
                                        })
                                        break  # One section per page to avoid spam
            
            return {
                "sections": sections[:10],  # Limit to first 10 sections
                "total_pages": len(doc)
            }
        except:
            return {"sections": [], "total_pages": len(doc)}

    def _extract_structure_pypdf2(self, pdf_reader) -> Dict[str, Any]:
        """Extract structure using PyPDF2."""
        try:
            sections = []
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text:
                    # Simple section detection
                    lines = text.split('\n')
                    for line in lines[:5]:  # Check first 5 lines
                        if len(line.strip()) > 10 and len(line.strip()) < 100:
                            sections.append({
                                "title": line.strip()[:100],
                                "page": page_num + 1,
                                "font_size": 12
                            })
                            break
            
            return {
                "sections": sections[:10],
                "total_pages": len(pdf_reader.pages)
            }
        except:
            return {"sections": [], "total_pages": len(pdf_reader.pages)}

    def _extract_structure_pdfplumber(self, pdf) -> Dict[str, Any]:
        """Extract structure using pdfplumber."""
        try:
            sections = []
            for page_num, page in enumerate(pdf.pages):
                if page.extract_text():
                    sections.append({
                        "title": f"Page {page_num + 1} Content",
                        "page": page_num + 1,
                        "font_size": 12
                    })
            
            return {
                "sections": sections[:10],
                "total_pages": len(pdf.pages)
            }
        except:
            return {"sections": [], "total_pages": len(pdf.pages)}

    def _extract_content_fitz(self, doc) -> Dict[str, Any]:
        """Extract content using PyMuPDF."""
        try:
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    # Split into paragraphs and clean
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for paragraph in paragraphs[:3]:  # Limit to first 3 paragraphs per page
                        if len(paragraph) > 20:  # Only meaningful paragraphs
                            text_content.append({
                                "text": paragraph[:500],  # Limit length
                                "page": page_num + 1
                            })
            
            return {
                "text_content": text_content,
                "total_paragraphs": len(text_content)
            }
        except:
            return {"text_content": [], "total_paragraphs": 0}

    def _extract_content_pypdf2(self, pdf_reader) -> Dict[str, Any]:
        """Extract content using PyPDF2."""
        try:
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text:
                    # Split into paragraphs
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for paragraph in paragraphs[:3]:
                        if len(paragraph) > 20:
                            text_content.append({
                                "text": paragraph[:500],
                                "page": page_num + 1
                            })
            
            return {
                "text_content": text_content,
                "total_paragraphs": len(text_content)
            }
        except:
            return {"text_content": [], "total_paragraphs": 0}

    def _extract_content_pdfplumber(self, pdf) -> Dict[str, Any]:
        """Extract content using pdfplumber."""
        try:
            text_content = []
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for paragraph in paragraphs[:3]:
                        if len(paragraph) > 20:
                            text_content.append({
                                "text": paragraph[:500],
                                "page": page_num + 1
                            })
            
            return {
                "text_content": text_content,
                "total_paragraphs": len(text_content)
            }
        except:
            return {"text_content": [], "total_paragraphs": 0}

    def _get_default_metadata(self) -> Dict[str, Any]:
        """Get default metadata when extraction fails."""
        return {
            "title": "PDF Document",
            "author": "Unknown",
            "subject": "PDF Content",
            "creator": "PDF Processor",
            "producer": "Unknown",
            "pages": 1,
            "file_size": 0
        }

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "metadata": self._get_default_metadata(),
            "structure": {"sections": [], "total_pages": 1},
            "content": {"text_content": [], "total_paragraphs": 0},
            "error": error_message,
            "processing_method": "Error"
        } 