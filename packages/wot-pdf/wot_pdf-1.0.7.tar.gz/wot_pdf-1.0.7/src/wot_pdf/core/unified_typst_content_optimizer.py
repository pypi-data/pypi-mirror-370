#!/usr/bin/env python3
"""
🚀 WOT-PDF UNIFIED TYPST CONTENT OPTIMIZER v2.0
===============================================
Integration z Unified Markdown → Typst Converter
Sistemski pristop k pretvorbi in optimizaciji za Typst

ENHANCED PIPELINE:
- Step 1: Advanced Python code protection 
- Step 2: Unified Markdown → Typst conversion
- Step 3: Character sanitization & Unicode
- Step 4: Restore protected content
- Step 5: Final cleanup & validation
"""
import re
import uuid
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConversionStats:
    """Statistike konverzije za debugging."""
    headers_converted: int = 0
    code_blocks_protected: int = 0
    inline_code_converted: int = 0
    lists_converted: int = 0
    formatting_converted: int = 0
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []

class UnifiedTypstContentOptimizer:
    """
    🎯 UNIFIED TYPST CONTENT OPTIMIZER
    Integrira najboljše lastnosti vseh obstoječih konverterjev
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.protected_blocks: Dict[str, str] = {}
        self.bold_placeholders: Dict[str, str] = {}
        self.stats = ConversionStats()
        
    def optimize_content_for_typst(self, content: str, template_type: str = "technical") -> str:
        """
        🚀 GLAVNA OPTIMIZACIJSKA FUNKCIJA - v2.0
        
        Args:
            content: Markdown vsebina za konverzijo
            template_type: Tip template (technical/professional/minimal)
            
        Returns:
            Optimizirana Typst vsebina
        """
        try:
            # Reset
            self.stats = ConversionStats()
            self.protected_blocks.clear()
            self.bold_placeholders.clear()
            
            if self.debug:
                self.logger.info("🚀 Starting unified Typst content optimization v2.0")
            
            # PIPELINE KORAKI
            content = self._step1_protect_critical_blocks(content)
            content = self._step2_unified_markdown_conversion(content)
            content = self._step3_character_sanitization(content)
            content = self._step4_restore_protected_content(content)
            content = self._step5_final_cleanup(content)
            
            if self.debug:
                self._log_optimization_stats()
                
            return content
            
        except Exception as e:
            error_msg = f"❌ CRITICAL: Unified optimization failed: {e}"
            self.logger.error(error_msg)
            self.stats.errors.append(error_msg)
            return content  # Return original on failure

    def _step1_protect_critical_blocks(self, content: str) -> str:
        """STEP 1: Zaščiti kritične bloke pred konverzijo"""
        
        # NAJPREJ zaščitimo Python elemente ZNOTRAJ code blokov
        content = self._protect_python_dictionaries(content)
        content = self._protect_python_comments(content)
        
        # POTEM konvertiramo code bloke (ki sedaj vsebujejo placeholderje)
        content = self._protect_all_code_blocks(content)
        
        # Generic code bloki
        content = self._protect_generic_code_blocks(content)
        
        return content
    
    def _protect_all_code_blocks(self, content: str) -> str:
        """Zaščiti VSE code bloke - FIXED stack-based parsing!"""
        
        if self.debug:
            print(f"🔍 Starting FIXED code block protection for {len(content)} chars")
        
        lines = content.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect code block start - MUST have language or be exactly ```
            opening_match = re.match(r'^(\s*)```(\w+)\s*$', line)  # WITH language
            plain_opening = re.match(r'^(\s*)```\s*$', line)       # WITHOUT language (generic)
            
            if opening_match or plain_opening:
                if opening_match:
                    indent, lang = opening_match.groups()
                else:
                    indent = plain_opening.group(1)
                    lang = "text"
                
                if self.debug:
                    print(f"🚨 Found opening marker: line {i+1}, lang='{lang}'")
                
                # Find matching closing ``` (exact match only)
                block_lines = [line]
                content_lines = []
                i += 1
                
                # Search for exact closing marker ```
                while i < len(lines):
                    current_line = lines[i]
                    
                    # Check for exact closing pattern
                    if re.match(r'^(\s*)```\s*$', current_line):
                        block_lines.append(current_line)
                        if self.debug:
                            print(f"✅ Found closing marker: line {i+1}")
                        break
                    else:
                        content_lines.append(current_line)
                        block_lines.append(current_line)
                    
                    i += 1
                
                # If we found matching close, process the block
                if i < len(lines):  # We found closing marker
                    code_content = '\n'.join(content_lines)
                    
                    if self.debug and ('def ' in code_content or 'import ' in code_content or 'confidence_level' in code_content):
                        print(f"🚨 Converting block with {lang}: {code_content[:50]}...")
                    
                    # Use simple backtick block format - Typst handles this natively
                    typst_block = f'```{lang}\n{code_content}\n```'
                    
                    if self.debug:
                        print(f"✅ Generated raw block (length: {len(typst_block)})")
                    
                    result_lines.append(typst_block)
                    self.stats.code_blocks_protected += 1
                else:
                    # No closing marker found, keep original
                    if self.debug:
                        print(f"⚠️  No closing marker found for block starting at line {i-len(content_lines)}")
                    result_lines.extend(block_lines)
                
            else:
                result_lines.append(line)
            
            i += 1
        
        final_content = '\n'.join(result_lines)
        
        if self.debug:
            print(f"✅ FIXED processing complete: {self.stats.code_blocks_protected} blocks converted")
        
        return final_content
        
        # DODATNO: Zaščiti delne/nezaprete code bloke (robni scenariji)
        partial_patterns = [
            # Linijo z množino ``` ki morda ni pravilno zaprta
            (r'^(\s*)```[^\n]*\n(?!.*?```)', 'PARTIAL_CODE'),
        ]
        
        for pattern, block_type in partial_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            for match in reversed(matches):
                if len(match.group(0)) > 10:  # Samo daljši bloki
                    full_block = match.group(0)
                    block_id = f"PROTECTED_{block_type}_{uuid.uuid4().hex[:8]}"
                    self.protected_blocks[block_id] = full_block
                    content = content[:match.start()] + block_id + content[match.end():]
            
        return content
    
    def _protect_python_dictionaries(self, content: str) -> str:
        """Zaščiti Python slovarje."""
        
        dict_pattern = r'\{[^{}]*:[^{}]*\}'
        matches = list(re.finditer(dict_pattern, content))
        
        for match in reversed(matches):
            dict_content = match.group(0)
            if ':' in dict_content:
                block_id = f"PROTECTED_DICT_{uuid.uuid4().hex[:8]}"
                self.protected_blocks[block_id] = dict_content
                content = content[:match.start()] + block_id + content[match.end():]
                
        return content
    
    def _protect_python_comments(self, content: str) -> str:
        """Zaščiti Python komentarje."""
        
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            # Python komentarji z # (ne markdown header!)
            if re.match(r'^\s*#[^#\s]', line):
                block_id = f"PROTECTED_COMMENT_{uuid.uuid4().hex[:8]}"
                self.protected_blocks[block_id] = line
                result_lines.append(block_id)
            else:
                result_lines.append(line)
                
        return '\n'.join(result_lines)
    
    def _protect_generic_code_blocks(self, content: str) -> str:
        """Zaščiti vse ostale code bloke z uporabo izboljšanega regex pristopa."""
        
        # REŠITEV: Uporabimo regex, vendar z non-greedy matching in boljšim pristopom
        # Prvo zaščitimo osnovne, enkratne code bloke (ne nested)
        simple_pattern = r'```(\w+)\n([^`]+?)\n```'
        matches = list(re.finditer(simple_pattern, content, re.DOTALL))
        
        # Sortiraj od zadaj naprej za pravilno replacement
        for match in reversed(matches):
            full_block = match.group(0)
            lang = match.group(1) or "generic"
            content_inside = match.group(2)
            
            # Zaščiti samo če nima nested ``` znotraj
            if '```' not in content_inside:
                block_id = f"PROTECTED_CODE_{lang}_{uuid.uuid4().hex[:8]}"
                self.protected_blocks[block_id] = full_block
                content = content[:match.start()] + block_id + content[match.end():]
                self.stats.code_blocks_protected += 1
        
        # Nato zaščitimo kompleksnejše strukture (z možnimi nested elementi)
        # Za ``` brez jezika
        generic_pattern = r'```\n([^`]*(?:`[^`][^`]*)*)\n```'
        matches = list(re.finditer(generic_pattern, content, re.DOTALL))
        
        for match in reversed(matches):
            full_block = match.group(0)
            block_id = f"PROTECTED_CODE_generic_{uuid.uuid4().hex[:8]}"
            self.protected_blocks[block_id] = full_block
            content = content[:match.start()] + block_id + content[match.end():]
            self.stats.code_blocks_protected += 1
        
        return content

    def _step2_unified_markdown_conversion(self, content: str) -> str:
        """STEP 2: Unified Markdown → Typst konverzija"""
        
        # Najprej obdelamo tabele (ker te potrebujejo multi-line analizo)
        content = self._convert_tables(content)
        
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Preskoči zaščitene bloke
            if line.strip().startswith('PROTECTED_'):
                converted_lines.append(line)
                continue
                
            # Preskoči že konvertirane raw bloke
            if line.strip().startswith('#raw('):
                converted_lines.append(line)
                continue
                
            # Preskoči že konvertirane tabele
            if line.strip().startswith('#table'):
                converted_lines.append(line)
                continue
                
            # Aplikacija konverzijskih pravil
            converted_line = line
            converted_line = self._convert_headers(converted_line)
            converted_line = self._convert_bold(converted_line)  # NAJPREJ bold!
            converted_line = self._convert_italic(converted_line)  # POTEM italic!
            converted_line = self._convert_inline_code(converted_line)
            converted_line = self._convert_unordered_lists(converted_line)
            converted_line = self._convert_ordered_lists(converted_line)
            converted_line = self._convert_links(converted_line)
            
            converted_lines.append(converted_line)
            
        return '\n'.join(converted_lines)
    
    def _convert_headers(self, line: str) -> str:
        """Konverzija Markdown headerjev → Typst"""
        
        if not line.strip().startswith('#'):
            return line
            
        match = re.match(r'^(\s*)(#{1,6})\s+(.+)$', line)
        if not match:
            return line
            
        indent, hashes, title = match.groups()
        header_level = len(hashes)
        
        typst_header = indent + '=' * header_level + ' ' + title
        self.stats.headers_converted += 1
        
        return typst_header
    
    def _convert_bold(self, line: str) -> str:
        """Konverzija bold: **text** → placeholder"""
        
        def replace_bold(match):
            text = match.group(1)
            placeholder = f"BOLD_PLACEHOLDER_{uuid.uuid4().hex[:8]}"
            # Keep double asterisks for Typst bold syntax
            self.bold_placeholders[placeholder] = f"**{text}**"
            self.stats.formatting_converted += 1
            return placeholder
            
        return re.sub(r'\*\*([^\*]+)\*\*', replace_bold, line)
    
    def _convert_italic(self, line: str) -> str:
        """Konverzija italic: *text* → _text_"""
        
        def replace_italic(match):
            full_match = match.group(0)
            if 'BOLD_PLACEHOLDER' in full_match:
                return full_match
                
            text = match.group(1)
            self.stats.formatting_converted += 1
            return f'_{text}_'
            
        return re.sub(r'\*([^\*\n]+)\*', replace_italic, line)
    
    def _convert_inline_code(self, line: str) -> str:
        """Konverzija inline kode: `code` → #raw("code") AND `` `code` `` → #raw("`code`")"""
        
        def replace_inline_code(match):
            code_content = match.group(1)
            self.stats.inline_code_converted += 1
            return f'#raw("{code_content}")'
        
        # First handle double backticks: `` any content including backticks ``
        # Pattern allows backticks inside by using non-greedy match of any character
        line = re.sub(r'``\s*(.*?)\s*``', replace_inline_code, line)
        
        # Then handle single backticks: `content` (but avoid already processed #raw)
        # Only match single backticks that are not part of #raw() calls
        line = re.sub(r'(?<!#raw\(")\\`([^`]+)\\`(?!")', replace_inline_code, line)
        
        return line
    
    def _convert_unordered_lists(self, line: str) -> str:
        """Konverzija unordered lists"""
        
        match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
        if match:
            indent, content = match.groups()
            self.stats.lists_converted += 1
            return f'{indent}- {content}'
            
        return line
    
    def _convert_ordered_lists(self, line: str) -> str:
        """Konverzija ordered lists"""
        
        match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        if match:
            indent, content = match.groups()
            self.stats.lists_converted += 1
            return f'{indent}+ {content}'
            
        return line
    
    def _convert_links(self, line: str) -> str:
        """Konverzija links: [text](url) → link("url")[text]"""
        
        def replace_link(match):
            text, url = match.groups()
            return f'link("{url}")[{text}]'
            
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, line)

    def _convert_tables(self, content: str) -> str:
        """Konverzija Markdown tabel → Typst tabele"""
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Prepoznaj tabelo (linija s '|' znaki)
            if '|' in line and line.strip():
                table_lines = []
                
                # Zberi vse linije tabele
                while i < len(lines) and ('|' in lines[i] or lines[i].strip() == '' or lines[i].strip().replace('-', '').replace('|', '').replace(':', '').strip() == ''):
                    if '|' in lines[i]:
                        table_lines.append(lines[i])
                    i += 1
                
                # Konvertiraj tabelo
                if len(table_lines) >= 2:  # Tabela mora imeti vsaj header in ena vrstica
                    typst_table = self._markdown_table_to_typst(table_lines)
                    result_lines.append(typst_table)
                    self.stats.lists_converted += 1  # Uporabimo obstoječo statistiko
                else:
                    result_lines.extend(table_lines)
                    i += 1
            else:
                result_lines.append(line)
                i += 1
        
        return '\n'.join(result_lines)
    
    def _markdown_table_to_typst(self, table_lines):
        """Konverzija Markdown tabele v Typst format"""
        
        # Izloči separator linije (z --- znaki)
        clean_lines = []
        for line in table_lines:
            if not re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
                clean_lines.append(line)
        
        if len(clean_lines) < 1:
            return '\n'.join(table_lines)  # Fallback
            
        # Parsiraj celice
        parsed_rows = []
        for line in clean_lines:
            # Odstrani začetni in končni |
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            if cells:  # Samo če imamo celice
                parsed_rows.append(cells)
        
        if not parsed_rows:
            return '\n'.join(table_lines)  # Fallback
            
        # Zgenerirај Typst tabelo
        num_cols = len(parsed_rows[0]) if parsed_rows else 1
        
        # Begin tabela
        typst_lines = ['#table(']
        typst_lines.append(f'  columns: {num_cols},')
        typst_lines.append('  stroke: 0.5pt,')
        typst_lines.append('  inset: 5pt,')
        
        # Dodaj celice
        for row_idx, row in enumerate(parsed_rows):
            for cell_idx, cell in enumerate(row):
                # Escape posebne znake za Typst
                escaped_cell = self._escape_typst_characters(cell)
                
                # Prvi red = header
                if row_idx == 0:
                    typst_lines.append(f'  [*{escaped_cell}*],')
                else:
                    typst_lines.append(f'  [{escaped_cell}],')
        
        typst_lines.append(')')
        typst_lines.append('')  # Prazen red za boljši izgled
        
        return '\n'.join(typst_lines)
    
    def _escape_typst_characters(self, text: str) -> str:
        """Pobegni posebne znake za Typst in konvertiraj markdown formatting"""
        
        # Ta metoda se kliče ZA table celice, ki so že šle skozi main conversion
        # Potrebujemo ohraniti #raw() bloke, vendar jih konvertirati v backticks za tabele
        
        # Konvertiraj #raw("content") nazaj v `content` za tabele
        def convert_raw_to_backticks(match):
            content = match.group(1)
            return f'`{content}`'
        
        text = re.sub(r'#raw\("([^"]*)"\)', convert_raw_to_backticks, text)
        
        # Escapaj posebne znaki za Typst
        text = re.sub(r'(?<!\\)\$', r'\\$', text)  # Dollar znaki
        text = text.replace('#', r'\#')  # Hash znaki  
        text = text.replace('"', r'\"')  # Narekovaji
        
        return text

    def _step3_character_sanitization(self, content: str) -> str:
        """STEP 3: Karakterni sanitization za Typst kompatibilnost"""
        
        # Osnovni sanitization (ohranjamo iz originala)
        sanitization_rules = [
            (r'[""]', '"'),  # Smart quotes
            (r"['']", "'"),  # Smart apostrophes - fixed quote escaping
            (r'[–—]', '-'),  # Em/en dashes
            (r'…', '...'),   # Ellipsis
        ]
        
        for pattern, replacement in sanitization_rules:
            content = re.sub(pattern, replacement, content)
        
        # Handle non-ASCII separately with better pattern
        content = re.sub(r'[^\x00-\x7F]', lambda m: self._handle_unicode_char(m.group()), content)
                
        return content
    
    def _handle_unicode_char(self, char: str) -> str:
        """Pametno rokovanje z Unicode karakterji"""
        
        # Ohranimo osnovne Unicode znaki ki so kompatibilni s Typst
        safe_unicode = {
            '→': '→',  # Arrow
            '←': '←',  # Arrow  
            '✓': '✓',  # Checkmark
            '✗': '✗',  # X mark
            '…': '...',  # Ellipsis
        }
        
        return safe_unicode.get(char, char)  # Ohrani če je safe, sicer vrni original

    def _step4_restore_protected_content(self, content: str) -> str:
        """STEP 4: Obnovi zaščitene bloke - ULTRA-ROBUSTNO"""
        
        if self.debug:
            print(f"🔓 Starting restoration of {len(self.protected_blocks)} protected blocks")
        
        # Najprej bold placeholderje
        for placeholder, bold_text in self.bold_placeholders.items():
            if placeholder in content:
                content = content.replace(placeholder, bold_text, 1)  # Only replace once!
                if self.debug:
                    print(f"✅ Restored bold: {placeholder}")
            
        # Potem protected bloke - ZELO PREVIDNO
        restored_count = 0
        for block_id, original_content in self.protected_blocks.items():
            if block_id in content:
                # Count occurrences to prevent duplication
                occurrences = content.count(block_id)
                if occurrences == 1:
                    content = content.replace(block_id, original_content, 1)
                    restored_count += 1
                    if self.debug:
                        print(f"✅ Restored block: {block_id}")
                elif occurrences > 1:
                    if self.debug:
                        print(f"⚠️  Multiple occurrences of {block_id}: {occurrences}")
                    # Replace all occurrences but with same content
                    content = content.replace(block_id, original_content)
                    restored_count += 1
            else:
                if self.debug:
                    print(f"⚠️  Block {block_id} not found in content")
        
        if self.debug:
            print(f"🔓 Restoration complete: {restored_count}/{len(self.protected_blocks)} blocks restored")
            
        return content

    def _step5_final_cleanup(self, content: str) -> str:
        """STEP 5: Finalno čiščenje"""
        
        # Odstrani preveč praznih vrstic
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Očisti presledke na koncu vrstic
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        return '\n'.join(cleaned_lines)
    
    def _log_optimization_stats(self):
        """Debug statistike"""
        
        self.logger.info("📊 UNIFIED OPTIMIZATION STATISTICS:")
        self.logger.info(f"  • Headers converted: {self.stats.headers_converted}")
        self.logger.info(f"  • Code blocks protected: {self.stats.code_blocks_protected}")
        self.logger.info(f"  • Inline code converted: {self.stats.inline_code_converted}")
        self.logger.info(f"  • Lists converted: {self.stats.lists_converted}")
        self.logger.info(f"  • Formatting converted: {self.stats.formatting_converted}")

