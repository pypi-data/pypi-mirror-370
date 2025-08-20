"""
Main processing module for PDF parsing.
This module integrates all the components to process PDF documents,
extract text and structure, and save the results.
"""

import os
import gc
import json
import logging
from pathlib import Path
import tempfile  
from typing import Optional, Union
import requests

from .pdf import pdf_to_images

from .models import initialize_yolo_model

from .box_processing import (nms_merge_boxes, 
                             remove_inner_boxes, 
                             remove_container_boxes, 
                             sort_bounding_boxes, 
                             deduplicate_boxes, 
                             recover_missed_boxes,
                             get_box_class, 
                             remove_contained_bounding_boxes)

from .image_processing import annotate_image, save_annotated_image

from .config import OUTPUT_DIR, IOU_THRESHOLD, TEXT_LABELS, CONTAINER_THRESHOLD, DEFAULT_EMBEDDING_MODEL, SYSTEM_PROMPT

import torch
import pytesseract
from PIL import Image

from openai import OpenAI, AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.exceptions import ServiceRequestError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_openai_client(api_key: Optional[str] = None,
                      azure_api_key: Optional[str] = None,
                      api_version: Optional[str] = None,
                      azure_endpoint: Optional[str] = None) -> Union[OpenAI, AzureOpenAI]: 
    
    """
    Initializes and returns an appropriate OpenAI client (standard or Azure).
    """

    if azure_api_key and api_version and azure_endpoint: 

        logger.info("Initializing AzureOpenAI client for embeddings.")
        return AzureOpenAI(api_key = azure_api_key, api_version = api_version, azure_endpoint = azure_endpoint)
    
    elif api_key:
    
        logger.info("Initializing OpenAI client for embeddings.")
        return OpenAI(api_key=api_key)
    
    else:
    
        raise ValueError("Insufficient credentials provided for OpenAI client.")

