"""
🎯 Template Registry
===================
Central registry for all available templates
"""

from typing import Dict, List

# Available templates registry
AVAILABLE_TEMPLATES = {
    "academic": {
        "name": "Academic Paper",
        "description": "Scientific and research document template with citations",
        "features": ["citations", "bibliography", "equations", "figures", "abstract"],
        "category": "academic",
        "complexity": "advanced"
    },
    "technical": {
        "name": "Technical Documentation", 
        "description": "Technical manuals and API documentation",
        "features": ["code_blocks", "diagrams", "api_docs", "tables", "syntax_highlighting"],
        "category": "documentation",
        "complexity": "standard"
    },
    "corporate": {
        "name": "Corporate Report",
        "description": "Executive reports and business documents", 
        "features": ["executive_summary", "charts", "financial_tables", "branding"],
        "category": "business",
        "complexity": "standard"
    },
    "educational": {
        "name": "Educational Guide",
        "description": "Learning materials and educational content",
        "features": ["exercises", "examples", "highlights", "summaries", "callouts"],
        "category": "education",
        "complexity": "standard"
    },
    "minimal": {
        "name": "Minimal Document",
        "description": "Clean, simple document layout",
        "features": ["basic_formatting", "clean_typography"],
        "category": "simple",
        "complexity": "basic"
    }
}

def get_template_names() -> List[str]:
    """Get list of all template names"""
    return list(AVAILABLE_TEMPLATES.keys())

def get_template_info(name: str) -> Dict:
    """Get template information"""
    return AVAILABLE_TEMPLATES.get(name, {})

def get_templates_by_category(category: str) -> Dict[str, Dict]:
    """Get templates filtered by category"""
    return {
        name: info 
        for name, info in AVAILABLE_TEMPLATES.items()
        if info.get("category") == category
    }
