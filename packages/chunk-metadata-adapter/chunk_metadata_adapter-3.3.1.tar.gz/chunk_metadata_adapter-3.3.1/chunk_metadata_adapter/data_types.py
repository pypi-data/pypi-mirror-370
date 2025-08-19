"""
Models for chunk metadata representation using Pydantic.

Бизнес-поля (Business fields) — расширяют основную модель чанка для поддержки бизнес-логики и интеграции с внешними системами.

Поля:
- category: Optional[str] — бизнес-категория записи (например, 'наука', 'программирование', 'новости'). Максимум 64 символа.
- title: Optional[str] — заголовок или краткое название записи. Максимум 256 символов.
- year: Optional[int] — год, связанный с записью (например, публикации). Диапазон: 0–2100.
- is_public: Optional[bool] — публичность записи (True/False).
- source: Optional[str] — источник данных (например, 'user', 'external', 'import'). Максимум 64 символов.
- language: str — язык содержимого (например, 'en', 'ru').
- tags: List[str] — список тегов для классификации.
- uuid: str — уникальный идентификатор (UUIDv4).
- type: str — тип чанка (например, 'Draft', 'DocBlock').
- text: str — нормализованный текст для поиска.
- body: str — исходный текст чанка.
- sha256: str — SHA256 хеш текста.
- created_at: str — ISO8601 дата создания.
- status: str — статус обработки.
- start: int — смещение начала чанка.
- end: int — смещение конца чанка.
"""
from enum import Enum
from typing import List, Dict, Optional, Union, Any, Pattern
import re
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator, field_validator, model_validator
import abc
import pydantic
from chunk_metadata_adapter.utils import get_empty_value_for_type, is_empty_value, get_base_type, get_valid_default_for_type, ChunkId, EnumBase


# UUID4 регулярное выражение для валидации
UUID4_PATTERN: Pattern = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)

# ISO 8601 с таймзоной
ISO8601_PATTERN: Pattern = re.compile(
    r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'
)


class ComparableEnum(EnumBase):
    @classmethod
    def from_string(cls, value: str) -> Optional[Enum]:
        """Converts a string to an enum member, case-insensitively."""
        raise NotImplementedError("This method must be implemented by subclasses.")

    def eqstr(self, value: Any) -> bool:
        """Compares with another value, converting string to enum first."""
        raise NotImplementedError("This method must be implemented by subclasses.")

    @classmethod
    def default_value(cls):
        """Returns the default value for the enum."""
        return None


class ChunkType(str, ComparableEnum):
    """Types of semantic chunks"""
    DOC_BLOCK = "DocBlock"
    CODE_BLOCK = "CodeBlock"
    MESSAGE = "Message"
    DRAFT = "Draft"
    TASK = "Task"
    SUBTASK = "Subtask"
    TZ = "TZ"
    COMMENT = "Comment"
    LOG = "Log"
    METRIC = "Metric"

    @classmethod
    def from_string(cls, value: str) -> Optional['ChunkType']:
        if not isinstance(value, str):
            return None
        for member in cls:
            if member.value.lower() == value.lower() or member.name.lower() == value.lower():
                return member
        return None

    def eqstr(self, value: Any) -> bool:
        if isinstance(value, str):
            enum_member = self.__class__.from_string(value)
            return self == enum_member
        return self == value

    @classmethod
    def default_value(cls):
        return cls.DOC_BLOCK


