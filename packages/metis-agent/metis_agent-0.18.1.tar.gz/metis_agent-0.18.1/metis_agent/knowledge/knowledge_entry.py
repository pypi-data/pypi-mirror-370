"""
Knowledge Entry Data Structure

Defines the core data structure for knowledge base entries with support for
different content types, metadata, and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import yaml


@dataclass
class KnowledgeEntry:
    """
    Core knowledge entry structure
    """
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    source: str = "user_input"  # user_input, ai_generated, external, file
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "embedding": self.embedding,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Export as JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_yaml(self) -> str:
        """Export as YAML string"""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def to_markdown(self) -> str:
        """Export as markdown file"""
        lines = []
        lines.append(f"# {self.title}")
        lines.append("")
        
        # Add metadata header
        lines.append("---")
        lines.append(f"id: {self.id}")
        lines.append(f"category: {self.category}")
        if self.tags:
            lines.append(f"tags: {', '.join(self.tags)}")
        lines.append(f"source: {self.source}")
        lines.append(f"created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"updated: {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"version: {self.version}")
        lines.append("---")
        lines.append("")
        
        # Add content
        lines.append(self.content)
        
        return "\n".join(lines)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        """Create from dictionary"""
        # Parse datetime strings
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            category=data["category"],
            tags=data.get("tags", []),
            source=data.get("source", "user_input"),
            created_at=created_at,
            updated_at=updated_at,
            version=data.get("version", 1),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'KnowledgeEntry':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'KnowledgeEntry':
        """Create from YAML string"""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_markdown(cls, markdown_content: str, entry_id: str = None) -> 'KnowledgeEntry':
        """Create from markdown content with frontmatter"""
        lines = markdown_content.strip().split('\n')
        
        # Parse frontmatter if present
        metadata = {}
        content_start = 0
        
        if lines and lines[0] == '---':
            # Find end of frontmatter
            for i, line in enumerate(lines[1:], 1):
                if line == '---':
                    # Parse YAML frontmatter
                    frontmatter = '\n'.join(lines[1:i])
                    try:
                        metadata = yaml.safe_load(frontmatter) or {}
                    except yaml.YAMLError:
                        metadata = {}
                    content_start = i + 1
                    break
        
        # Extract title from first heading or use provided
        title = metadata.get("title", "")
        if not title and content_start < len(lines):
            for line in lines[content_start:]:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
        
        # Extract content (skip title if it was the first heading)
        content_lines = lines[content_start:]
        if content_lines and content_lines[0].startswith('# ') and content_lines[0][2:].strip() == title:
            content_lines = content_lines[1:]
        
        content = '\n'.join(content_lines).strip()
        
        # Generate ID if not provided
        if not entry_id:
            entry_id = metadata.get("id", f"kb_{int(datetime.now().timestamp())}")
        
        return cls(
            id=entry_id,
            title=title or "Untitled",
            content=content,
            category=metadata.get("category", "general"),
            tags=metadata.get("tags", []),
            source=metadata.get("source", "file"),
            created_at=datetime.fromisoformat(metadata.get("created", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(metadata.get("updated", datetime.now().isoformat())),
            version=metadata.get("version", 1),
            metadata=metadata.get("metadata", {})
        )
    
    def update_content(self, new_content: str, increment_version: bool = True):
        """Update content and metadata"""
        self.content = new_content
        self.updated_at = datetime.now()
        if increment_version:
            self.version += 1
    
    def add_tags(self, tags: List[str]):
        """Add tags to the entry"""
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)
        self.updated_at = datetime.now()
    
    def remove_tags(self, tags: List[str]):
        """Remove tags from the entry"""
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
        self.updated_at = datetime.now()
    
    def get_summary(self, max_length: int = 200) -> str:
        """Get a summary of the content"""
        if len(self.content) <= max_length:
            return self.content
        
        # Try to break at sentence boundary
        truncated = self.content[:max_length]
        last_sentence = truncated.rfind('.')
        if last_sentence > max_length * 0.7:  # If we can break at a reasonable sentence
            return truncated[:last_sentence + 1]
        else:
            return truncated + "..."


@dataclass
class KnowledgeQueryResult:
    """
    Result structure for knowledge queries
    """
    entries: List[KnowledgeEntry]
    total_count: int
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    relevance_scores: List[float] = field(default_factory=list)
    
    def get_context_string(self, max_length: int = 2000) -> str:
        """Format as context string for LLM"""
        if not self.entries:
            return ""
        
        context_parts = ["Relevant knowledge:"]
        current_length = len(context_parts[0])
        
        for i, entry in enumerate(self.entries):
            relevance = self.relevance_scores[i] if i < len(self.relevance_scores) else 1.0
            
            # Format entry
            entry_text = f"{i+1}. [{entry.category}] {entry.title}: {entry.get_summary(300)} (relevance: {relevance:.2f})"
            
            # Check if adding this entry would exceed max length
            if current_length + len(entry_text) + 1 > max_length:
                break
            
            context_parts.append(entry_text)
            current_length += len(entry_text) + 1
        
        return "\n".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "total_count": self.total_count,
            "query": self.query,
            "filters": self.filters,
            "execution_time": self.execution_time,
            "relevance_scores": self.relevance_scores
        }