# ============================================================================
# BACKWARD COMPATIBILITY - Ohrani obstoječo TypstContentOptimizer interface
# ============================================================================

class TypstContentOptimizer(UnifiedTypstContentOptimizer):
    """
    Backward compatibility wrapper za obstoječo TypstContentOptimizer
    """
    
    def __init__(self):
        super().__init__(debug=False)
        # Ohrani staro interface
        self.logger = logging.getLogger(__name__)
        self.protected_blocks = {}
        
    # Ohrani stare metode imena za kompatibilnost
    def _markdown_to_typst_converter(self, content: str) -> str:
        """Backward compatibility za staro metodo"""
        return self._step2_unified_markdown_conversion(content)
        
    def _protect_code_blocks(self, content: str) -> str:
        """Backward compatibility za staro metodo"""
        return self._step1_protect_critical_blocks(content)
        
    def _restore_code_blocks(self, content: str) -> str:
        """Backward compatibility za staro metodo"""
        return self._step4_restore_protected_content(content)

# ============================================================================
# TESTING
# ============================================================================

def test_unified_optimizer():
    """Test unified optimizerja"""
    
    test_markdown = """# Test document

## Section with **bold** and *italic*

Here's some `inline code` and a [link](https://example.com).

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Row 2    | Value A  | Value B  |

```python
# Python comment  
config = {
    "setting": "value"
}
```

- List item 1
- List item 2

1. Numbered item
2. Another item
"""
    
    optimizer = UnifiedTypstContentOptimizer(debug=True)
    result = optimizer.optimize_content_for_typst(test_markdown)
    
    print("🚀 UNIFIED TYPST OPTIMIZER TEST")
    print("="*50)
    print("\nINPUT:")
    print("-"*30)
    print(test_markdown)
    print("\nOUTPUT:")
    print("-"*30)
    print(result)
    print("\n" + "="*50)

if __name__ == "__main__":
    test_unified_optimizer()
