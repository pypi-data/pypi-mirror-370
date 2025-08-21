"""
🎯 WOT-PDF Main API
==================
High-level convenience functions for PDF generation
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..core.generator import PDFGenerator
from ..core.book_generator import BookGenerator
from ..core.template_manager import TemplateManager
from ..core.intelligent_engine_router import IntelligentEngineRouter, EngineType

# Global instances for convenience
_pdf_generator = None
_book_generator = None
_template_manager = None
_engine_router = None

def get_pdf_generator() -> PDFGenerator:
    """Get or create global PDF generator instance"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFGenerator()
    return _pdf_generator

def get_book_generator() -> BookGenerator:
    """Get or create global book generator instance"""
    global _book_generator
    if _book_generator is None:
        _book_generator = BookGenerator(get_pdf_generator())
    return _book_generator

def get_template_manager() -> TemplateManager:
    """Get or create global template manager instance"""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager

def get_engine_router() -> IntelligentEngineRouter:
    """Get or create global engine router instance"""
    global _engine_router
    if _engine_router is None:
        _engine_router = IntelligentEngineRouter()
    return _engine_router

def generate_pdf(input_content: Union[str, Path],
                 output_file: Union[str, Path],
                 template: str = "technical",
                 title: Optional[str] = None,
                 author: Optional[str] = None,
                 **kwargs) -> Dict[str, Any]:
    """
    Generate PDF from markdown content
    
    Args:
        input_content: Markdown content or file path
        output_file: Output PDF file path
        template: Template name (default: "technical")
        title: Document title
        author: Document author
        **kwargs: Additional template parameters
        
    Returns:
        Generation result dictionary
        
    Example:
        >>> result = generate_pdf("# Hello World", "output.pdf")
        >>> print(result["success"])
        True
    """
    generator = get_pdf_generator()
    
    return generator.generate(
        input_content=input_content,
        output_file=Path(output_file),
        template=template,
        title=title,
        author=author,
        **kwargs
    )

def generate_book(input_dir: Union[str, Path],
                  output_file: Union[str, Path],
                  template: str = "technical", 
                  title: Optional[str] = None,
                  author: Optional[str] = None,
                  recursive: bool = True,
                  **kwargs) -> Dict[str, Any]:
    """
    Generate book from directory of markdown files
    
    Args:
        input_dir: Directory containing markdown files
        output_file: Output PDF file path
        template: Template name (default: "technical")
        title: Book title (auto-generated if None)
        author: Book author
        recursive: Search subdirectories for markdown files
        **kwargs: Additional template parameters
        
    Returns:
        Generation result dictionary
        
    Example:
        >>> result = generate_book("./docs/", "book.pdf", template="academic")
        >>> print(f"Generated book with {result['source_files']} files")
    """
    book_gen = get_book_generator()
    engine_router = get_engine_router()
    
    # Read sample content to analyze engine compatibility
    input_path = Path(input_dir)
    if input_path.exists():
        sample_content = ""
        markdown_files = list(input_path.glob("**/*.md" if recursive else "*.md"))
        
        # Read first few files for analysis
        for md_file in markdown_files[:3]:  # Sample first 3 files
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    sample_content += f.read() + "\n"
                if len(sample_content) > 5000:  # Enough for analysis
                    break
            except Exception:
                continue
        
        # Get engine recommendation (unless forced via environment)
        force_typst = os.environ.get('FORCE_TYPST', '').lower() in ('true', '1', 'yes')
        if force_typst:
            logging.info("🎯 FORCE_TYPST detected - forcing Typst engine")
            kwargs['force_engine'] = 'typst'
        elif sample_content:
            analysis = engine_router.analyze_content(sample_content)
            if analysis.recommended_engine == EngineType.REPORTLAB:
                logging.info(f"🎯 Engine Router: Recommending {analysis.recommended_engine.value} "
                           f"(confidence: {analysis.confidence:.1f}%)")
                logging.info(f"Complexity score: {analysis.complexity_score}")
                kwargs['force_engine'] = 'reportlab'
    
    return book_gen.generate_book(
        input_dir=Path(input_dir),
        output_file=Path(output_file),
        template=template,
        title=title,
        author=author,
        recursive=recursive,
        **kwargs
    )

def list_templates() -> List[Dict[str, Any]]:
    """
    List all available templates
    
    Returns:
        List of template information dictionaries
        
    Example:
        >>> templates = list_templates()
        >>> for template in templates:
        ...     print(f"{template['name']}: {template['description']}")
    """
    manager = get_template_manager()
    return manager.list_templates()

def get_template_info(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific template
    
    Args:
        template_name: Name of the template
        
    Returns:
        Template information dictionary or None if not found
        
    Example:
        >>> info = get_template_info("academic")
        >>> print(info["features"])
        ['citations', 'bibliography', 'equations', 'figures', 'abstract']
    """
    manager = get_template_manager()
    return manager.get_template(template_name)

def search_templates(query: str) -> List[Dict[str, Any]]:
    """
    Search templates by keyword
    
    Args:
        query: Search query
        
    Returns:
        List of matching templates
        
    Example:
        >>> results = search_templates("academic")
        >>> print([t["name"] for t in results])
        ['Academic Paper']
    """
    manager = get_template_manager()
    return manager.search_templates(query)

def analyze_content_for_engine(content: str) -> Dict[str, Any]:
    """
    Analyze content and recommend best PDF engine
    
    Args:
        content: Markdown content to analyze
        
    Returns:
        Engine recommendation dictionary
        
    Example:
        >>> analysis = analyze_content_for_engine("# Simple content")
        >>> print(f"Recommended engine: {analysis['engine']}")
        typst
    """
    router = get_engine_router()
    analysis = router.analyze_content(content)
    
    # Convert to dictionary format for CLI
    return {
        'engine': analysis.recommended_engine.value,
        'confidence': analysis.confidence,
        'complexity_score': analysis.complexity_score,
        'details': {
            'code_blocks': analysis.code_block_count,
            'languages': analysis.programming_languages,
            'special_char_density': analysis.special_char_density,
            'math_content': analysis.has_math_formulas,
            'tables': analysis.has_tables
        },
        'reason': f"Content complexity: {analysis.complexity_score:.1f}/100",
        'issues': []  # Could be extended based on analysis_details
    }

def validate_template(template_name: str) -> bool:
    """
    Check if template exists
    
    Args:
        template_name: Name of the template
        
    Returns:
        True if template exists, False otherwise
        
    Example:
        >>> validate_template("technical")
        True
        >>> validate_template("nonexistent")
        False
    """
    manager = get_template_manager()
    return manager.validate_template(template_name)

# Convenience aliases
pdf = generate_pdf
book = generate_book
templates = list_templates
