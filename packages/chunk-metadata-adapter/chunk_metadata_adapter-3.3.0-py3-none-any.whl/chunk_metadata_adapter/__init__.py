"""
Chunk Metadata Adapter - A package for managing metadata for chunked content.

This package provides tools for creating, managing, and converting metadata 
for chunks of content in various systems, including RAG pipelines, document 
processing, and machine learning training datasets.
"""

# Core classes
from .semantic_chunk import SemanticChunk, ChunkMetrics, FeedbackMetrics
from .chunk_query import ChunkQuery
from .metadata_builder import ChunkMetadataBuilder

# Data types and enums
from .data_types import (
    ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum,
    ComparableEnum
)

# AST and parsing
from .ast import (
    ASTNode, ASTVisitor, ASTValidator, ASTAnalyzer,
    FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    ASTNodeFactory,
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string
)
from .filter_parser import FilterParser, FilterParseError
from .filter_grammar import FILTER_GRAMMAR
from .ast_optimizer import ASTOptimizer, optimize_ast
from .filter_executor import FilterExecutor

# Search response handling
from .search_response import SearchResult, ChunkQueryResponse, SearchResponseBuilder

# Hybrid search functionality
from .hybrid_search import (
    HybridStrategy, HybridSearchConfig, HybridSearchHelper, HybridSearchValidator
)

# Validation and analysis
from .query_validator import QueryValidator, ValidationResult
from .complexity_analyzer import ComplexityAnalyzer, analyze_complexity
from .security_validator import SecurityValidator
from .performance_analyzer import PerformanceAnalyzer

# Examples
from .examples_module import (
    example_basic_flat_metadata,
    example_structured_chunk,
    example_conversion_between_formats,
    example_chain_processing,
    example_data_lifecycle,
    example_metrics_extension,
    example_full_chain_structured_semantic_flat,
    example_is_code_detection,
    example_filter_factory_method,
    example_filter_usage
)

__version__ = "3.2.0"

__all__ = [
    # Core classes
    "SemanticChunk", "ChunkMetrics",
    "ChunkQuery", 
    "ChunkMetadataBuilder",
    
    # Data types and enums
    "ChunkType", "ChunkRole", "ChunkStatus", "BlockType", "LanguageEnum",
    "FeedbackMetrics", "ComparableEnum",
    
    # AST and parsing
    "ASTNode", "ASTVisitor", "ASTValidator", "ASTAnalyzer",
    "FieldCondition", "LogicalOperator", "ParenExpression", "TypedValue",
    "ASTNodeFactory",
    "ast_to_json", "ast_from_json", "ast_to_json_string", "ast_from_json_string",
    "FilterParser", "FilterParseError", "FILTER_GRAMMAR",
    "ASTOptimizer", "optimize_ast", "FilterExecutor",
    
    # Search response handling
    "SearchResult", "ChunkQueryResponse", "SearchResponseBuilder",
    
    # Hybrid search functionality
    "HybridStrategy", "HybridSearchConfig", "HybridSearchHelper", "HybridSearchValidator",
    
    # Validation and analysis
    "QueryValidator", "ValidationResult",
    "ComplexityAnalyzer", "analyze_complexity",
    "SecurityValidator", "PerformanceAnalyzer",
    
    # Examples
    "example_basic_flat_metadata",
    "example_structured_chunk", 
    "example_conversion_between_formats",
    "example_chain_processing",
    "example_data_lifecycle",
    "example_metrics_extension",
    "example_full_chain_structured_semantic_flat",
    "example_is_code_detection",
    "example_filter_factory_method",
    "example_filter_usage",
]
