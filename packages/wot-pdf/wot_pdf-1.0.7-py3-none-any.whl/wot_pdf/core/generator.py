"""
🎯 WOT-PDF Core Generator
========================
Clean, standalone PDF generator with dual-engine architecture
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Import engines
from ..engines.typst_engine import TypstEngine
from ..engines.enhanced_reportlab_engine import EnhancedReportLabEngine
from .intelligent_engine_router import IntelligentEngineRouter

class PDFGenerator:
    """
    Core PDF generator with dual-engine architecture
    
    Primary: Typst CLI (superior typography)
    Fallback: ReportLab (100% reliability)
    """
    
    def __init__(self, 
                 default_template: str = "technical",
                 output_dir: Optional[str] = None,
                 enable_typst: bool = True,
                 debug: bool = False):
        """
        Initialize PDF generator
        
        Args:
            default_template: Default template name
            output_dir: Default output directory
            enable_typst: Whether to use Typst engine
            debug: Enable debug logging
        """
        self.default_template = default_template
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "output"
        self.debug = debug
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Initialize engines
        self.typst_engine = TypstEngine() if enable_typst else None
        self.reportlab_engine = EnhancedReportLabEngine()
        self.router = IntelligentEngineRouter()
        
        # Track generation stats
        self.stats = {
            "total_generated": 0,
            "typst_success": 0,
            "reportlab_fallback": 0,
            "errors": 0
        }
    
    def generate(self, 
                 input_content: Union[str, Path],
                 output_file: Union[str, Path],
                 template: Optional[str] = None,
                 force_engine: Optional[str] = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Generate PDF from input content
        
        Args:
            input_content: Markdown content or file path
            output_file: Output PDF path
            template: Template name (optional)
            force_engine: Force specific engine ('typst' or 'reportlab')
            **kwargs: Additional template parameters
            
        Returns:
            Generation result with metadata
        """
        try:
            # Resolve paths
            output_path = Path(output_file)
            template_name = template or self.default_template
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read input content
            if isinstance(input_content, Path) or os.path.isfile(str(input_content)):
                with open(input_content, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = str(input_content)
            
            # Check for forced engine
            if force_engine == 'reportlab':
                self.logger.info("🎯 Forced engine: ReportLab (skipping Typst)")
                return self._generate_with_reportlab(content, output_path, template_name, **kwargs)
            elif force_engine == 'typst':
                self.logger.info("🎯 Forced engine: Typst")
                return self._generate_with_typst(content, output_path, template_name, **kwargs)
            
            # Use intelligent engine routing
            recommendation = self.router.recommend_engine(content)
            recommended_engine = recommendation['engine']
            confidence = recommendation['confidence']
            
            if recommended_engine == 'reportlab' and confidence > 0.7:
                self.logger.info(f"🎯 Engine Router: Recommending reportlab (confidence: {confidence:.1%})")
                self.logger.info(f"Complexity score: {recommendation.get('complexity_score', 'unknown')}")
                return self._generate_with_reportlab(content, output_path, template_name, **kwargs)
            
            # Try Typst engine first (normal flow)
            if self.typst_engine:
                result = self._generate_with_typst(content, output_path, template_name, **kwargs)
                if result.get("success"):
                    return result
            
            # Fallback to ReportLab
            return self._generate_with_reportlab(content, output_path, template_name, **kwargs)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "none",
                "stats": self.stats.copy()
            }
    
    def _generate_with_typst(self, content: str, output_path: Path, template_name: str, **kwargs) -> Dict[str, Any]:
        """Generate with Typst engine"""
        try:
            result = self.typst_engine.generate(
                content=content,
                output_file=output_path,
                template=template_name,
                **kwargs
            )
            
            if result.get("success"):
                self.stats["typst_success"] += 1
                self.stats["total_generated"] += 1
                self.logger.info(f"✅ Generated with Typst: {output_path}")
                return {
                    **result,
                    "engine": "typst",
                    "stats": self.stats.copy()
                }
            else:
                raise Exception(result.get("error", "Typst generation failed"))
                
        except Exception as e:
            self.logger.warning(f"Typst generation failed: {e}")
            raise
    
    def _generate_with_reportlab(self, content: str, output_path: Path, template_name: str, **kwargs) -> Dict[str, Any]:
        """Generate with ReportLab engine"""
        try:
            result = self.reportlab_engine.generate(
                content=content,
                output_file=output_path,
                template=template_name,
                **kwargs
            )
            
            self.stats["reportlab_fallback"] += 1
            self.stats["total_generated"] += 1
            self.logger.info(f"✅ Generated with ReportLab: {output_path}")
            
            return {
                **result,
                "engine": "enhanced_reportlab",
                "stats": self.stats.copy()
            }
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"ReportLab generation failed: {e}")
            raise
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List available templates"""
        # This will be implemented based on template registry
        return [
            {"name": "academic", "description": "Research papers with citations"},
            {"name": "technical", "description": "Technical documentation"},
            {"name": "corporate", "description": "Business reports"},
            {"name": "educational", "description": "Learning materials"},
            {"name": "minimal", "description": "Clean, simple design"}
        ]
    
    def get_stats(self) -> Dict[str, int]:
        """Get generation statistics"""
        return self.stats.copy()
