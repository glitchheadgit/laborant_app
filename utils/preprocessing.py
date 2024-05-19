import pymupdf
import docx
import requests
import re
import ast
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


def format_with_yangex_gpt(prompt_main: str) -> List[Dict[str, Union[str, int, float]]]:
    """
    Format user analysis prompt to a python list of dictionaries
    
    Arguments
    ---------
    * prompt_main - User analyses input

    Returns
    -------
    * List of dictionaries with analysis type, its value and measurement unit as keys
    """

    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': f'API-key {config.yandex_gpt_api.get_secret_value()}',
        "Content-Type": "application/json",
    }
    data = {
      "modelUri": f"gpt://{config.yandex_gpt_catalogue.get_secret_value()}/yandexgpt",
      "completionOptions": {
        "stream": False,
        "temperature": 0.3,
        "maxTokens": "2000"
      },
      "messages": [
        {
          "role": "system",
          "text": config.prompt_system.get_secret_value()
        },
        {
          "role": "user", 
          "text": config.prompt_user.get_secret_value() + prompt_main
        }
      ]
    }

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                {resp.status_code}, {resp.text}
            )
        )
    else:
        print(ast.literal_eval(resp.text))
        result = ast.literal_eval(resp.text)['result']['alternatives'][0]['message']['text']
        result = re.sub(r'\n', ' ', result)
        result = re.sub(r'\s\s+', '', result)
        return re.search(r'\[.*\]', result).group()