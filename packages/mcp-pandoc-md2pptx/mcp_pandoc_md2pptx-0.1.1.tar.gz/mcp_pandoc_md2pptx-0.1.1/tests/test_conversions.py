import pypandoc
import os
import pytest

# Define paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

# Ensure directories exist
for dir_path in [FIXTURE_DIR, OUTPUT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Create markdown test fixture
markdown_content = """# Test Presentation

## Slide 1
This is the first slide with some content.

## Slide 2
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Slide 3
**Bold text** and *italic text* for formatting test.
"""

with open(os.path.join(FIXTURE_DIR, 'test.md'), 'w') as f:
    f.write(markdown_content)

def test_markdown_to_pptx_conversion():
    """Test converting markdown to PPTX format."""
    input_file = os.path.join(FIXTURE_DIR, 'test.md')
    output_file = os.path.join(OUTPUT_DIR, 'test.pptx')
    
    # Remove output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Convert markdown to PPTX
    pypandoc.convert_file(input_file, 'pptx', outputfile=output_file)
    
    # Verify output file was created
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0

def test_markdown_content_to_pptx():
    """Test converting markdown content string to PPTX format."""
    output_file = os.path.join(OUTPUT_DIR, 'content_test.pptx')
    
    # Remove output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Convert markdown content to PPTX
    pypandoc.convert_text(markdown_content, 'pptx', format='markdown', outputfile=output_file)
    
    # Verify output file was created
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0

def test_markdown_to_pptx_with_template():
    """Test converting markdown to PPTX with a template."""
    # First create a basic template
    template_file = os.path.join(FIXTURE_DIR, 'template.pptx')
    pypandoc.convert_text('# Template', 'pptx', format='markdown', outputfile=template_file)
    
    input_file = os.path.join(FIXTURE_DIR, 'test.md')
    output_file = os.path.join(OUTPUT_DIR, 'templated_test.pptx')
    
    # Remove output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Convert with template (use --reference-doc for PPTX)
    pypandoc.convert_file(
        input_file, 
        'pptx', 
        outputfile=output_file,
        extra_args=['--reference-doc', template_file]
    )
    
    # Verify output file was created
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0
