"""Pydantic models for code structure and AST parsing."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class CodeSymbol(BaseModel):
    """Code symbol (class, function, method, endpoint)."""
    name: str
    symbol_type: str  # class, function, method, component
    line_number: int = 0
    docstring: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)


class FileCodeAnalysis(BaseModel):
    """Analysis of a single source code file."""
    file_path: str
    language: str
    classes: List[CodeSymbol] = Field(default_factory=list)
    functions: List[CodeSymbol] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    internal_imports: List[str] = Field(default_factory=list)
    external_imports: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    is_entry_point: bool = False
    lines_of_code: int = 0


class CodeStructureData(BaseModel):
    """Structured code architecture representation."""
    source_directories: List[str] = Field(default_factory=list)
    total_modules_analyzed: int = 0
    classes_count: int = 0
    functions_count: int = 0
    modules: List[str] = Field(default_factory=list)
    imports_map: Dict[str, List[str]] = Field(default_factory=dict)
    detected_entry_points: List[str] = Field(default_factory=list)
    file_analyses: List[FileCodeAnalysis] = Field(default_factory=list)
    hierarchical_summary: str = ""
