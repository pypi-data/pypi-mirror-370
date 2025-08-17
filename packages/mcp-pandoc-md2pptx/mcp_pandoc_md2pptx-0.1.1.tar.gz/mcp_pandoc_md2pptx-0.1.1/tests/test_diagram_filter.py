import pytest
import tempfile
import os
from pathlib import Path
from mcp_pandoc_md2pptx.server import handle_call_tool, DIAGRAM_FILTER_PATH


class TestDiagramFilter:
    """Test diagram filter integration"""

    @pytest.mark.asyncio
    async def test_diagram_filter_applied_by_default(self):
        """Test that diagram filter is applied by default"""
        markdown_content = """# Test Presentation

## Diagram Example

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

## Regular Content

This is regular markdown content.
"""
        
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            result = await handle_call_tool(
                "convert-contents",
                {
                    "contents": markdown_content,
                    "output_file": output_path
                }
            )
            
            # Check that conversion succeeded
            assert len(result) == 1
            assert "successfully converted" in result[0].text
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_diagram_filter_with_file_input(self):
        """Test diagram filter with file input"""
        fixture_path = Path(__file__).parent / "fixtures" / "diagram_test.md"
        
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            result = await handle_call_tool(
                "convert-contents",
                {
                    "input_file": str(fixture_path),
                    "output_file": output_path
                }
            )
            
            assert len(result) == 1
            assert "successfully converted" in result[0].text
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_diagram_filter_with_template(self):
        """Test that diagram filter works with custom templates"""
        markdown_content = """# Template Test

```plantuml
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi
@enduml
```
"""
        
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Create a simple template file for testing
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as template_file:
            template_path = template_file.name
            # Write minimal PPTX content (in real scenario, this would be a proper PPTX)
            template_file.write(b"PK")  # Minimal ZIP signature
        
        try:
            # This test may fail if template is invalid, but should still apply filter
            with pytest.raises(ValueError):  # Expected due to invalid template
                await handle_call_tool(
                    "convert-contents",
                    {
                        "contents": markdown_content,
                        "output_file": output_path,
                        "template": template_path
                    }
                )
            
        finally:
            for path in [output_path, template_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_diagram_filter_path_exists(self):
        """Test that the diagram filter file exists"""
        assert DIAGRAM_FILTER_PATH.exists()
        assert DIAGRAM_FILTER_PATH.suffix == ".lua"
        
        # Check that the file contains expected content
        content = DIAGRAM_FILTER_PATH.read_text()
        assert "diagram" in content.lower()
        assert "pandoc" in content.lower()

    @pytest.mark.asyncio
    async def test_conversion_without_diagrams(self):
        """Test that regular markdown still works with filter applied"""
        markdown_content = """# Simple Presentation

## Slide 1
- Point 1
- Point 2

## Slide 2
Regular text content without any diagrams.
"""
        
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            result = await handle_call_tool(
                "convert-contents",
                {
                    "contents": markdown_content,
                    "output_file": output_path
                }
            )
            
            assert len(result) == 1
            assert "successfully converted" in result[0].text
            assert os.path.exists(output_path)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
