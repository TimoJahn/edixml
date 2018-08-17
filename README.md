# edixml - UN/EDIFACT Message Reader
## Requirements 
- Python 3.6 or higher

## Features
- All encodings
- Version independent
- XML

## Functions
- parse_edi(data: bytes) -> list
- make_edi(segments: list) -> bytes
- parse_xml(root: ElementTree.Element) -> list
- make_xml(segments: list) -> ElementTree.Element
- pretty_xml(root: ElementTree.Element) -> str

Read the EDIXML.ipynb or play with the Tk-UI gui.py 
