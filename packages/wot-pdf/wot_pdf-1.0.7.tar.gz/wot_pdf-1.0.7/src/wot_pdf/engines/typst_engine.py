"""
🎯 Typst Engine - Future-Proofed Implementation
===============================================
Advanced Typst engine with future-proofing protection
Integrated with security validation and version management
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import our enhanced components
try:
    from ..core.future_proofing_system import FutureProofingSystem
    FUTURE_PROOFING_AVAILABLE = True
except ImportError:
    FUTURE_PROOFING_AVAILABLE = False
    logging.warning("Future-proofing system not available")

# Import unified content optimizer
try:
    from ..core.unified_typst_content_optimizer import UnifiedTypstContentOptimizer
    UNIFIED_OPTIMIZER_AVAILABLE = True
except ImportError:
    # Fallback to old optimizer
    try:
        from ..core.typst_content_optimizer import TypstContentOptimizer
        UNIFIED_OPTIMIZER_AVAILABLE = False
    except ImportError:
        UNIFIED_OPTIMIZER_AVAILABLE = None
        logging.warning("No Typst content optimizer available")

class TypstEngine:
    """
    Advanced Typst engine with future-proofing protection
    Includes security validation, version management, and safe compilation
    """
    
    def __init__(self):
        """Initialize Typst engine with future-proofing"""
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(__file__).parent.parent
        
        # Initialize future-proofing system
        if FUTURE_PROOFING_AVAILABLE:
            self.future_proofing = FutureProofingSystem()
            self.logger.info("🛡️ Future-proofing system enabled")
        else:
            self.future_proofing = None
            self.logger.warning("⚠️ Future-proofing system disabled")
        
        # Initialize content optimizer
        if UNIFIED_OPTIMIZER_AVAILABLE is True:
            self.content_optimizer = UnifiedTypstContentOptimizer(debug=True)
            self.logger.info("🚀 Unified Typst content optimizer enabled")
        elif UNIFIED_OPTIMIZER_AVAILABLE is False:
            self.content_optimizer = TypstContentOptimizer()
            self.logger.info("⚙️ Legacy Typst content optimizer enabled")
        else:
            self.content_optimizer = None
            self.logger.warning("⚠️ No content optimizer available")
        
        # Check if Typst CLI is available
        self.typst_available = self._check_typst_cli()
        
        if not self.typst_available:
            self.logger.warning("System Typst CLI not found - this engine will not function")
    
    def _check_typst_cli(self) -> bool:
        """Check if Typst CLI is available in system PATH"""
        try:
            result = subprocess.run(
                ["typst", "--version"], 
                capture_output=True, 
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            if result.returncode == 0:
                self.logger.info(f"Typst CLI found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def generate(self, 
                 content: str,
                 output_file: Path,
                 template: str = "technical",
                 **kwargs) -> Dict[str, Any]:
        """
        Generate PDF using Typst CLI with future-proofing protection
        
        Args:
            content: Markdown content
            output_file: Output PDF path
            template: Template name
            **kwargs: Template parameters
            
        Returns:
            Generation result
        """
        self.logger.info(f"🔧 TypstEngine.generate called with skip_optimization={kwargs.get('skip_optimization', 'NOT_SET')}")
        
        if not self.typst_available:
            raise RuntimeError("Typst CLI not available")
        
        # Generate unique document ID for compilation management
        document_id = f"typst_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # STEP 1: Apply future-proofing protection
            if self.future_proofing:
                # Process content through security and version management
                processed_content, issues = self.future_proofing.process_content_safely(
                    content, document_id
                )
                
                if issues:
                    self.logger.info(f"🛡️ Future-proofing applied: {len(issues)} issues resolved")
                    for issue in issues[:3]:  # Log first 3 issues
                        self.logger.debug(f"   - {issue}")
                
                content = processed_content
            
            # STEP 2: Use safe compilation context
            if self.future_proofing:
                with self.future_proofing.safe_compilation_context(document_id) as slot:
                    return self._compile_with_slot(content, output_file, template, slot, **kwargs)
            else:
                # Fallback to direct compilation
                return self._compile_direct(content, output_file, template, **kwargs)
            
        except Exception as e:
            self.logger.error(f"❌ Typst generation failed for {document_id}: {e}")
            raise
    
    def _compile_with_slot(self, content: str, output_file: Path, template: str, slot, **kwargs) -> Dict[str, Any]:
        """Compile Typst with managed compilation slot"""
        self.logger.info(f"🔧 Compiling with managed slot: {slot.document_id}")
        
        # Convert markdown to Typst using temp directory from slot
        skip_optimization = kwargs.pop('skip_optimization', False)
        typst_content = self._markdown_to_typst(content, template, skip_optimization=skip_optimization, **kwargs)
        
        # Create temp file in managed directory
        temp_typst_file = Path(slot.temp_dir) / "document.typ"
        temp_typst_file.write_text(typst_content, encoding='utf-8')
        
        try:
            # Compile with Typst CLI
            result = subprocess.run([
                'typst', 'compile', str(temp_typst_file), str(output_file)
            ], 
            capture_output=True, 
            encoding='utf-8',
            errors='replace',  # Handle encoding errors gracefully
            timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size if output_file.exists() else 0
                self.logger.info(f"✅ Typst compilation successful: {file_size} bytes")
                
                return {
                    "success": True,
                    "output_file": str(output_file),
                    "file_size_bytes": file_size,
                    "engine": "typst",
                    "compilation_slot": slot.document_id,
                    "typst_source": str(temp_typst_file)
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown compilation error"
                self.logger.error(f"❌ Typst compilation failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": f"Typst compilation failed: {error_msg}",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Typst compilation timeout")
            return {
                "success": False,
                "error": "Compilation timeout (5 minutes exceeded)"
            }
        except Exception as e:
            self.logger.error(f"❌ Compilation process error: {e}")
            return {
                "success": False,
                "error": f"Process error: {e}"
            }
    
    def _compile_direct(self, content: str, output_file: Path, template: str, **kwargs) -> Dict[str, Any]:
        """Direct compilation without slot management (fallback)"""
        self.logger.warning("⚠️ Using direct compilation (no future-proofing)")
        
        # Convert markdown to Typst
        skip_optimization = kwargs.pop('skip_optimization', False)
        typst_content = self._markdown_to_typst(content, template, skip_optimization=skip_optimization, **kwargs)
        
        # Create temporary Typst file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False, encoding='utf-8') as f:
            f.write(typst_content)
            temp_typst_file = f.name
        
        try:
            # Compile with Typst CLI
            result = subprocess.run([
                'typst', 'compile', temp_typst_file, str(output_file)
            ], 
            capture_output=True, 
            timeout=60,
            encoding='utf-8',
            errors='replace',  # Handle encoding errors gracefully
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size if output_file.exists() else 0
                return {
                    "success": True,
                    "output_file": str(output_file),
                    "template": template,
                    "engine": "typst_direct",
                    "file_size_bytes": file_size,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = result.stderr or result.stdout or "Unknown Typst error"
                self.logger.error(f"Typst compilation failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Typst compilation failed: {error_msg}",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
                
        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_typst_file)
            except OSError:
                pass
    
    def _markdown_to_typst(self, markdown_content: str, template: str, skip_optimization: bool = False, **kwargs) -> str:
        """
        Convert markdown content to Typst syntax
        
        This is a simplified, clean conversion focused on reliability
        """
        self.logger.info(f"🔍 _markdown_to_typst called with skip_optimization={skip_optimization}")
        
        # Get template
        typst_template = self._get_template(template)
        
        # Basic metadata
        title = kwargs.get('title', 'Document')
        author = kwargs.get('author', 'Generated by WOT-PDF')
        
        # Apply template with metadata
        header = typst_template.format(
            title=title,
            author=author,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        # Convert markdown to Typst content
        typst_content = self._convert_markdown_syntax(markdown_content, skip_optimization=skip_optimization)
        
        return header + "\n\n" + typst_content
    
    def _convert_markdown_syntax(self, content: str, skip_optimization: bool = False) -> str:
        """
        Enhanced markdown to Typst conversion with unified optimizer
        """
        
        # Check if optimization should be skipped (for pre-processed content)
        if skip_optimization:
            self.logger.info("🔄 Skipping optimization - content already processed")
            return content
        
        # Uporabi unified content optimizer če je na voljo
        if self.content_optimizer:
            self.logger.info("🚀 Using unified Typst content optimizer")
            return self.content_optimizer.optimize_content_for_typst(content, "technical")
        
        # Fallback: osnovni conversion
        self.logger.warning("⚠️ Using fallback markdown conversion")
        return self._basic_markdown_conversion(content)
    
    def _basic_markdown_conversion(self, content: str) -> str:
        """
        Basic fallback markdown to Typst conversion
        """
        lines = content.split('\n')
        typst_lines = []
        in_code_block = False
        in_table = False
        table_headers = []
        table_rows = []
        code_lang = ""
        
        for i, line in enumerate(lines):
            # Code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    code_lang = line.strip()[3:].strip()
                    if code_lang:
                        typst_lines.append(f"```{code_lang}")
                    else:
                        typst_lines.append("```")
                else:
                    # Ending code block
                    in_code_block = False
                    typst_lines.append("```")
                continue
            
            # If inside code block, preserve line as-is
            if in_code_block:
                typst_lines.append(line)
                continue
            
            # Table detection
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                self.logger.debug(f"Table line detected: {line}")
                if not in_table:
                    # Starting a table
                    in_table = True
                    table_headers = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    self.logger.debug(f"Table headers: {table_headers}")
                    continue
                elif line.strip().replace('|', '').replace('-', '').replace(' ', '') == '':
                    # Table separator line, skip
                    self.logger.debug("Table separator line, skipping")
                    continue
                else:
                    # Table data row
                    table_row = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    table_rows.append(table_row)
                    self.logger.debug(f"Table row added: {table_row}")
                    # Check if next line is still table
                    if i + 1 >= len(lines) or not (lines[i + 1].strip().startswith('|') and lines[i + 1].strip().endswith('|')):
                        # End of table, output it
                        self.logger.debug(f"End of table, creating Typst table with {len(table_headers)} headers and {len(table_rows)} rows")
                        typst_table = self._create_typst_table(table_headers, table_rows)
                        typst_lines.append(typst_table)
                        self.logger.debug(f"Generated Typst table: {typst_table}")
                        in_table = False
                        table_headers = []
                        table_rows = []
                    continue
            
            # Headers
            if line.startswith('#') and not in_code_block:
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ').strip()
                if level <= 6:
                    typst_lines.append(f"{'=' * level} {header_text}")
                continue
            
            # Horizontal rules
            if line.strip() in ['---', '***', '___']:
                typst_lines.append("#line(length: 100%)")
                continue
            
            # Lists (improved handling)
            if line.strip().startswith(('- ', '* ', '+ ')):
                indent = len(line) - len(line.lstrip())
                item_text = line.strip()[2:].strip()
                # Convert markdown formatting in list items
                item_text = self._convert_inline_formatting(item_text)
                typst_lines.append(' ' * indent + f"- {item_text}")
                continue
            
            # Numbered lists
            if line.strip() and line.strip()[0].isdigit() and '. ' in line.strip():
                indent = len(line) - len(line.lstrip())
                item_text = line.strip().split('. ', 1)[1] if '. ' in line.strip() else line.strip()
                item_text = self._convert_inline_formatting(item_text)
                typst_lines.append(' ' * indent + f"+ {item_text}")
                continue
            
            # Block quotes
            if line.strip().startswith('> '):
                quote_text = line.strip()[2:]
                quote_text = self._convert_inline_formatting(quote_text)
                typst_lines.append(f"#quote[{quote_text}]")
                continue
            
            # Regular text with inline formatting
            if line.strip():
                converted_line = self._convert_inline_formatting(line)
                typst_lines.append(converted_line)
            else:
                typst_lines.append("")
        
        return '\n'.join(typst_lines)
    
    def _create_typst_table(self, headers: list, rows: list) -> str:
        """Create Typst table from markdown table data"""
        if not headers:
            return ""
        
        # Calculate column count
        col_count = len(headers)
        
        # Create table header with white text on blue background and center alignment
        header_cells = ', '.join([f'[#text(fill: white, weight: "bold")[#align(center)[{self._escape_typst_text(header)}]]]' for header in headers])
        
        # Create table rows with smart alignment
        table_rows = []
        for row in rows:
            # Pad row if necessary
            while len(row) < col_count:
                row.append("")
            # Smart alignment based on content
            aligned_cells = []
            for cell in row[:col_count]:
                cell_content = cell.strip()
                # Escape special characters in cell content
                escaped_cell = self._escape_typst_text(cell)
                # Check if cell contains primarily numbers/currency/percentages
                if any(c in cell_content for c in ['$', '%', '€', '£']) or cell_content.replace(',', '').replace('.', '').replace('-', '').replace('+', '').replace('$', '').isdigit():
                    aligned_cells.append(f'[#align(right)[{escaped_cell}]]')
                else:
                    aligned_cells.append(f'[#align(left)[{escaped_cell}]]')
            row_cells = ', '.join(aligned_cells)
            table_rows.append(row_cells)
        
        # Combine all rows
        all_rows = [header_cells] + table_rows
        table_content = ',\n  '.join(all_rows)
        
        return f"""#table(
  columns: ({', '.join(['auto'] * col_count)}),
  stroke: 1pt + rgb("#b0b0b0"),
  fill: (x, y) => if y == 0 {{ rgb("#4A90E2") }} else if calc.odd(y) {{ rgb("#f7f8fa") }} else {{ white }},
  align: horizon,
  inset: 8pt,
  {table_content}
)"""
    
    def _convert_inline_formatting(self, text: str) -> str:
        """Convert inline markdown formatting to Typst"""
        import re
        
        # Bold: **text** or __text__ -> *text*
        text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
        text = re.sub(r'__(.+?)__', r'*\1*', text)
        
        # Italic: *text* or _text_ -> _text_
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'_\1_', text)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'_\1_', text)
        
        # Inline code: `code` -> `code`
        text = re.sub(r'`([^`]+?)`', r'`\1`', text)
        
        # Links: [text](url) -> #link("url")[text]
        text = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'#link("\2")[\1]', text)
        
        # Images: ![alt](url) -> #image("url")
        text = re.sub(r'!\[([^\]]*?)\]\(([^)]+?)\)', r'#image("\2")', text)
        
        # Strikethrough: ~~text~~ -> #strike[text]
        text = re.sub(r'~~(.+?)~~', r'#strike[\1]', text)
        
        return text
    
    def _escape_typst_text(self, text: str) -> str:
        """Escape special characters for Typst"""
        # Escape dollar signs which are math delimiters in Typst
        text = text.replace('$', r'\$')
        # Escape other special characters if needed
        text = text.replace('#', r'\#')
        text = text.replace('@', r'\@')
        return text
    
    def _get_template(self, template_name: str) -> str:
        """Get Typst template from file or inline"""
        template_dir = self.base_dir / "templates" / "typst"
        template_file = template_dir / f"{template_name}.typ"
        
        # Try to load from file first
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.warning(f"Failed to load template file {template_file}: {e}")
        
        # Fallback to inline templates
        return self._get_inline_template(template_name)
    
    def _get_inline_template(self, template_name: str) -> str:
        """Get fallback inline Typst template"""
        templates = {
            "technical": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
  lang: "en"
)

#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.65em)

#align(center)[
  #text(size: 20pt, weight: "bold")[{title}]
  
  #v(1em)
  
  #text(size: 12pt)[{author}]
  
  #v(0.5em)
  
  #text(size: 10pt)[{date}]
]

#v(2em)''',

            "academic": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4", 
  margin: (left: 3cm, right: 3cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Linux Libertine",
  size: 12pt,
  lang: "en"
)

#set heading(numbering: "1.")
#set par(justify: true, first-line-indent: 1.5em)

#align(center)[
  #text(size: 18pt, weight: "bold")[{title}]
  
  #v(1em)
  
  #text(size: 14pt)[{author}]
  
  #v(0.5em)
  
  #text(size: 10pt)[{date}]
]

#v(2em)''',

            "minimal": '''#set document(title: "{title}", author: "{author}")
#set page(margin: 2cm, numbering: "1")
#set text(font: "Arial", size: 11pt)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 16pt, weight: "bold")[{title}]
  #v(1em)
  #text(size: 10pt)[{author} • {date}]
]

#v(1.5em)''',

            "corporate": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
  header: [
    #line(length: 100%, stroke: 0.5pt + gray)
    #v(-8pt)
    #text(size: 8pt, fill: gray)[{title}]
    #h(1fr)
    #text(size: 8pt, fill: gray)[{date}]
  ]
)

#set text(font: "Arial", size: 11pt)
#set heading(numbering: "1.")
#set par(justify: true)

#align(center)[
  #text(size: 20pt, weight: "bold", fill: rgb("#1f4788"))[{title}]
  
  #v(0.5em)
  
  #text(size: 12pt, fill: gray)[{author}]
  
  #v(0.3em)
  
  #text(size: 10pt, fill: gray)[{date}]
]

#v(2em)''',

            "educational": '''#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: 2.5cm,
  numbering: "1",
  number-align: center,
)

#set text(font: "Open Sans", size: 11pt)
#set heading(numbering: "1.")
#set par(justify: true, leading: 0.7em)

#rect(
  width: 100%,
  fill: rgb("#f0f8ff"),
  stroke: rgb("#4a90e2"),
  radius: 5pt,
  inset: 1em
)[
  #align(center)[
    #text(size: 18pt, weight: "bold", fill: rgb("#2c5aa0"))[{title}]
    
    #v(0.5em)
    
    #text(size: 12pt)[{author}]
    
    #v(0.3em)
    
    #text(size: 10pt, style: "italic")[{date}]
  ]
]

#v(2em)'''
        }
        
        return templates.get(template_name, templates["technical"])