class PDFParser: 

    """
    Main class for parsing PDF documents. Optionally performs OCR on extracted elements.
    """
    
    def __init__(self, 
                 yolo_model_path = None, 
                 debug_mode = False, 
                 container_threshold = None, 
                 ocr=False, 
                 azure_ocr_endpoint=None, 
                 azure_ocr_key=None, 
                 hierarchy=True,
                 embed=False,
                 classify_tables=False,
                 embedding_model=None,
                 openai_api_key=None,
                 azure_openai_api_key=None,
                 azure_openai_api_version=None,
                 azure_openai_endpoint=None): 
        
        """
        Initialize the PDF Parser.
        
        Args:
            yolo_model_path (str, optional): Path to the YOLO model file.
                If None, uses the default path from config.
            
            debug_mode (bool, optional): Enable debug mode with additional logging and outputs.
                Defaults to False.
            
            container_threshold (int, optional): Minimum number of contained boxes required
                to remove a container box. If None, uses the default from config.
            ocr (bool, optional): Enable OCR processing using Azure Document Intelligence.
                Defaults to False. Requires Azure credentials.
            hierarchy (bool, optional): Enable hierarchy generation.
                Defaults to True.
            azure_ocr_endpoint (str, optional): Azure Document Intelligence endpoint URL.
                Required if ocr is True. Defaults to env var AZURE_DOC_INTEL_ENDPOINT.
            azure_ocr_key (str, optional): Azure Document Intelligence API key.
                Required if ocr is True. Defaults to env var AZURE_DOC_INTEL_KEY.
            embed (bool, optional): If True, generate embeddings for extracted text.
                Defaults to False.
            classify_tables (bool, optional): If True, classify tables in the document.
                Defaults to False.
            embedding_model (str, optional): Name of the OpenAI model for embeddings.
                Defaults to the value in config.
            openai_api_key (str, optional): API key for standard OpenAI service.
            azure_openai_api_key (str, optional): API key for Azure OpenAI service (for embeddings and table classification).
            azure_openai_api_version (str, optional): API version for Azure OpenAI service.
            azure_openai_endpoint (str, optional): Endpoint URL for Azure OpenAI service (for embeddings and table classification).
        """

        self.yolo_model = initialize_yolo_model(yolo_model_path)
        self.debug_mode = debug_mode
        self.container_threshold = container_threshold or CONTAINER_THRESHOLD
        self.ocr = ocr
        self.hierarchy = hierarchy
        self.azure_ocr_endpoint = None
        self.azure_ocr_key = None
        self.document_client = None
        self.classify_tables = classify_tables

        # --- Embedding settings ---
        self.embed = embed
        self.embedding_model = embedding_model or DEFAULT_EMBEDDING_MODEL
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.azure_openai_api_key = azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_api_version = azure_openai_api_version or os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_openai_endpoint = azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_client = None
        
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            
        if self.ocr:

            self.azure_ocr_endpoint = azure_ocr_endpoint or os.getenv("AZURE_DOC_INTEL_ENDPOINT")
            self.azure_ocr_key = azure_ocr_key or os.getenv("AZURE_DOC_INTEL_KEY")

            if not self.azure_ocr_endpoint or not self.azure_ocr_key:

                raise ValueError("Azure endpoint and key are required for OCR. "
                                 "Provide them as arguments or set environment variables "
                                 "AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY.")

            try:
            
                self.document_client = DocumentIntelligenceClient(endpoint=self.azure_ocr_endpoint, credential=AzureKeyCredential(self.azure_ocr_key))
                logger.info("Azure Document Intelligence client initialized for OCR.")
            
            except Exception as e:
            
                logger.error(f"Failed to initialize Azure Document Intelligence client: {e}")
                raise ValueError(f"Failed to initialize Azure Document Intelligence client: {e}")
        
        # Validate embedding configuration if enabled
        if self.embed:
            if not self.ocr:
                logger.warning("Embedding is enabled, but OCR is disabled. No text will be available to embed.")
            
            # Check for valid credentials
            is_azure_configured = (self.azure_openai_api_key and self.azure_openai_api_version and self.azure_openai_endpoint)
            if not self.openai_api_key and not is_azure_configured:
                raise ValueError(
                    "Embedding is enabled, but no valid API credentials were provided. "
                    "Please provide either 'openai_api_key' or a complete set of Azure credentials."
                )

        # Prepare for memory-efficient processing if GPU is available 
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def parse_document(self, pdf_path, output_dir=None, generate_annotations=True, iou_threshold=None, save_bounding_boxes=True, use_tesseract = False):
        
        """
        Parse a PDF document, optionally performing OCR.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
            output_dir (str, optional): Directory to save output files.
                If None, uses the default from config.
            
            generate_annotations (bool, optional): Whether to generate annotated images.
                Defaults to True.
                        
            iou_threshold (float, optional): Threshold for merging bounding boxes.
                If None, uses the default from config.
            
            save_bounding_boxes (bool, optional): Whether to save individual bounding box images.
                Required for OCR. Defaults to True.

        Returns:
            dict: Dictionary containing the parsed document data.
        """

        if self.ocr and not save_bounding_boxes: 
            
            logger.warning("OCR requires saving bounding boxes. Setting save_bounding_boxes=True.")
            save_bounding_boxes = True

        # Set defaults from config if not provided
        output_dir = output_dir or OUTPUT_DIR
        iou_threshold = iou_threshold or IOU_THRESHOLD

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract filename without extension for output naming
        file_basename = Path(pdf_path).stem
                    
        # Process document all at once (original method)
        logger.info(f"Converting PDF to images: {pdf_path}")
        pages = pdf_to_images(pdf_path)
        
        # Process all pages
        logger.info("Processing all pages at once...")
        processed_pages = self._process_pages_improved(pages, iou_threshold)
        
        # Generate annotations if requested
        if generate_annotations: 
            
            logger.info("Generating annotated images...")
            annotations_dir = os.path.join(output_dir, "annotations")
            self._generate_annotations(pages, processed_pages, annotations_dir)
            
        # Save individual bounding boxes if requested
        if save_bounding_boxes: 
            
            logger.info("Saving individual bounding box images...")
            boxes_dir = os.path.join(output_dir, "boxes")
            self._save_bounding_boxes(processed_pages, boxes_dir)
        
        # Include document structure information
        structure_info = {}
        for page_num, page_content in processed_pages.items(): 

            page_structure = {}
            for label, element in page_content.items():

                page_structure[label] = {'coordinates': element['coordinates'],
                                         'class': get_box_class(label),
                                         'confidence': element['confidence']}
                
            structure_info[str(page_num)] = page_structure
                
        # Save results to file
        result_path = os.path.join(output_dir, "boxes.json")
        with open(result_path, 'w', encoding='utf-8') as f: 
            json.dump(structure_info, f, ensure_ascii = False, indent = 2)
            
        logger.info(f"Parsing complete. Base structure saved to {result_path}")

        # --- Hierarchy Step ---
        if self.hierarchy: 

            unclustered_content = {page:{k:None for k, v in boxes.items()} for page, boxes in structure_info.items()}

            # Flatten content, adding page notation to tag name 
            flattened_doc_texts = {}
            for page, page_content in unclustered_content.items(): 
                
                for tag, content in page_content.items(): 
                        
                        if (not content) or (content.strip() != ''):
                            
                            flattened_doc_texts[f"{page}_{tag}"] = content

            # Establish hierarchy by assigning heading to each chunk 
            heading = None
            chunks = {}
            order = 0
            for tag, text in flattened_doc_texts.items(): 

                page = tag.split('_')[0]

                if 'title' in tag: 

                    chunks[tag] = {'heading':heading, 'page':page, 'order':order}
                    heading = tag

                else: 

                    chunks[tag] = {'heading':heading, 'page':page, 'order':order}
                
                order += 1

            # Save hierarchy to file
            hierarchy_path = os.path.join(output_dir, "hierarchy.json")
            with open(hierarchy_path, 'w', encoding='utf-8') as f:
                json.dump(chunks, f)
            
            logger.info(f"Hierarchy saved to {hierarchy_path}")
        
        # --- OCR Step ---
        sorted_doc_texts = None
        if self.ocr: 

            logger.info(f"Starting OCR process using {'Tesseract' if use_tesseract else 'Azure'}...")
            
            try:
                
                sorted_doc_texts = self._run_ocr(output_dir, file_basename, result_path, use_tesseract)
                ocr_path = os.path.join(output_dir, "text.json")
                with open(ocr_path, 'w', encoding = 'utf-8') as f: 
                    json.dump(sorted_doc_texts, f, ensure_ascii = False, indent = 2)
                        
                logger.info("OCR processing finished successfully.")
            
            except Exception as e: 

                logger.error(f"OCR processing failed: {e}", exc_info=self.debug_mode)

        # --- Embedding Step ---
        embeddings_results = None
        if self.embed and sorted_doc_texts:
            logger.info("Starting embedding generation...")
            try:
                embeddings_results = self._generate_embeddings(sorted_doc_texts)
                embedding_path = os.path.join(output_dir, "embeddings.json")
                with open(embedding_path, 'w', encoding='utf-8') as f:
                    json.dump(embeddings_results, f, ensure_ascii=False, indent=2)
                logger.info(f"Embedding generation successful. Saved to {embedding_path}")
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}", exc_info=self.debug_mode)
        elif self.embed:
            logger.warning("Embedding was enabled, but no text was extracted. Skipping embedding step.")
            
         # --- Table Classification Step ---
        table_classification_results = None
        if self.classify_tables and sorted_doc_texts:
            logger.info("Starting table classification...")
            try:
                table_classification_results, tables_were_found = self._classify_tables(sorted_doc_texts, structure_info)
                
                if table_classification_results:
                    # Optionally save to a file
                    table_class_path = os.path.join(output_dir, "tables.json")
                    with open(table_class_path, 'w', encoding='utf-8') as f:
                        json.dump(table_classification_results, f, ensure_ascii=False, indent=2)
                    logger.info(f"Table classification successful. Saved to {table_class_path}")
                elif tables_were_found:
                    logger.warning("Table classification was attempted, but it failed for all tables. Please check the logs for errors.")

            except Exception as e:
                logger.error(f"Table classification failed with an unexpected error: {e}", exc_info=self.debug_mode)
        elif self.classify_tables:
            logger.warning("Table classification was enabled, but no text was extracted. Skipping classification step.")
        
        # Clean up to free memory
       
        self._cleanup_images(pages)
        self._cleanup_images(processed_pages)

        gc.collect()
        if torch.cuda.is_available(): 

            torch.cuda.empty_cache()
    
        result = {
            'structure': structure_info,
            'text': sorted_doc_texts,
            'hierarchy': chunks if self.hierarchy else None,
            'embeddings': embeddings_results,
            'tables': table_classification_results
        }
              
        return result

    def _classify_tables(self, sorted_doc_texts, structure_info):

        """
        Classifies tables from the processed pages using their OCR'd text.
        """
        if not self.azure_openai_endpoint or not self.azure_openai_api_key:
            raise ValueError("The 'azure_openai_endpoint' and 'azure_openai_api_key' must be provided for table classification.")

        # if not self.openai_client:
        #     self.openai_client = get_openai_client(api_key=self.openai_api_key,
        #                                            azure_api_key=self.azure_openai_api_key,
        #                                            api_version=self.azure_openai_api_version,
        #                                            azure_endpoint=self.azure_openai_endpoint)

        headers = {"Content-Type": "application/json", "api-key": self.azure_openai_api_key}
        
        if not self.azure_openai_api_key:
            raise ValueError("Azure OpenAI API key is required for table classification.")

        table_classifications = {}
        found_tables = False

        for page_num, page_content in sorted_doc_texts.items():
            for label, text in page_content.items():
                if page_num in structure_info and label in structure_info[page_num]:
                    element_class = structure_info[page_num][label].get('class')
                    if element_class == 'table' and text and not text.isspace():
                        found_tables = True
                        try:
                            USER_PROMPT = f"""[TABLE_TEXT]\n{text}"""
                            payload = {
                                "messages": [{"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]}, {"role": "user", "content": [{"type": "text", "text": USER_PROMPT}]}],
                                "temperature": 0.7
                            }
                            
                            response = requests.post(self.azure_openai_endpoint, headers = headers, json = payload)
                            response.raise_for_status()
                            response_json = response.json()
                            output = response_json['choices'][0]['message']['content'].strip()

                            try:
                                output_json = json.loads(output)
                            except Exception:
                                output_json = {
                                    "price_change_type": "",
                                    "misc_type": "",
                                    "product_type": "other"
                                }
                            
                            table_id = f"{page_num}_{label}"
                            table_classifications[table_id] = output_json
                        except requests.exceptions.RequestException as e:
                            error_content = ""
                            if e.response is not None:
                                error_content = f" Status Code: {e.response.status_code}, Response: {e.response.text}"
                            logger.error(f"HTTP request failed for table {label} on page {page_num}: {e}{error_content}", exc_info=self.debug_mode)
                        except (KeyError, IndexError) as e:
                            logger.error(f"Failed to parse API response for table {label} on page {page_num}. Response: {response.text}", exc_info=self.debug_mode)
                        except Exception as e:
                            logger.error(f"An unexpected error occurred during classification for table {label} on page {page_num}: {e}", exc_info=self.debug_mode)
        
        if not found_tables:
            logger.warning("No tables were identified in the document, so no classification was performed.")

        return table_classifications, found_tables

    def _generate_embeddings(self, sorted_doc_texts): 
        
        """
        Generates embeddings for the given text blocks using a batch approach.
        """
        
        if not self.openai_client: 

            self.openai_client = get_openai_client(api_key = self.openai_api_key,
                                                   azure_api_key = self.azure_openai_api_key,
                                                   api_version = self.azure_openai_api_version,
                                                   azure_endpoint = self.azure_openai_endpoint)

        texts_to_embed = []
        text_keys = []
        for page_num, page_content in sorted_doc_texts.items(): 

            for element_id, text in page_content.items(): 

                if text and not text.isspace(): 

                    texts_to_embed.append(text.replace("\n", " "))
                    text_keys.append((page_num, element_id))
        
        embedding_vectors = []
        if texts_to_embed: 
            logger.info(f"Generating embeddings for {len(texts_to_embed)} text block(s) using model '{self.embedding_model}'.")
            try: 

                response = self.openai_client.embeddings.create(input = texts_to_embed, model = self.embedding_model)
                embedding_vectors = [item.embedding for item in response.data]

            except Exception as e:
                
                logger.error(f"OpenAI API call for embeddings failed: {e}", exc_info = self.debug_mode)

                # Re-raise the exception to be caught by the main parse_document method
                raise

        embeddings_map = {key: vec for key, vec in zip(text_keys, embedding_vectors)}

        # Reconstruct the results dictionary, preserving the original structure
        final_embeddings = {}
        for page_num, page_content in sorted_doc_texts.items(): 

            final_embeddings[page_num] = {}
            for element_id, text in page_content.items(): 
            
                key = (page_num, element_id)
                final_embeddings[page_num][element_id] = embeddings_map.get(key)
        
        return final_embeddings
    
    def _ocr_with_tesseract(self, image_path):
        
        """
        Process a single bounding box image using Tesseract.

        Args:
            image_path (str): Path to the local image file.

        Returns:
            str: Extracted text content, or an empty string if OCR fails.
        """

        text = ""
        original_cmd = None
        try:

            # Load the image using Pillow
            img = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(img, lang='eng') # Specify language if needed
            text = text.strip()

            if self.debug_mode:
                logger.debug(f"Tesseract OCR successful for: {os.path.basename(image_path)}")

        except FileNotFoundError:
             
             logger.error(f"Image file not found for Tesseract OCR: {image_path}")
        except pytesseract.TesseractNotFoundError:
            
            logger.error(
                "Tesseract is not installed or not in your PATH. "
                "Please install Tesseract OCR engine"
            )
            # Re-raise or return empty string depending on desired behavior
            
            raise # Or return ""
       
        except Exception as e:
            logger.error(f"Error during Tesseract OCR for {os.path.basename(image_path)}: {e}", exc_info=self.debug_mode)
       

        return text
    
    def _get_pdf_page_count(self, pdf_path):
        
        """Get the number of pages in a PDF file."""
        
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        
        return page_count
    
    def _process_single_page(self, pages, page_num, iou_threshold): 
        
        """
        Process a single page of the document.
        
        Args:
            pages (dict): Dictionary containing a single page image.
            page_num (int): Page number being processed.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """
        # Parse document structure with YOLO
        parsed_page = self._parse_document_structure(pages)
        
        # Process parsed page with improved algorithm
        if page_num in parsed_page:
            processed_page = self._process_page_improved(pages, parsed_page[page_num], page_num, iou_threshold)
            return processed_page
        
        return {}
    
    def _cleanup_images(self, data): 

        """
        Remove image data from the processed results to free memory.
        
        Args:
            data: Data structure containing images to clean up.
            
        Returns:
            The same data structure with images removed.
        """

        if isinstance(data, dict):

            for key, value in list(data.items()):

                if key == 'image' and isinstance(value, Image.Image):
                    data[key] = None  # Remove the image

                elif isinstance(value, dict):
                    self._cleanup_images(value)

                elif isinstance(value, list):

                    for item in value:

                        if isinstance(item, dict):

                            self._cleanup_images(item)
        return data
    
    def _save_bounding_boxes_for_page(self, page_content, page_dir): 

        """
        Save individual bounding box images for a single page.
        
        Args:
            page_content (dict): Dictionary of page elements.
            page_dir (str): Directory to save bounding box images.
        """

        for label, element in page_content.items():

            if 'image' in element:

                # Create a safe filename from the label
                safe_label = label.replace('/', '_').replace('\\', '_')
                image_path = os.path.join(page_dir, f"{safe_label}.png")
                
                # Save the bounding box image
                element['image'].save(image_path)
                
                # Save coordinates as JSON
                coords_path = os.path.join(page_dir, f"{safe_label}_coords.json")
                with open(coords_path, 'w') as f:
                    json.dump({
                        'label': label,
                        'class': get_box_class(label),
                        'coordinates': element['coordinates']
                    }, f, indent=2)
    
    def _parse_document_structure(self, pages): 
        
        """
        Parse document structure using YOLO.
        
        Args:
            pages (dict): Dictionary of page images.
            
        Returns:
            dict: Dictionary of parsed page elements.
        """

        all_detections = {}
        
        for page_num, page in pages.items():
            
            # Clear PyTorch cache before processing each page
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            # Save page temporarily
            page.save('temp_page.jpg')
            
            # Run detection
            det_res = self.yolo_model.predict('temp_page.jpg',
                                               imgsz=1024, 
                                               conf=0.01,  # Using lower confidence threshold
                                               device="cuda:0" if torch.cuda.is_available() else "cpu")
            
            # Remove temporary file
            os.remove('temp_page.jpg')
            
            # Process detection results
            page_detections = {}
            for result in det_res: 

                # Convert the original image array to a PIL Image
                orig_img_array = result.orig_img
                orig_img = Image.fromarray(orig_img_array)
                
                # Get class names
                names = result.names  # Dictionary mapping class indices to class names
                
                # Get the boxes object
                boxes = result.boxes  # Boxes object
                
                # Access bounding box data
                boxes_data = boxes.xyxy  # Torch tensor with shape [num_boxes, 4]

                # Convert boxes data to a NumPy array
                # if isinstance(boxes_data, torch.Tensor):
                boxes_array = boxes_data.cpu().numpy()
                
                # Iterate over each detected box
                num_boxes = boxes_array.shape[0]
                for i in range(num_boxes):

                    box = boxes_array[i]
                    x1, y1, x2, y2 = box[:4]

                    # Get boxes.conf and boxes.cls
                    confidence = float(boxes.conf[i]) 
                    cls = int(boxes.cls[i])
                    
                    # Get class name
                    class_name = names.get(cls, 'Unknown') if cls is not None else 'Unknown'
                    
                    # Format coordinates 
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w = x2 - x1
                    h = y2 - y1
                    
                    # Crop the image using the bounding box coordinates
                    cropped_img = orig_img.crop((x1, y1, x2, y2))
                    
                    numbered_class_name = f'{class_name.replace(" ", "_")}_{i}'
                    
                    # Append the detection details to the dictionary
                    page_detections[numbered_class_name] = {'coordinates': [x1, y1, w, h], 
                                                            'image': cropped_img,
                                                            'confidence': confidence}
            
            # Sort detections by vertical position
            sorted_page_detections = dict(sorted((item for item in page_detections.items()), key = lambda item: item[1]['coordinates'][1]))
            
            all_detections[page_num] = sorted_page_detections
            
            # Clear PyTorch cache after processing
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return all_detections
    
    def _process_page_improved(self, pages, page_content, page_num, iou_threshold): 
        
        """
        Process a single page using the improved algorithm.
        
        Args:
            pages (dict): Dictionary of page images.
            page_content (dict): Dictionary of page elements.
            page_num (int): Page number being processed.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """

        logger.info(f"Processing page {page_num} with {len(page_content)} elements")
        
        # STEP 1: Perform class-specific NMS to merge overlapping boxes of the same class
        logger.info("Step 1: Performing class-specific NMS")
        merged_boxes = nms_merge_boxes(page_content, iou_threshold, class_specific = True)
        
        # STEP 2: Remove container boxes that contain multiple other boxes
        logger.info(f"Step 2: Removing container boxes (threshold: {self.container_threshold})")
        no_container_boxes = remove_container_boxes(merged_boxes, min_contained_boxes=self.container_threshold)
        
        # STEP 3: Remove boxes that are completely inside other boxes, with improved handling
        logger.info("Step 3: Removing inner boxes with improved handling")
        filtered_boxes = remove_inner_boxes(no_container_boxes, containment_threshold=0.95, safe_classes=TEXT_LABELS)
        
        # STEP 4: Attempt to recover boxes that might have been incorrectly removed
        logger.info("Step 4: Recovering potentially missed boxes")
        recovered_boxes = recover_missed_boxes(merged_boxes, filtered_boxes, pages[page_num])
        
        # STEP 5: Sort boxes by position
        logger.info("Step 5: Sorting boxes by position")
        sorted_boxes = sort_bounding_boxes(recovered_boxes)

        # STEP 6: Deduplicate boxes
        logger.info("Step 6: Deduplicating boxes")
        deduplicated_boxes = deduplicate_boxes(sorted_boxes)

        # STEP 7: Remove contained boxes
        logger.info("Step 7: Removing contained boxes")
        final_boxes = remove_contained_bounding_boxes(deduplicated_boxes)
        
        logger.info(f"Finished processing page {page_num}: {len(final_boxes)} elements")
        
        # Garbage collection
        gc.collect()
        
        return final_boxes
    
    def _process_pages_improved(self, pages, iou_threshold) : 
        
        """
        Process all pages using the improved algorithm.
        
        Args:
            pages (dict): Dictionary of page images.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """
        
        processed_pages = {}
        for page_num, page_content in self._parse_document_structure(pages).items():
            
            processed_pages[page_num] = self._process_page_improved(pages, page_content, page_num, iou_threshold)
            
            # Clean up after each page to save memory
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return processed_pages
    
    def _save_debug_image(self, original_image, boxes, output_path): 
        """
        Save a debug image with bounding boxes for troubleshooting.
        
        Args:
            original_image (PIL.Image): The original image.
            boxes (dict): Dictionary of bounding boxes.
            output_path (str): Path to save the debug image.
        """
        annotated = annotate_image(boxes, original_image)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        annotated.save(output_path)
        logger.debug(f"Saved debug image to {output_path}")
    
    def _generate_annotations(self, pages, processed_pages, output_dir): 

        """
        Generate annotated images showing detected elements.
        
        Args:
            pages (dict): Dictionary of page images.
            processed_pages (dict): Dictionary of processed page elements.
            output_dir (str): Directory to save annotated images.
        """

        os.makedirs(output_dir, exist_ok=True)
        
        for page_num, page_content in processed_pages.items():
            if page_num in pages:
                annotated_image = annotate_image(page_content, pages[page_num])
                save_annotated_image(annotated_image, output_dir, page_num)
                
                # Clean up to free memory
                annotated_image = None
                gc.collect()
                
    def _save_bounding_boxes(self, processed_pages, output_dir): 
        """
        Save individual bounding box images.
        
        Args:
            processed_pages (dict): Dictionary of processed page elements.
            output_dir (str): Directory to save bounding box images.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for page_num, page_content in processed_pages.items():
            page_dir = os.path.join(output_dir, f"page_{page_num}")
            os.makedirs(page_dir, exist_ok=True)
            
            self._save_bounding_boxes_for_page(page_content, page_dir)
            
            # Garbage collection after each page
            gc.collect()

    def _ocr_with_azure(self, image_path): 

        """
        Process a single bounding box image using Azure Document Intelligence,
        handling potential small image sizes by padding.

        Args:
            image_path (str): Path to the local image file (e.g., PNG).

        Returns:
            str: Extracted text content, or an empty string if OCR fails.
        """
        
        if not self.document_client:
            logger.error("OCR client not initialized. Cannot process image.")
            return ""

        temp_path = None
        process_path = image_path
        text = ""

        try:
            # Check image dimensions and pad if necessary
            with Image.open(image_path) as img:
                
                width, height = img.size
                needs_padding = width < 50 or height < 50

                if needs_padding:
                    
                    new_width = max(width, 50)
                    new_height = max(height, 50)
                    padded_img = Image.new('RGB', (new_width, new_height), color='white')
                   
                    # Convert to RGB if necessary before pasting
                    if img.mode != 'RGB':
                   
                        img = img.convert('RGB')
                  
                    padded_img.paste(img, (0, 0))

                    # Use NamedTemporaryFile to handle cleanup automatically
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                     
                        temp_path = temp_file.name
                        padded_img.save(temp_path, format='JPEG')
                   
                    process_path = temp_path
                    if self.debug_mode:
                    
                         logger.debug(f"Padded image {os.path.basename(image_path)} to {new_width}x{new_height}, saved to temp file: {temp_path}")


            # Process the image (original or padded)
            try:
                with open(process_path, "rb") as image_file:
                  
                    # Use the 'prebuilt-read' model for OCR
                    poller = self.document_client.begin_analyze_document("prebuilt-read", image_file.read())
                    result = poller.result() # Wait for the result

                    # Safely access content, default to empty string if not found
                    text = result.content if result and hasattr(result, 'content') else ""

                    if self.debug_mode and not text:
                        logger.debug(f"OCR returned no content for image: {os.path.basename(image_path)}")
                  
                    elif self.debug_mode:
                         logger.debug(f"OCR successful for: {os.path.basename(image_path)}")


            except ServiceRequestError as e:
                logger.error(f"Azure service error during OCR for {os.path.basename(image_path)}: {e}")
         
            except Exception as e:
                 logger.error(f"Error during OCR processing for {os.path.basename(image_path)}: {e}", exc_info=self.debug_mode)


        except FileNotFoundError:
             logger.error(f"Image file not found for OCR: {image_path}")
    
        except Exception as e:
            logger.error(f"Error opening or padding image {image_path}: {e}", exc_info=self.debug_mode)
    
        finally:
    
            # Clean up temporary file if created
            if temp_path and os.path.exists(temp_path):
        
                try:
        
                    os.unlink(temp_path)
                    if self.debug_mode:
                        logger.debug(f"Cleaned up temporary OCR file: {temp_path}")
        
                except Exception as e:
                     logger.warning(f"Could not remove temporary OCR file {temp_path}: {e}")

        return text

    def _run_ocr(self, output_dir, doc_name, structure_json_path, use_tesseract = False): 

        """
        Run OCR on all saved bounding box images for the document,
        sort the text based on the structure JSON, and save the results.

        Args:
            output_dir (str): The main output directory for the document.
            doc_name (str): The base name of the document file (without extension).
            structure_json_path (str): Path to the _parsed.json file containing structure info.
            use_tesseract (bool): If True, use Tesseract; otherwise use Azure.
        """

        output_doc_boxes_dir = os.path.join(output_dir, "boxes")
        if not os.path.isdir(output_doc_boxes_dir):
            
            logger.error(f"Bounding box directory not found for OCR: {output_doc_boxes_dir}")
            return

        doc_texts = {} # Structure: {page_num_str: {box_id: text}}

        # Iterate through page directories (e.g., page_0, page_1)
        page_dirs = sorted([d for d in os.listdir(output_doc_boxes_dir) if os.path.isdir(os.path.join(output_doc_boxes_dir, d)) and d.startswith("page_")],
                           key=lambda x: int(x.split('_')[-1])) # Sort numerically

        for page_dir_name in page_dirs:
            
            page_num_str = page_dir_name.split('_')[-1]
            page_path = os.path.join(output_doc_boxes_dir, page_dir_name)
            logger.info(f"Processing OCR for page {page_num_str}...")

            texts = {} # Structure: {box_id: text}
            box_files = [f for f in os.listdir(page_path) if f.lower().endswith(".png")] # Assume boxes are PNG

            for box_file in box_files:
           
                image_path = os.path.join(page_path, box_file)
           
                # Box ID is the filename without extension
                box_id = os.path.splitext(box_file)[0]
                try:
                                        
                    if use_tesseract:
                        text = self._ocr_with_tesseract(image_path)
                    
                    else:
                        text = self._ocr_with_azure(image_path)
                    
                    texts[box_id] = text
           
                except Exception as e:

                    logger.error(f"Failed OCR for box {box_id} on page {page_num_str}: {e}", exc_info=self.debug_mode)
                    texts[box_id] = "" # Store empty string on error

            doc_texts[page_num_str] = texts
            logger.info(f"Finished OCR for page {page_num_str}.")


        # Load the structure JSON to get the correct order
        try:

            with open(structure_json_path, "r", encoding='utf-8') as f: 
                
                structure = json.load(f)
           
        except FileNotFoundError: 

            logger.error(f"Structure JSON file not found: {structure_json_path}")
            return
      
        except json.JSONDecodeError: 
            
             logger.error(f"Error decoding structure JSON file: {structure_json_path}")
             return
       
        except Exception as e: 
            
             logger.error(f"Error loading structure JSON {structure_json_path}: {e}", exc_info=self.debug_mode)
             return


        # Create the sorted text dictionary based on structure order
        sorted_doc_texts = {} # {page_num_str: {box_id: text}}
        for page_num_str, page_content in structure.items(): 
      
            if page_num_str in doc_texts: 
     
                sorted_page_texts = {}
                for box_id in page_content.keys(): # Iterate in the order defined by structure JSON
      
                    if box_id in doc_texts[page_num_str]: 
                        sorted_page_texts[box_id] = doc_texts[page_num_str][box_id]
      
                    else: 

                        # Box ID exists in structure but not in OCR results (maybe OCR failed?)
                        logger.warning(f"Box ID '{box_id}' from structure JSON not found in OCR results for page {page_num_str}. Storing empty text.")
                        sorted_page_texts[box_id] = ""
         
                sorted_doc_texts[page_num_str] = sorted_page_texts
        
            else: 
                 
                 # Page exists in structure but not in OCR results (maybe no boxes saved?)
                 logger.warning(f"Page {page_num_str} from structure JSON not found in OCR results. Skipping.")

        return sorted_doc_texts

    # --- End OCR Methods ---