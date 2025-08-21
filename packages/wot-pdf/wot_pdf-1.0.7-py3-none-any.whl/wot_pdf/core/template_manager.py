"""
🎯 Template Manager
==================
Manage PDF templates and their configurations
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

class TemplateManager:
    """
    Manage PDF generation templates
    """
    
    def __init__(self):
        """Initialize template manager"""
        self.logger = logging.getLogger(__name__)
        
        # Template registry
        self.templates = {
            "academic": {
                "name": "Academic Paper",
                "description": "Scientific and research document template with citations",
                "features": ["citations", "bibliography", "equations", "figures", "abstract"],
                "best_for": "Research papers, academic articles, thesis documents",
                "typography": "serif",
                "margins": "wide",
                "numbering": "enabled"
            },
            "technical": {
                "name": "Technical Documentation",
                "description": "Technical manuals and API documentation",
                "features": ["code_blocks", "diagrams", "api_docs", "tables", "syntax_highlighting"],
                "best_for": "User manuals, API docs, technical guides",
                "typography": "sans-serif", 
                "margins": "standard",
                "numbering": "enabled"
            },
            "corporate": {
                "name": "Corporate Report",
                "description": "Executive reports and business documents",
                "features": ["executive_summary", "charts", "financial_tables", "branding"],
                "best_for": "Business reports, executive summaries, presentations",
                "typography": "sans-serif",
                "margins": "standard",
                "numbering": "enabled"
            },
            "educational": {
                "name": "Educational Guide",
                "description": "Learning materials and educational content",
                "features": ["exercises", "examples", "highlights", "summaries", "callouts"],
                "best_for": "Tutorials, course materials, learning guides",
                "typography": "friendly",
                "margins": "comfortable",
                "numbering": "enabled"
            },
            "minimal": {
                "name": "Minimal Document",
                "description": "Clean, simple document layout",
                "features": ["basic_formatting", "clean_typography"],
                "best_for": "Simple documents, quick generation, drafts",
                "typography": "clean",
                "margins": "minimal",
                "numbering": "optional"
            }
        }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates
        
        Returns:
            List of template information
        """
        return [
            {
                "name": name,
                **info
            }
            for name, info in self.templates.items()
        ]
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get template information
        
        Args:
            name: Template name
            
        Returns:
            Template information or None if not found
        """
        return self.templates.get(name)
    
    def validate_template(self, name: str) -> bool:
        """
        Validate if template exists
        
        Args:
            name: Template name
            
        Returns:
            True if template exists
        """
        return name in self.templates
    
    def get_template_names(self) -> List[str]:
        """Get list of template names"""
        return list(self.templates.keys())
    
    def get_default_template(self) -> str:
        """Get default template name"""
        return "technical"
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Search templates by name, description, or features
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        matches = []
        
        for name, info in self.templates.items():
            # Search in name
            if query_lower in name.lower():
                matches.append({"name": name, **info, "match_type": "name"})
                continue
            
            # Search in description
            if query_lower in info["description"].lower():
                matches.append({"name": name, **info, "match_type": "description"})
                continue
            
            # Search in features
            if any(query_lower in feature.lower() for feature in info["features"]):
                matches.append({"name": name, **info, "match_type": "feature"})
                continue
            
            # Search in best_for
            if query_lower in info["best_for"].lower():
                matches.append({"name": name, **info, "match_type": "use_case"})
        
        return matches
