"""
Builder for chunk metadata.

This module provides tools for creating and manipulating chunk metadata
for semantic chunking systems.
"""
import uuid
import hashlib
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
from .utils import str_to_list, list_to_str, to_flat_dict, from_flat_dict

from .semantic_chunk import (
    SemanticChunk, 
    ChunkType, 
    ChunkRole, 
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics
)
from .data_types import LanguageEnum
# Если потребуется фильтр — импортировать так:
# from .chunk_query import ChunkQuery

from chunk_metadata_adapter.utils import ChunkId


class ChunkMetadataBuilder:
    """
    Builder for universal chunk metadata.
    
    Used after chunk text is formed to augment it with metadata fields:
    - uuid, sha256, created_at
    - project, status, role, tags, etc.
    
    Supports lifecycle states of data:
    - RAW: initial ingestion of unprocessed data
    - CLEANED: data that has been cleaned and preprocessed
    - VERIFIED: data verified against rules and standards
    - VALIDATED: data validated with cross-references and context
    - RELIABLE: data marked as reliable and ready for use
    
    Supports both flat and structured formats.
    """
    def __init__(
        self, 
        project: Optional[str] = None, 
        unit_id: Optional[str] = None,
        chunking_version: str = "1.0"
    ):
        """
        Initialize a new metadata builder.
        
        Args:
            project: Optional project identifier
            unit_id: Optional identifier for the chunking unit/service
            chunking_version: Version of chunking algorithm used
        """
        self.project = project
        self.unit_id = unit_id if unit_id is not None else ChunkId.default_value()
        self.chunking_version = chunking_version

    def generate_uuid(self) -> str:
        """Generate a new UUIDv4 string"""
        return str(uuid.uuid4())

    def compute_sha256(self, text: str) -> str:
        """Compute SHA256 hash of the given text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO8601 format with UTC timezone"""
        return datetime.now(timezone.utc).isoformat()

    def build_flat_metadata(
        self, *,
        text: Optional[str] = None,
        body: str,
        source_id: str,
        ordinal: int,
        type: Union[str, ChunkType],
        language: str,
        source_path: Optional[str] = None,
        source_lines_start: Optional[int] = None,
        source_lines_end: Optional[int] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        role: Optional[Union[str, ChunkRole]] = None,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        link_parent: Optional[str] = None,
        link_related: Optional[str] = None,
        status: Union[str, ChunkStatus] = ChunkStatus.RAW,
        coverage: Optional[float] = None,
        cohesion: Optional[float] = None,
        boundary_prev: Optional[float] = None,
        boundary_next: Optional[float] = None,
        # бизнес-поля
        category: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
        is_public: Optional[bool] = None,
        source: Optional[str] = None,
        tokens: Optional[int] = None,
        block_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build chunk metadata in a flat dictionary format.
        
        Args:
            body: Raw/original content of the chunk (before cleaning)
            text: Cleaned/normalized content of the chunk
            source_id: Identifier of the source (file, document, dialogue)
            ordinal: Order of the chunk within the source
            type: Type of the chunk (see ChunkType)
            language: Programming or natural language of the content
            source_path: Optional path to the source file
            source_lines_start: Start line in source file
            source_lines_end: End line in source file
            summary: Brief summary of the chunk content
            tags: List of tags
            role: Role of the content creator
            task_id: Task identifier
            subtask_id: Subtask identifier
            link_parent: UUID of the parent chunk
            link_related: UUID of a related chunk
            status: Processing status of the chunk (default: RAW for initial data ingestion)
                   See ChunkStatus for lifecycle states (RAW, CLEANED, VERIFIED, VALIDATED, RELIABLE)
            Бизнес-поля:
            - category: Optional[str]
            - title: Optional[str]
            - year: Optional[int]
            - is_public: Optional[bool]
            - source: Optional[str]
            Если поле не указано или пустое — будет None.
            
        Returns:
            Dictionary with flat metadata
        """
        # Verify UUIDs
        if not isinstance(source_id, str) or not uuid.UUID(source_id, version=4):
            raise ValueError(f"source_id must be a valid UUIDv4 string: {source_id}")
            
        if link_parent is not None and (not isinstance(link_parent, str) or not uuid.UUID(link_parent, version=4)):
            raise ValueError(f"link_parent must be a valid UUIDv4 string: {link_parent}")
            
        if link_related is not None and (not isinstance(link_related, str) or not uuid.UUID(link_related, version=4)):
            raise ValueError(f"link_related must be a valid UUIDv4 string: {link_related}")
        
        # Validate coverage
        if coverage is not None:
            try:
                cov = float(coverage)
            except Exception:
                raise ValueError(f"coverage must be a float in [0, 1], got: {coverage}")
            if not (0 <= cov <= 1):
                raise ValueError(f"coverage must be in [0, 1], got: {coverage}")
            coverage = cov
        
        # Convert enum types to string values if needed
        if isinstance(type, ChunkType):
            chunk_type_enum = type
            type = type.value
        else:
            chunk_type_enum = ChunkType(type)
        if isinstance(role, ChunkRole):
            role = role.value
        if isinstance(status, ChunkStatus):
            status = status.value
            
        # Compute is_code_chunk based on type and language
        language_enum = LanguageEnum(language) if language else None
        is_code_chunk = (
            chunk_type_enum == ChunkType.CODE_BLOCK or
            (language_enum and LanguageEnum.is_programming_language(language_enum))
        )
            
        # Приведение text/body к единому правилу
        if text in (None, "") and body not in (None, ""):
            text = body
        elif body in (None, "") and text not in (None, ""):
            body = text

        # tags should be a list of strings
        if tags is not None and not isinstance(tags, list):
            raise ValueError(f"tags must be a list of strings or None, got: {tags.__class__.__name__}")
        if tags:
            tags = list_to_str(tags, separator=',', allow_none=True)

        return {
            "uuid": self.generate_uuid(),
            "source_id": source_id,
            "ordinal": ordinal,
            "sha256": self.compute_sha256(text),
            "body": body if body else None,
            "text": text,
            "summary": summary if summary else None,
            "language": language,
            "type": type,
            "source_path": source_path if source_path else None,
            "source_lines_start": source_lines_start,
            "source_lines_end": source_lines_end,
            "project": self.project if self.project else None,
            "task_id": task_id if task_id else None,
            "subtask_id": subtask_id if subtask_id else None,
            "status": status,
            "unit_id": self.unit_id if self.unit_id else None,
            "created_at": self._get_iso_timestamp(),
            "tags": tags,
            "role": role if role else None,
            "link_parent": link_parent,
            "link_related": link_related,
            "quality_score": None,
            "coverage": coverage,
            "cohesion": cohesion,
            "boundary_prev": boundary_prev,
            "boundary_next": boundary_next,
            "used_in_generation": False,
            "feedback_accepted": 0,
            "feedback_rejected": 0,
            "category": category if category else None,
            "title": title if title else None,
            "year": year if year is not None else None,
            "is_public": is_public if is_public is not None else None,
            "source": source if source else None,
            "tokens": tokens if tokens is not None else None,
            "block_type": block_type if block_type else None,
            "is_code_chunk": "true" if is_code_chunk else "false",  # Flat format uses string
        }
        
    # Alias for backward compatibility
    build_metadata = build_flat_metadata

    def build_semantic_chunk(
        self, *,
        chunk_uuid: Optional[str] = None,
        text: Optional[str] = None,
        body: str,
        language: str,
        chunk_type: Union[str, ChunkType],
        source_id: Optional[str] = None,
        summary: Optional[str] = None,
        role: Optional[Union[str, ChunkRole]] = None,
        source_path: Optional[str] = None,
        source_lines: Optional[List[int]] = None,
        ordinal: Optional[int] = None,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        links: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Union[str, ChunkStatus] = ChunkStatus.RAW,
        metrics: Optional[ChunkMetrics] = None,
        quality_score: Optional[float] = None,
        coverage: Optional[float] = None,
        cohesion: Optional[float] = None,
        boundary_prev: Optional[float] = None,
        boundary_next: Optional[float] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        # бизнес-поля
        category: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
        is_public: Optional[bool] = None,
        source: Optional[str] = None,
        sha256: Optional[str] = None,
        tokens: Optional[List[str]] = None,
        block_type: Optional[str] = None,
    ) -> SemanticChunk:
        """
        Build a fully-structured SemanticChunk object.
        
        Args:
            body: Raw/original content of the chunk (before cleaning)
            text: Cleaned/normalized content of the chunk
            language: Programming or natural language of the content
            chunk_type: Type of the chunk
            source_id: Optional identifier of the source
            summary: Brief summary of the chunk content
            role: Role of the content creator
            source_path: Optional path to the source file
            source_lines: List of line numbers [start, end]
            ordinal: Order of the chunk within the source
            task_id: Task identifier
            subtask_id: Subtask identifier
            links: List of links to other chunks (format: "relation:uuid")
            tags: List of tags
            status: Processing status of the chunk (default: RAW for initial data ingestion)
                   The data lifecycle includes these states:
                   - RAW: Initial raw data as ingested into the system
                   - CLEANED: Data after cleaning and preprocessing
                   - VERIFIED: Data verified against rules and standards
                   - VALIDATED: Data validated with cross-references
                   - RELIABLE: Data ready for use in critical systems
            start: Start offset of the chunk in the source text (in bytes or characters)
            end: End offset of the chunk in the source text (in bytes or characters)
            Бизнес-поля:
            - category: Optional[str]
            - title: Optional[str]
            - year: Optional[int]
            - is_public: Optional[bool]
            - source: Optional[str]
            Если поле не указано или пустое — будет None.
            
        Returns:
            Fully populated SemanticChunk instance
        """
        # Проверка типов для tags и links (сначала проверяем типы!)
        if tags is not None and not isinstance(tags, list):
            raise ValueError("tags must be a list of strings, got: {}".format(type(tags)))
        if links is not None and not isinstance(links, list):
            raise ValueError("links must be a list of strings, got: {}".format(type(links)))
        
        # Verify UUIDs
        if source_id is not None and (not isinstance(source_id, str) or not uuid.UUID(source_id, version=4)):
            raise ValueError(f"source_id must be a valid UUIDv4 string: {source_id}")
            
        # Validate links format and UUIDs
        if links:
            for link in links:
                parts = link.split(":", 1)
                if len(parts) != 2 or not parts[0] or not parts[1]:
                    raise ValueError(f"Link must follow 'relation:uuid' format: {link}")
                try:
                    uuid.UUID(parts[1], version=4)
                except (ValueError, AttributeError):
                    raise ValueError(f"Invalid UUID4 in link: {link}")
        
        # Convert string types to enums if needed
        if isinstance(chunk_type, str):
            chunk_type = ChunkType(chunk_type)
        if isinstance(role, str) and role:
            role = ChunkRole(role)
        if isinstance(status, str):
            # Case-insensitive mapping handled by Enum _missing_
            status = ChunkStatus(status)
            
        # Prepare metrics
        if metrics is None:
            metrics = ChunkMetrics(
                quality_score=quality_score,
                coverage=coverage,
                cohesion=cohesion,
                boundary_prev=boundary_prev,
                boundary_next=boundary_next,
                tokens=tokens,
            )
        elif tokens is not None:
            metrics.tokens = tokens

        # Явно приводим опциональные строковые поля к валидной строке, если пусто
        def valid_str(val, min_len):
            return val if val is not None and val != '' else 'x' * min_len
        project = valid_str(self.project, 1) if self.project is not None else ""
        # UUID4 автозаполнение
        def valid_uuid(val):
            try:
                if val and isinstance(val, str):
                    import re
                    UUID4_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
                    if UUID4_PATTERN.match(val):
                        return val
                return str(uuid.uuid4())
            except Exception:
                return str(uuid.uuid4())
        unit_id = valid_uuid(self.unit_id) if self.unit_id is not None else str(uuid.uuid4())
        task_id = valid_uuid(task_id) if task_id is not None else str(uuid.uuid4())
        subtask_id = valid_uuid(subtask_id) if subtask_id is not None else str(uuid.uuid4())
        # Приведение text/body к единому правилу
        if text in (None, "") and body not in (None, ""):
            text = body
        elif body in (None, "") and text not in (None, ""):
            body = text
        body = valid_str(body, 1)
        summary = valid_str(summary, 1)
        source_path = valid_str(source_path, 1)
        
        chunking_version = valid_str(self.chunking_version, 1) if self.chunking_version is not None else "1.0"
        if tags is None:
            tags = []
        if isinstance(tags, str):
            tags = str_to_list(tags, separator=',', allow_none=True)
        elif not isinstance(tags, list):
            raise ValueError(f"tags must be a list of strings, got: {type(tags)}")

        return SemanticChunk(
            uuid=chunk_uuid if chunk_uuid is not None else self.generate_uuid(),
            source_id=source_id,
            project=project,
            task_id=task_id,
            subtask_id=subtask_id,
            unit_id=unit_id,
            type=chunk_type,
            role=role,
            language=language,
            body=body,
            text=text,
            summary=summary,
            source_path=source_path,
            source_lines=source_lines,
            ordinal=ordinal,
            sha256=sha256 if sha256 is not None else self.compute_sha256(text),
            chunking_version=chunking_version,
            status=status,
            links=links or [],
            tags=tags,
            metrics=metrics if metrics is not None else ChunkMetrics(),
            created_at=self._get_iso_timestamp(),
            start=start,
            end=end,
            category=category if category else None,
            title=title if title else None,
            year=year if year is not None else None,
            is_public=is_public if is_public is not None else None,
            source=source if source else None,
            block_type=block_type if block_type else None,
        )

    def flat_to_semantic(self, flat_chunk: Dict[str, Any]) -> SemanticChunk:
        """Convert flat dictionary metadata to SemanticChunk model (обёртка над SemanticChunk.from_flat_dict)."""
        return SemanticChunk.from_flat_dict(flat_chunk)

    def semantic_to_flat(self, chunk: SemanticChunk) -> Dict[str, Any]:
        """Convert SemanticChunk model to flat dictionary format (обёртка над chunk.to_flat_dict())."""
        d = chunk.to_flat_dict()
        # tags: List[str] -> str (для обратной совместимости flat-словаря)
        if "tags" in d and isinstance(d["tags"], list):
            d["tags"] = ",".join(d["tags"])
        # link_parent/link_related: если есть в links, выставить uuid, иначе None
        link_parent = None
        link_related = None
        links = getattr(chunk, "links", None)
        if links:
            for l in links:
                if l.startswith("parent:"):
                    link_parent = l.split(":", 1)[1]
                elif l.startswith("related:"):
                    link_related = l.split(":", 1)[1]
        d["link_parent"] = link_parent
        d["link_related"] = link_related
        return d

    def semantic_to_json_dict(self, chunk: SemanticChunk) -> dict:
        """Convert SemanticChunk to JSON-serializable dict (обёртка над chunk.model_dump())."""
        return chunk.model_dump()

    def json_dict_to_semantic(self, d: dict) -> SemanticChunk:
        """Convert JSON-serializable dict to SemanticChunk (обёртка над SemanticChunk(**d))."""
        return SemanticChunk(**d)
