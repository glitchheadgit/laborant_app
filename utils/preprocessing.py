import pymupdf
import docx
import requests
import re
from io import BytesIO
from config_reader import config
from typing import List, Dict, Union


def read_pdf(file: BytesIO) -> str:
    """
    Extracts text from pdf
    Arguments
    ---------
    * file - BytesIO object

    Returns
    -------
    * String with full document text    
    """
    with pymupdf.open('pdf', file) as pdf:
        return chr(12).join([page.get_text() for page in pdf])


def read_docx(file: BytesIO) -> str:
    """
    Extracts text from docx
    Arguments
    ---------
    * file - BytesIO object

    Returns
    -------
    * String with full document text    
    """
    doc = docx.Document(file)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

# def add_state(csv: str) -> str:
#     csv = csv.split(',')
#     for