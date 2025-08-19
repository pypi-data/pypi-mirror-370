# Wokelo Docs

**Create, read, and update Microsoft Word (.docx) and PowerPoint (.pptx) files with extended features**

Wokelo Docs is an open-source Python library that merges and extends the functionality of [**python-docx**](https://github.com/python-openxml/python-docx) and [**python-pptx**](https://github.com/scanny/python-pptx), empowering developers to automate and enhance document and presentation creation. This library is designed to enable seamless generation and manipulation of Microsoft Word and PowerPoint files without requiring Microsoft Office.

## Features

### Word Enhancements
- Native support for **comments** and **footnotes**.
- Enhanced chart support, allowing the addition of dynamic charts to Word documents, positioning and scaling them with precision.

### PowerPoint Enhancements
- New functionality for **adding and manipulating pictures** in slide masters with improved picture shape ID management.

### Office File Analysis
- Extract text and images from both Word and PowerPoint files.


## Installation

Install via pip:

```bash
pip install wokelo-docs
```

## Usage

### Word Documents (.docx)

Create and manipulate Word documents, including comments and footnotes

```python
from wokelo_docs.docx import Document
from datetime import datetime

# Create document with comprehensive comment usage
doc = Document()

# Add content
p1 = doc.add_paragraph("This is the introduction paragraph.")
p2 = doc.add_paragraph("This paragraph contains important information.")

# Add comments to specific runs
intro_run = p1.runs[0]
intro_comment = intro_run.add_comment(
    text="Consider expanding this introduction",
    author="Reviewer 1",
    initials="R1",
    dtime=datetime.now().isoformat()
)

important_run = p2.runs[0]
important_comment = important_run.add_comment(
    text="This needs fact-checking",
    author="Editor",
    initials="ED"
)

# Save and later read comments
doc.save('reviewed_document.docx')

# Read comments back
doc2 = Document('reviewed_document.docx')
for paragraph in doc2.paragraphs:
    for run in paragraph.runs:
        if run.comments:
            for comment in run.comments:
                print(f"{comment.author}: {comment.text}")
```

### PowerPoint Presentations (.pptx)

Create and update PowerPoint presentations, suitable for dynamic content or automation.

```python
from wokelo_docs.pptx import Presentation
from wokelo_docs.pptx.enum.shapes import MSO_SHAPE
from wokelo_docs.pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])

# Create individual shapes first
shape1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(1), Inches(1))
shape2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(2.5), Inches(1), Inches(1), Inches(1))
shape3 = slide.shapes.add_shape(MSO_SHAPE.TRIANGLE, Inches(1.75), Inches(2.5), Inches(1), Inches(1))

# Create a group with the shapes
group = slide.shapes.add_group_shape([shape1, shape2, shape3])

# The group automatically calculates its extents based on contained shapes
print(f"Group position: ({group.left}, {group.top})")
print(f"Group size: {group.width} x {group.height}")

# Add more shapes to the group
group_shapes = group.shapes
new_shape = group_shapes.add_shape(
    MSO_SHAPE.STAR_5_POINT,
    Inches(0.5),  # Relative to group
    Inches(0.5),
    Inches(0.5),
    Inches(0.5)
)

prs.save('presentation_with_groups.pptx')
```

For documentation, please refer [Docs](./Docs/)

## Acknowledgment
Wokelo Docs leverages the incredible work done by the open-source projects [**python-docx**](https://github.com/python-openxml/python-docx) and [**python-pptx**](https://github.com/scanny/python-pptx) for handling Microsoft Word and PowerPoint file operations. These libraries form the foundation of Wokelo Docs, upon which we've added enhanced features for more dynamic content generation and richer document functionality.


## License

This project is dual-licensed under the MIT License and the Apache 2.0 License  [LICENSE](LICENSE)

The core code of the project is licensed under the MIT License.

New features, enhancements, or contributions are licensed under the Apache 2.0 License.