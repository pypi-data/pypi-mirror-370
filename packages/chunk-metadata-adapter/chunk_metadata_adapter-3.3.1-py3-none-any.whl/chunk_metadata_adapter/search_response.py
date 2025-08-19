"""
Search response handling for BM25 and hybrid search results.

This module provides classes for handling search responses from the server,
including BM25 scores, semantic scores, and hybrid search results.

Key features:
- SearchResult: Individual search result with scores
- ChunkQueryResponse: Response handler for API responses
- Score normalization and validation
- Error handling for server responses

Author: Development Team
Created: 2024-01-20
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json

from .semantic_chunk import SemanticChunk


@dataclass
class SearchResult:
    """
    Individual search result with scores and metadata.
    
    This class represents a single search result from BM25 or hybrid search,
    containing the chunk data, various scores, and additional metadata.
    
    Attributes:
        chunk_id: Unique identifier of the chunk
        chunk: SemanticChunk object with chunk data
        bm25_score: BM25 relevance score (0.0 to 1.0)
        semantic_score: Semantic similarity score (0.0 to 1.0)
        hybrid_score: Combined hybrid score (0.0 to 1.0)
        rank: Position in search results (1-based)
        matched_fields: List of fields that matched the query
        highlights: Highlighted text snippets from matched fields
        search_metadata: Additional search metadata
    """
    
    chunk_id: str
    chunk: SemanticChunk
    bm25_score: Optional[float] = None
    semantic_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    rank: int = 0
    matched_fields: Optional[List[str]] = None
    highlights: Optional[Dict[str, List[str]]] = None
    search_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate search result data."""
        self._validate_scores()
        self._validate_rank()
    
    def _validate_scores(self) -> None:
        """Validate score values are in valid range."""
        for score_name, score_value in [
            ("bm25_score", self.bm25_score),
            ("semantic_score", self.semantic_score),
            ("hybrid_score", self.hybrid_score)
        ]:
            if score_value is not None and (score_value < 0.0 or score_value > 1.0):
                raise ValueError(f"{score_name} must be between 0.0 and 1.0, got: {score_value}")
    
    def _validate_rank(self) -> None:
        """Validate rank is non-negative."""
        if self.rank < 0:
            raise ValueError(f"Rank must be non-negative, got: {self.rank}")
    
    @property
    def primary_score(self) -> Optional[float]:
        """
        Get the primary score for ranking.
        
        Returns:
            float: Primary score (hybrid_score if available, otherwise bm25_score)
        """
        if self.hybrid_score is not None:
            return self.hybrid_score
        elif self.bm25_score is not None:
            return self.bm25_score
        elif self.semantic_score is not None:
            return self.semantic_score
        else:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search result to dictionary.
        
        Returns:
            dict: Dictionary representation of the search result
        """
        result = {
            "chunk_id": self.chunk_id,
            "chunk": self.chunk.model_dump(),
            "rank": self.rank
        }
        
        if self.bm25_score is not None:
            result["bm25_score"] = self.bm25_score
        if self.semantic_score is not None:
            result["semantic_score"] = self.semantic_score
        if self.hybrid_score is not None:
            result["hybrid_score"] = self.hybrid_score
        if self.matched_fields:
            result["matched_fields"] = self.matched_fields
        if self.highlights:
            result["highlights"] = self.highlights
        if self.search_metadata:
            result["search_metadata"] = self.search_metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """
        Create SearchResult from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            SearchResult: Search result object
        """
        # Extract chunk data
        chunk_data = data.get("chunk", {})
        chunk = SemanticChunk(**chunk_data)
        
        return cls(
            chunk_id=data["chunk_id"],
            chunk=chunk,
            bm25_score=data.get("bm25_score"),
            semantic_score=data.get("semantic_score"),
            hybrid_score=data.get("hybrid_score"),
            rank=data.get("rank", 0),
            matched_fields=data.get("matched_fields"),
            highlights=data.get("highlights"),
            search_metadata=data.get("search_metadata")
        )


class ChunkQueryResponse:
    """
    Response handler for ChunkQuery API responses.
    
    This class handles parsing and validation of server responses
    for BM25 and hybrid search operations.
    
    Features:
    - Response structure validation
    - Search result parsing
    - Error handling
    - Metadata extraction
    """
    
    def __init__(self, response_data: Dict[str, Any]):
        """
        Initialize response handler.
        
        Args:
            response_data: Raw response data from server
        """
        self.response_data = response_data
        self._validate_response()
        self._parse_results()
    
    def _validate_response(self) -> None:
        """
        Validate server response structure.
        
        Raises:
            ValueError: If response structure is invalid
        """
        if 'status' not in self.response_data:
            raise ValueError("Missing required field in response: status")
        
        if self.response_data['status'] not in ['success', 'error']:
            raise ValueError(f"Invalid status in response: {self.response_data['status']}")
        
        # Only require 'data' field for success responses
        if self.response_data['status'] == 'success' and 'data' not in self.response_data:
            raise ValueError("Missing required field in response: data")
    
    def _parse_results(self) -> None:
        """Parse search results from response data."""
        self.results: List[SearchResult] = []
        self.metadata: Dict[str, Any] = {}
        
        if self.response_data['status'] == 'success':
            data = self.response_data['data']
            
            # Parse search results
            if 'results' in data:
                for result_data in data['results']:
                    try:
                        result = SearchResult.from_dict(result_data)
                        self.results.append(result)
                    except Exception as e:
                        # Log error but continue parsing other results
                        print(f"Error parsing search result: {e}")
            
            # Parse metadata
            self.metadata = data.get('metadata', {})
            
            # Parse search statistics
            self.total_results = data.get('total_results', len(self.results))
            self.search_time = data.get('search_time', 0.0)
            self.query_time = data.get('query_time', 0.0)
        else:
            # Handle error response
            self.total_results = 0
            self.search_time = 0.0
            self.query_time = 0.0
            # Store error message in metadata for access
            self.metadata = {'error': self.response_data.get('error', 'Unknown error')}
    
    @property
    def is_success(self) -> bool:
        """
        Check if response indicates success.
        
        Returns:
            bool: True if response is successful
        """
        return self.response_data['status'] == 'success'
    
    @property
    def error_message(self) -> Optional[str]:
        """
        Get error message if response failed.
        
        Returns:
            str: Error message or None if successful
        """
        if not self.is_success:
            return self.response_data.get('error', 'Unknown error')
        return None
    
    def get_results(self, limit: Optional[int] = None) -> List[SearchResult]:
        """
        Get search results, optionally limited.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List[SearchResult]: List of search results
        """
        if limit is None:
            return self.results
        else:
            return self.results[:limit]
    
    def get_top_results(self, n: int = 10) -> List[SearchResult]:
        """
        Get top N results by score.
        
        Args:
            n: Number of top results to return
            
        Returns:
            List[SearchResult]: Top N results sorted by score
        """
        sorted_results = sorted(
            self.results,
            key=lambda r: r.primary_score or 0.0,
            reverse=True
        )
        return sorted_results[:n]
    
    def get_results_by_score_threshold(self, threshold: float) -> List[SearchResult]:
        """
        Get results above score threshold.
        
        Args:
            threshold: Minimum score threshold (0.0 to 1.0)
            
        Returns:
            List[SearchResult]: Results with score >= threshold
        """
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got: {threshold}")
        
        return [
            result for result in self.results
            if result.primary_score is not None and result.primary_score >= threshold
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get search statistics.
        
        Returns:
            dict: Search statistics
        """
        if not self.is_success:
            return {"error": self.error_message}
        
        stats = {
            "total_results": self.total_results,
            "returned_results": len(self.results),
            "search_time": self.search_time,
            "query_time": self.query_time,
            "metadata": self.metadata
        }
        
        # Add score statistics if available
        scores = [r.primary_score for r in self.results if r.primary_score is not None]
        if scores:
            stats.update({
                "min_score": min(scores),
                "max_score": max(scores),
                "avg_score": sum(scores) / len(scores),
                "score_distribution": {
                    "high": len([s for s in scores if s >= 0.8]),
                    "medium": len([s for s in scores if 0.5 <= s < 0.8]),
                    "low": len([s for s in scores if s < 0.5])
                }
            })
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary.
        
        Returns:
            dict: Dictionary representation of the response
        """
        return {
            "status": self.response_data['status'],
            "results": [result.to_dict() for result in self.results],
            "statistics": self.get_statistics(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_json(cls, json_str: str) -> "ChunkQueryResponse":
        """
        Create response from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            ChunkQueryResponse: Response object
        """
        try:
            response_data = json.loads(json_str)
            return cls(response_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def to_json(self) -> str:
        """
        Convert response to JSON string.
        
        Returns:
            str: JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)


