"""
🧪 WOT-PDF Tests
================
Unit tests for WOT-PDF package
"""

import pytest
import tempfile
import os
from pathlib import Path

from wot_pdf import PDFGenerator, generate_pdf, generate_book


class TestPDFGenerator:
    """Test core PDF generation"""
    
    def test_generator_init(self):
        """Test generator initialization"""
        generator = PDFGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate')
    
    def test_reportlab_fallback(self):
        """Test ReportLab fallback engine"""
        generator = PDFGenerator()
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            try:
                result = generator.generate(
                    input_content="# Test Document\n\nSimple test.",
                    output_file=tmp.name,
                    template="minimal",
                    force_engine="reportlab"
                )
                
                assert result["success"] is True
                assert os.path.exists(tmp.name)
                assert os.path.getsize(tmp.name) > 0
                
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)


class TestAPI:
    """Test high-level API functions"""
    
    def test_generate_pdf_with_file(self):
        """Test PDF generation from file"""
        
        # Create test markdown file
        test_content = "# API Test\n\nTesting the API."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as input_file:
            input_file.write(test_content)
            input_file.flush()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
                try:
                    result = generate_pdf(
                        input_content=input_file.name,
                        output_file=output_file.name,
                        template="minimal"
                    )
                    
                    assert result["success"] is True
                    assert os.path.exists(output_file.name)
                    
                finally:
                    for file_path in [input_file.name, output_file.name]:
                        if os.path.exists(file_path):
                            os.unlink(file_path)
    
    def test_generate_pdf_with_content(self):
        """Test PDF generation from content string"""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            try:
                result = generate_pdf(
                    input_content="# String Test\n\nDirect content test.",
                    output_file=tmp.name,
                    template="minimal"
                )
                
                assert result["success"] is True
                assert os.path.exists(tmp.name)
                assert result["file_size_bytes"] > 0
                
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)


class TestBookGeneration:
    """Test book generation from directories"""
    
    def test_generate_book_from_directory(self):
        """Test book generation from markdown directory"""
        
        # Create temporary directory with markdown files
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Create test markdown files
            test_files = {
                "01_intro.md": "# Introduction\n\nWelcome to the book.",
                "02_chapter.md": "# Chapter 2\n\nMain content here.",
                "03_conclusion.md": "# Conclusion\n\nThat's all folks!"
            }
            
            for filename, content in test_files.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Generate book
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
                try:
                    result = generate_book(
                        input_dir=temp_dir,
                        output_file=output_file.name,
                        template="minimal",
                        title="Test Book"
                    )
                    
                    assert result["success"] is True
                    assert os.path.exists(output_file.name)
                    assert result["source_files"] == 3
                    assert result["file_size_bytes"] > 0
                    
                finally:
                    if os.path.exists(output_file.name):
                        os.unlink(output_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
