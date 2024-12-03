import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import pyheif
from io import BytesIO
from typing import List, Dict, Union

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def read_document(file: BytesIO, language='rus') -> str:
    """
    Extracts text from a PDF or other image-based documents using OCR (Tesseract).
    
    Arguments
    ---------
    * file - BytesIO object
    * language - Language for OCR (default is 'rus')
    
    Returns
    -------
    * String with full document text    
    """

    # Сохраняем временный файл для обработки через pdf2image
    temp_file_path = 'temp_pdf_file.pdf'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file.read())
    
    # Определяем расширение файла
    file_extension = os.path.splitext(temp_file_path)[1].lower()
    full_text = ""

    # Если файл PDF
    if file_extension == '.pdf':
        images = convert_from_path(temp_file_path)
        for image in images:
            # Используем Tesseract для извлечения текста с изображений
            text = pytesseract.image_to_string(image, lang=language)
            full_text += text + "\n"

    # Если файл HEIC (фотографии iOS)
    elif file_extension == '.heic':
        heif_file = pyheif.read(temp_file_path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        text = pytesseract.image_to_string(image, lang=language)
        full_text += text

    # Если файл изображение
    elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        image = Image.open(temp_file_path)
        text = pytesseract.image_to_string(image, lang=language)
        full_text += text

    # Удаляем временный файл после обработки
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    print("Расшифрованный текст: \n", full_text)

    return full_text if full_text else "No text found or unsupported file type"