class SearchResponseBuilder:
    """
    Builder for creating search responses.
    
    This class provides a convenient way to build search responses
    for testing and development purposes.
    """
    
    def __init__(self):
        """Initialize response builder."""
        self.results: List[SearchResult] = []
        self.metadata: Dict[str, Any] = {}
        self.search_time: float = 0.0
        self.query_time: float = 0.0
    
    def add_result(self, result: SearchResult) -> "SearchResponseBuilder":
        """
        Add a search result.
        
        Args:
            result: Search result to add
            
        Returns:
            SearchResponseBuilder: Self for chaining
        """
        self.results.append(result)
        # Sort results by rank after adding
        self.results.sort(key=lambda r: r.rank)
        return self
    
    def set_metadata(self, metadata: Dict[str, Any]) -> "SearchResponseBuilder":
        """
        Set response metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            SearchResponseBuilder: Self for chaining
        """
        self.metadata = metadata
        return self
    
    def set_timing(self, search_time: float, query_time: float) -> "SearchResponseBuilder":
        """
        Set timing information.
        
        Args:
            search_time: Search execution time
            query_time: Query processing time
            
        Returns:
            SearchResponseBuilder: Self for chaining
        """
        self.search_time = search_time
        self.query_time = query_time
        return self
    
    def build(self) -> ChunkQueryResponse:
        """
        Build the search response.
        
        Returns:
            ChunkQueryResponse: Built response object
        """
        response_data = {
            "status": "success",
            "data": {
                "results": [result.to_dict() for result in self.results],
                "metadata": self.metadata,
                "total_results": len(self.results),
                "search_time": self.search_time,
                "query_time": self.query_time
            }
        }
        
        return ChunkQueryResponse(response_data)
    
    def build_error(self, error_message: str) -> ChunkQueryResponse:
        """
        Build error response.
        
        Args:
            error_message: Error message
            
        Returns:
            ChunkQueryResponse: Error response object
        """
        response_data = {
            "status": "error",
            "error": error_message
        }
        
        return ChunkQueryResponse(response_data)
