import pandas as pd
import pymupdf
import docx
import hashlib
import os
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


def save_data(chatid: int, age: str, sex: str, table: str, analysis: str) -> None:
    dirs = [os.path.join('data', 'tables'), os.path.join('data', 'analyses')]
    file = hashlib.sha256(str(chatid).encode()).hexdigest() + '_1'
    counter = 2
    for dir in dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)
        while os.path.exists(os.path.join(dir, file)):
            file = file[:-1] + str(counter)
            counter += 1
        with open(os.path.join(dir, file), 'w') as f:
            if dir.endswith('tables'):
                f.write('# Age: ' + str(age) + '\n')
                f.write('# Sex: ' + sex + '\n')
                f.write(table)
            else:
                f.write(analysis)