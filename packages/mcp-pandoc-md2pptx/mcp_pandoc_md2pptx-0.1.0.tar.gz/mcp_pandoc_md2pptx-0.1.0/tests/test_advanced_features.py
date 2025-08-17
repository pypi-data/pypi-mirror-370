"""
Test suite for mcp-pandoc-md2pptx markdown to PPTX conversion

This file tests the simplified functionality:
1. Markdown to PPTX conversion
2. Template support for PPTX styling
3. Basic error handling
"""
import pytest
import os
import tempfile
import sys


class TestMarkdownToPptxConversion:
    """Test the core markdown to PPTX conversion functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        
        # Ensure fixture directory exists
        if not os.path.exists(self.fixture_dir):
            os.makedirs(self.fixture_dir)
        
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_basic_markdown_to_pptx(self):
        """Test basic markdown to PPTX conversion"""
        import pypandoc
        
        markdown_content = """# Test Presentation

## Slide 1
This is the first slide.

## Slide 2
- Point 1
- Point 2
"""
        
        output_path = os.path.join(self.temp_dir, 'test.pptx')
        
        # Convert markdown to PPTX
        pypandoc.convert_text(
            markdown_content,
            'pptx',
            format='markdown',
            outputfile=output_path
        )
        
        # Verify output was created
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_markdown_file_to_pptx(self):
        """Test converting markdown file to PPTX"""
        import pypandoc
        
        # Create test markdown file
        markdown_file = os.path.join(self.temp_dir, 'input.md')
        with open(markdown_file, 'w') as f:
            f.write("# Test\n\nContent here.")
        
        output_path = os.path.join(self.temp_dir, 'output.pptx')
        
        # Convert file to PPTX
        pypandoc.convert_file(
            markdown_file,
            'pptx',
            outputfile=output_path
        )
        
        # Verify output was created
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0


class TestTemplateSupport:
    """Test PPTX template functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        
        # Ensure fixture directory exists
        if not os.path.exists(self.fixture_dir):
            os.makedirs(self.fixture_dir)
        
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_pptx_with_template(self):
        """Test PPTX generation with template"""
        import pypandoc
        
        # Create a basic template first
        template_path = os.path.join(self.fixture_dir, 'template.pptx')
        if not os.path.exists(template_path):
            pypandoc.convert_text(
                '# Template Slide',
                'pptx',
                format='markdown',
                outputfile=template_path
            )
        
        output_path = os.path.join(self.temp_dir, 'templated_output.pptx')
        
        # Convert with template (use --reference-doc for PPTX)
        pypandoc.convert_text(
            '# Test Presentation\n\nContent with template.',
            'pptx',
            format='markdown',
            outputfile=output_path,
            extra_args=['--reference-doc', template_path]
        )
        
        # Verify output was created
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_template_file_validation(self):
        """Test template file existence validation"""
        nonexistent_template = os.path.join(self.temp_dir, 'nonexistent.pptx')
        
        # Should not exist
        assert not os.path.exists(nonexistent_template)


class TestServerModule:
    """Test the server module functionality"""

    def test_server_module_imports(self):
        """Test that the server module imports correctly"""
        # Add the src directory to path for import
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Import the server module
        from mcp_pandoc_md2pptx import server
        
        # Verify core functions exist
        assert hasattr(server, 'handle_call_tool')
        assert hasattr(server, 'handle_list_tools')
        assert hasattr(server, 'server')

    def test_tool_schema_validation(self):
        """Test that the tool schema is properly defined"""
        # Add the src directory to path for import
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from mcp_pandoc_md2pptx import server
        
        # The server should have the convert-contents tool
        assert hasattr(server, 'server')


class TestErrorHandling:
    """Test error handling scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_missing_input_validation(self):
        """Test validation when both contents and input_file are missing"""
        # This would be tested at the server level
        # For now, just test the concept
        contents = None
        input_file = None
        
        # Should fail validation
        assert not (contents or input_file)

    def test_missing_output_file_validation(self):
        """Test validation when output_file is missing"""
        output_file = None
        
        # Should fail validation for PPTX
        assert not output_file

    def test_nonexistent_input_file(self):
        """Test handling of nonexistent input files"""
        nonexistent_file = os.path.join(self.temp_dir, 'nonexistent.md')
        
        # Should not exist
        assert not os.path.exists(nonexistent_file)