class ChunkRole(str, ComparableEnum):
    """Roles in the system"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    REVIEWER = "reviewer"
    DEVELOPER = "developer"

    @classmethod
    def default_value(cls):
        return cls.USER

    @classmethod
    def from_string(cls, value: str) -> Optional['ChunkRole']:
        if not isinstance(value, str):
            return None
        for member in cls:
            if member.value.lower() == value.lower() or member.name.lower() == value.lower():
                return member
        return None

    def eqstr(self, value: Any) -> bool:
        if isinstance(value, str):
            enum_member = self.__class__.from_string(value)
            return self == enum_member
        return self == value


class ChunkStatus(str, ComparableEnum):
    """
    Status of a chunk processing.
    
    Represents the lifecycle stages of data in the system:
    1. Initial ingestion of raw data (RAW)
    2. Data cleaning/pre-processing (CLEANED)
    3. Verification against rules and standards (VERIFIED)
    4. Validation with cross-references and context (VALIDATED)
    5. Reliable data ready for usage (RELIABLE)
    
    Also includes operational statuses for tracking processing state.
    """
    # Начальный статус для новых данных
    NEW = "new"
    
    # Статусы жизненного цикла данных
    RAW = "raw"                    # Сырые данные, как они поступили в систему
    CLEANED = "cleaned"            # Данные прошли очистку от ошибок и шума
    VERIFIED = "verified"          # Данные проверены на соответствие правилам и стандартам
    VALIDATED = "validated"        # Данные прошли валидацию с учетом контекста и перекрестных ссылок
    RELIABLE = "reliable"          # Надежные данные, готовые к использованию
    
    # Операционные статусы
    INDEXED = "indexed"            # Данные проиндексированы
    OBSOLETE = "obsolete"          # Данные устарели
    REJECTED = "rejected"          # Данные отклонены из-за критических проблем
    IN_PROGRESS = "in_progress"    # Данные в процессе обработки
    
    # Дополнительные статусы для управления жизненным циклом
    NEEDS_REVIEW = "needs_review"  # Требуется ручная проверка
    ARCHIVED = "archived"          # Данные архивированы

    @classmethod
    def from_string(cls, value: str) -> Optional['ChunkStatus']:
        if not isinstance(value, str):
            return None
        for member in cls:
            if member.value.lower() == value.lower() or member.name.lower() == value.lower():
                return member
        return None

    def eqstr(self, value: Any) -> bool:
        if isinstance(value, str):
            enum_member = self.__class__.from_string(value)
            return self == enum_member
        return self == value

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return super()._missing_(value)

    @classmethod
    def default_value(cls):
        return cls.NEW


# FeedbackMetrics moved to semantic_chunk.py to avoid duplication


class BlockType(str, ComparableEnum):
    """Типы исходных блоков для агрегации и анализа."""
    PARAGRAPH = "paragraph"
    MESSAGE = "message"
    SECTION = "section"
    OTHER = "other"

    @classmethod
    def default_value(cls):
        return cls.OTHER

    @classmethod
    def from_string(cls, value: str) -> Optional['BlockType']:
        if not isinstance(value, str):
            return None
        for member in cls:
            if member.value.lower() == value.lower() or member.name.lower() == value.lower():
                return member
        return None

    def eqstr(self, value: Any) -> bool:
        if isinstance(value, str):
            enum_member = self.__class__.from_string(value)
            return self == enum_member
        return self == value


class LanguageEnum(str, ComparableEnum):
    """Programming, natural, and formula languages supported by the system.
    
    Includes all 54 programming languages supported by guesslang, natural languages, and formula languages (e.g., LaTeX, MathML, AsciiMath, MathJax, KaTeX, SymPy).
    
    Special values:
        - UNKNOWN: Unknown or unspecified language
    
    Natural languages:
        - EN, RU, UK, DE, FR, ES, ZH, JA
    
    Programming languages:
        - Assembly, Batchfile, C, C#, C++, Clojure, CMake, COBOL, CoffeeScript, CSS, CSV, Dart, DM, Dockerfile, Elixir, Erlang, Fortran, Go, Groovy, Haskell, HTML, INI, Java, JavaScript, JSON, Julia, Kotlin, Lisp, Lua, Makefile, Markdown, Matlab, Objective-C, OCaml, Pascal, Perl, PHP, PowerShell, Prolog, Python, R, Ruby, Rust, Scala, Shell, SQL, Swift, TeX, TOML, TypeScript, Verilog, Visual Basic, XML, YAML, 1C
    
    Formula languages (for mathematical and scientific notation):
        - LATEX: LaTeX markup language for scientific documents
        - MATHML: MathML (Mathematical Markup Language)
        - ASCIIMATH: AsciiMath notation
        - MATHJAX: MathJax JavaScript display engine
        - KATEX: KaTeX JavaScript display engine
        - SYMPY: SymPy symbolic mathematics language
    """
    # Special values
    UNKNOWN = "UNKNOWN"
    
    # Natural languages
    EN = "en"
    RU = "ru"
    UK = "uk"
    DE = "de"
    FR = "fr"
    ES = "es"
    ZH = "zh"
    JA = "ja"
    
    # Programming languages from guesslang (54 languages)
    ASSEMBLY = "Assembly"
    BATCHFILE = "Batchfile"
    C = "C"
    CSHARP = "C#"
    CPP = "C++"
    CLOJURE = "Clojure"
    CMAKE = "CMake"
    COBOL = "COBOL"
    COFFEESCRIPT = "CoffeeScript"
    CSS = "CSS"
    CSV = "CSV"
    DART = "Dart"
    DM = "DM"
    DOCKERFILE = "Dockerfile"
    ELIXIR = "Elixir"
    ERLANG = "Erlang"
    FORTRAN = "Fortran"
    GO = "Go"
    GROOVY = "Groovy"
    HASKELL = "Haskell"
    HTML = "HTML"
    INI = "INI"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    JSON = "JSON"
    JULIA = "Julia"
    KOTLIN = "Kotlin"
    LISP = "Lisp"
    LUA = "Lua"
    MAKEFILE = "Makefile"
    MARKDOWN = "Markdown"
    MATLAB = "Matlab"
    OBJECTIVE_C = "Objective-C"
    OCAML = "OCaml"
    PASCAL = "Pascal"
    PERL = "Perl"
    PHP = "PHP"
    POWERSHELL = "PowerShell"
    PROLOG = "Prolog"
    PYTHON = "Python"
    R = "R"
    RUBY = "Ruby"
    RUST = "Rust"
    SCALA = "Scala"
    SHELL = "Shell"
    SQL = "SQL"
    SWIFT = "Swift"
    TEX = "TeX"
    TOML = "TOML"
    TYPESCRIPT = "TypeScript"
    VERILOG = "Verilog"
    VISUAL_BASIC = "Visual Basic"
    XML = "XML"
    YAML = "YAML"
    
    # Additional languages
    ONEC = "1C"  # 1С programming language

    # Formula languages
    LATEX = "LaTeX"         # LaTeX markup language
    MATHML = "MathML"       # Mathematical Markup Language
    ASCIIMATH = "AsciiMath" # AsciiMath notation
    MATHJAX = "MathJax"     # MathJax JavaScript engine
    KATEX = "KaTeX"         # KaTeX JavaScript engine
    SYMPY = "SymPy"         # SymPy symbolic mathematics

    @classmethod
    def from_string(cls, value: str) -> Optional['LanguageEnum']:
        if not isinstance(value, str):
            return None
        
        # Normalize input value
        normalized_value = value.lower().strip()
        
        # Special handling for C++ variants
        if normalized_value in ['c++', 'cpp']:
            return cls.CPP
        if normalized_value in ['js', 'javascript']:
            return cls.JAVASCRIPT
        if normalized_value in ['py', 'python']:
            return cls.PYTHON
        if normalized_value in ['latex', 'tex']:
            return cls.LATEX
        if normalized_value in ['mathml']:
            return cls.MATHML
        if normalized_value in ['asciimath']:
            return cls.ASCIIMATH
        if normalized_value in ['mathjax']:
            return cls.MATHJAX
        if normalized_value in ['katex']:
            return cls.KATEX
        if normalized_value in ['sympy']:
            return cls.SYMPY
        for member in cls:
            if member.value.lower() == normalized_value or member.name.lower() == normalized_value:
                return member
        return None

    def eqstr(self, value: Any) -> bool:
        if isinstance(value, str):
            enum_member = self.__class__.from_string(value)
            return self == enum_member
        return self == value

    @classmethod
    def default_value(cls):
        return cls.UNKNOWN
    
    @classmethod
    def is_programming_language(cls, value: Union[str, 'LanguageEnum']) -> bool:
        """Check if the given value represents a programming or formula language."""
        if isinstance(value, str):
            enum_value = cls.from_string(value)
        else:
            enum_value = value
        
        if enum_value is None:
            return False
        
        # Natural languages and special values are not programming or formula languages
        natural_languages = {cls.UNKNOWN, cls.EN, cls.RU, cls.UK, cls.DE, cls.FR, cls.ES, cls.ZH, cls.JA}
        return enum_value not in natural_languages
