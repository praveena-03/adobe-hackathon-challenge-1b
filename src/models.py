"""
Data models for Adobe Hackathon Challenge 1b
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class PersonaType(str, Enum):
    RESEARCHER = "researcher"
    STUDENT = "student"
    BUSINESS_ANALYST = "business_analyst"
    TECHNICAL_WRITER = "technical_writer"
    LEGAL_PROFESSIONAL = "legal_professional"
    MEDICAL_PROFESSIONAL = "medical_professional"

class PersonaConfig(BaseModel):
    """Configuration for persona-based analysis"""
    persona_type: PersonaType
    focus_areas: List[str] = Field(default_factory=list)
    expertise_level: str = Field(default="intermediate")
    analysis_depth: str = Field(default="standard")
    custom_keywords: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True

class ProcessingRequest(BaseModel):
    """Request model for processing collections"""
    collection_path: str
    persona_configs: List[PersonaConfig] = Field(default_factory=list)
    output_format: str = Field(default="json")
    include_cross_analysis: bool = Field(default=True)
    max_processing_time: Optional[int] = Field(default=60)

class ProcessingResponse(BaseModel):
    """Response model for processing results"""
    success: bool
    filename: str
    processing_time: float
    file_size: int
    result: Dict[str, Any]
    error: Optional[str] = None

class DocumentElement(BaseModel):
    """Represents a structured document element"""
    element_type: str
    text: str
    page_number: Optional[int] = None
    coordinates: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentStructure(BaseModel):
    """Represents the structure of a document"""
    title: Optional[str] = None
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    headings: List[str] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    figures: List[Dict[str, Any]] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)

class PersonaAnalysis(BaseModel):
    """Results of persona-based analysis"""
    persona_type: PersonaType
    key_insights: List[str] = Field(default_factory=list)
    relevance_score: float
    complexity_assessment: str
    recommended_actions: List[str] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
    summary: str

class CrossDocumentAnalysis(BaseModel):
    """Cross-document analysis results"""
    common_themes: List[str] = Field(default_factory=list)
    document_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge_graph: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)

class TaskStatus(BaseModel):
    """Background task status"""
    task_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[float] = None
    result_path: Optional[str] = None
    error: Optional[str] = None
    created_at: float
    updated_at: float 