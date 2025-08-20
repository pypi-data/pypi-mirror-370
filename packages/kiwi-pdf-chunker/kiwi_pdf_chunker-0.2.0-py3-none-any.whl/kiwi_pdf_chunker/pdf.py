"""
PDF processing module.

This module contains functions for processing PDF documents, including
converting PDFs to images.
"""

import io
import gc
import logging
from PIL import Image
import fitz  # PyMuPDF

from .config import ZOOM_FACTOR

# Configure logging
logger = logging.getLogger(__name__)

def pdf_to_images(pdf_path, zoom=None): 

    """
    Reads a PDF file and converts each page into a high-resolution PIL Image.

    Args:
        pdf_path (str): The file path to the PDF.
        zoom (float, optional): Scaling factor for the image resolution.
            Defaults to the value in config.

    Returns:
        dict: A dictionary where keys are page numbers (1-indexed) and values are
            high-resolution PIL Images.
    """
    if zoom is None:
        zoom = ZOOM_FACTOR

    images = {}
    try:
        pdf_document = fitz.open(pdf_path)  # Open the PDF file

        for page_number in range(len(pdf_document)):
            
            page = pdf_document.load_page(page_number)  # Load page
            matrix = fitz.Matrix(zoom, zoom)  # Scale the image for higher resolution
            pixmap = page.get_pixmap(matrix=matrix)  # Render the page to a pixmap

            # Convert pixmap to PIL Image
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            images[page_number + 1] = image  # Store the image in the dictionary

        pdf_document.close()  # Close the PDF document

    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {str(e)}")

    return images

def pdf_to_images_batched(pdf_path, page_numbers=None, zoom=None): 

    """
    Reads specific pages from a PDF file and converts them into high-resolution PIL Images.
    This function is memory-efficient for processing large PDFs.

    Args:
        pdf_path (str): The file path to the PDF.
        page_numbers (list, optional): List of page numbers to convert (1-indexed).
            If None, all pages will be converted.
        zoom (float, optional): Scaling factor for the image resolution.
            Defaults to the value in config.

    Returns:
        dict: A dictionary where keys are page numbers (1-indexed) and values are
            high-resolution PIL Images.
    """

    if zoom is None:
        zoom = ZOOM_FACTOR

    images = {}
    try:
        pdf_document = fitz.open(pdf_path)  # Open the PDF file
        
        # If no specific pages are requested, convert all pages
        if page_numbers is None:
            page_numbers = list(range(1, len(pdf_document) + 1))
            
        # Convert only the requested pages
        for page_number in page_numbers:

            if page_number < 1 or page_number > len(pdf_document):

                logger.warning(f"Page number {page_number} is out of range (1-{len(pdf_document)})")
                continue
                
            page = pdf_document.load_page(page_number - 1)  # Load page (0-indexed in fitz)
            matrix = fitz.Matrix(zoom, zoom)  # Scale the image for higher resolution
            pixmap = page.get_pixmap(matrix=matrix)  # Render the page to a pixmap

            # Convert pixmap to PIL Image
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            images[page_number] = image  # Store the image in the dictionary
            
            # Free memory
            pixmap = None
            gc.collect()

        pdf_document.close()  # Close the PDF document

    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {str(e)}")

    return images

def get_pdf_page_count(pdf_path): 
    """
    Get the number of pages in a PDF file.
    
    Args:
        pdf_path (str): The file path to the PDF.
        
    Returns:
        int: The number of pages in the PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        page_count = len(pdf_document)
        pdf_document.close()
        return page_count
    except Exception as e:
        logger.error(f"Error getting PDF page count: {str(e)}")
        return 0