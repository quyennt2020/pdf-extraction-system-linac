"""
PDF Processor specialized for medical device service manuals
"""

import os
import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import re
from datetime import datetime
import hashlib
import json


@dataclass
class PDFPage:
    """Represents a single PDF page with extracted content"""
    page_number: int
    text_content: str
    tables: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    annotations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    extraction_method: str = "hybrid"


@dataclass
class PDFDocument:
    """Represents entire PDF document with metadata"""
    filename: str
    file_path: str
    total_pages: int
    pages: List[PDFPage]
    document_metadata: Dict[str, Any]
    processing_timestamp: float
    file_hash: str


class MedicalDevicePDFProcessor:
    """
    Specialized PDF processor for medical device service manuals
    with optimized extraction for error codes, tables, and technical content
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize PDF processor"""
        
        self.config = config or self._get_default_config()
        
        # Medical device specific patterns
        self.medical_patterns = {
            "error_codes": [
                r'\b\d{4}\b',  # 4-digit error codes
                r'Error\s+Code\s*:?\s*\d{4}',
                r'Code\s+\d{4}'
            ],
            "software_versions": [
                r'R\d+\.\d+[x]*',
                r'Integrity™\s+R\d+\.\d+',
                r'Software\s+Release\s*:?\s*([^\n]+)'
            ],
            "components": [
                r'MLC[i]*\d*',
                r'leaf\s+motor',
                r'collimator',
                r'gantry',
                r'linear\s+accelerator'
            ],
            "safety_notices": [
                r'WARNING\s*:',
                r'CAUTION\s*:',
                r'DANGER\s*:',
                r'NOTE\s*:'
            ]
        }
        
        logger.info("Medical device PDF processor initialized")
    
    def process_pdf(self, file_path: str) -> PDFDocument:
        """
        Process PDF document with medical device specific extraction
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            PDFDocument with extracted content
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        logger.info(f"Processing medical device PDF: {file_path}")
        
        # Generate file hash for caching
        file_hash = self._generate_file_hash(file_path)
        
        # Check cache if enabled
        if self.config.get("enable_cache", False):
            cached_result = self._check_cache(file_hash)
            if cached_result:
                logger.info("Using cached PDF processing result")
                return cached_result
        
        # Extract document metadata
        doc_metadata = self._extract_document_metadata(file_path)
        
        # Process pages
        pages = []
        
        try:
            # Use PyMuPDF for primary extraction
            with fitz.open(file_path) as pdf_doc:
                total_pages = len(pdf_doc)
                
                logger.info(f"Processing {total_pages} pages")
                
                for page_num in range(total_pages):
                    page = self._process_page_fitz(pdf_doc, page_num)
                    
                    # Enhance with pdfplumber for better table extraction
                    page = self._enhance_page_with_pdfplumber(file_path, page_num, page)
                    
                    # Apply medical device specific processing
                    page = self._apply_medical_processing(page)
                    
                    pages.append(page)
                    
                    logger.info(f"Processed page {page_num + 1}/{total_pages}")
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
        
        # Create PDF document object
        pdf_document = PDFDocument(
            filename=os.path.basename(file_path),
            file_path=file_path,
            total_pages=total_pages,
            pages=pages,
            document_metadata=doc_metadata,
            processing_timestamp=datetime.now().timestamp(),
            file_hash=file_hash
        )
        
        # Cache result if enabled
        if self.config.get("enable_cache", False):
            self._cache_result(file_hash, pdf_document)
        
        logger.info(f"Successfully processed PDF: {total_pages} pages")
        
        return pdf_document
    
    def _process_page_fitz(self, pdf_doc: fitz.Document, page_num: int) -> PDFPage:
        """Process page using PyMuPDF (fitz)"""
        
        page = pdf_doc[page_num]
        
        # Extract text content
        text_content = page.get_text()
        
        # Extract tables (basic)
        tables = []
        try:
            table_data = page.find_tables()
            for table in table_data:
                table_dict = {
                    "bbox": table.bbox,
                    "data": table.extract(),
                    "extraction_method": "fitz"
                }
                tables.append(table_dict)
        except Exception as e:
            logger.warning(f"Error extracting tables from page {page_num + 1}: {str(e)}")
        
        # Extract images
        images = []
        try:
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                img_dict = {
                    "index": img_index,
                    "xref": img[0],
                    "bbox": page.get_image_bbox(img),
                    "extraction_method": "fitz"
                }
                images.append(img_dict)
        except Exception as e:
            logger.warning(f"Error extracting images from page {page_num + 1}: {str(e)}")
        
        # Extract annotations
        annotations = []
        try:
            annot_list = page.annots()
            for annot in annot_list:
                annot_dict = {
                    "type": annot.type[1],
                    "content": annot.info["content"],
                    "rect": list(annot.rect),
                    "extraction_method": "fitz"
                }
                annotations.append(annot_dict)
        except Exception as e:
            logger.warning(f"Error extracting annotations from page {page_num + 1}: {str(e)}")
        
        # Create page metadata
        metadata = {
            "rotation": page.rotation,
            "mediabox": list(page.mediabox),
            "cropbox": list(page.cropbox),
            "text_length": len(text_content),
            "table_count": len(tables),
            "image_count": len(images),
            "annotation_count": len(annotations)
        }
        
        return PDFPage(
            page_number=page_num + 1,
            text_content=text_content,
            tables=tables,
            images=images,
            annotations=annotations,
            metadata=metadata,
            extraction_method="fitz"
        )
    
    def _enhance_page_with_pdfplumber(self, file_path: str, page_num: int, page: PDFPage) -> PDFPage:
        """Enhance page extraction using pdfplumber for better table handling"""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_num < len(pdf.pages):
                    plumber_page = pdf.pages[page_num]
                    
                    # Enhanced table extraction
                    plumber_tables = plumber_page.extract_tables()
                    
                    if plumber_tables:
                        # Replace or enhance existing tables
                        enhanced_tables = []
                        
                        for i, table_data in enumerate(plumber_tables):
                            table_dict = {
                                "index": i,
                                "data": table_data,
                                "extraction_method": "pdfplumber",
                                "row_count": len(table_data) if table_data else 0,
                                "col_count": len(table_data[0]) if table_data and table_data[0] else 0
                            }
                            enhanced_tables.append(table_dict)
                        
                        # Merge with existing tables or replace
                        if enhanced_tables:
                            page.tables = enhanced_tables
                            page.metadata["enhanced_table_extraction"] = True
                            page.extraction_method = "hybrid"
                    
                    # Enhanced text extraction (if needed)
                    plumber_text = plumber_page.extract_text()
                    if plumber_text and len(plumber_text) > len(page.text_content):
                        page.text_content = plumber_text
                        page.metadata["enhanced_text_extraction"] = True
        
        except Exception as e:
            logger.warning(f"Error enhancing page {page_num + 1} with pdfplumber: {str(e)}")
        
        return page
    
    def _apply_medical_processing(self, page: PDFPage) -> PDFPage:
        """Apply medical device specific processing to page"""
        
        # Identify medical content types
        medical_content = {
            "error_codes": [],
            "software_versions": [],
            "components": [],
            "safety_notices": [],
            "table_types": []
        }
        
        # Pattern matching for medical content
        for content_type, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, page.text_content, re.IGNORECASE)
                medical_content[content_type].extend(matches)
        
        # Classify tables based on content
        for i, table in enumerate(page.tables):
            table_type = self._classify_medical_table(table)
            table["medical_classification"] = table_type
            medical_content["table_types"].append(table_type)
        
        # Add medical metadata to page
        page.metadata["medical_content"] = medical_content
        page.metadata["is_error_code_page"] = len(medical_content["error_codes"]) > 0
        page.metadata["is_table_heavy"] = len(page.tables) > 2
        page.metadata["safety_notice_count"] = len(medical_content["safety_notices"])
        
        return page
    
    def _classify_medical_table(self, table: Dict[str, Any]) -> str:
        """Classify table based on medical device context"""
        
        if not table.get("data"):
            return "unknown"
        
        # Convert table data to string for analysis
        table_text = ""
        for row in table["data"]:
            if row:
                table_text += " ".join([str(cell) for cell in row if cell]) + "\n"
        
        table_text = table_text.lower()
        
        # Classification logic
        if any(keyword in table_text for keyword in ["error", "code", "fault"]):
            return "error_code_table"
        elif any(keyword in table_text for keyword in ["software", "release", "version"]):
            return "software_version_table"
        elif any(keyword in table_text for keyword in ["component", "part", "specification"]):
            return "component_specification_table"
        elif any(keyword in table_text for keyword in ["procedure", "step", "maintenance"]):
            return "procedure_table"
        elif any(keyword in table_text for keyword in ["parameter", "value", "measurement"]):
            return "technical_specification_table"
        else:
            return "general_table"
    
    def _extract_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract document-level metadata"""
        
        metadata = {
            "filename": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "processing_timestamp": datetime.now().isoformat()
        }
        
        try:
            with fitz.open(file_path) as doc:
                pdf_metadata = doc.metadata
                
                metadata.update({
                    "title": pdf_metadata.get("title", ""),
                    "author": pdf_metadata.get("author", ""),
                    "subject": pdf_metadata.get("subject", ""),
                    "creator": pdf_metadata.get("creator", ""),
                    "producer": pdf_metadata.get("producer", ""),
                    "creation_date": pdf_metadata.get("creationDate", ""),
                    "modification_date": pdf_metadata.get("modDate", "")
                })
                
                # Detect document type based on metadata and content
                metadata["document_type"] = self._detect_document_type(pdf_metadata)
                
        except Exception as e:
            logger.warning(f"Error extracting document metadata: {str(e)}")
        
        return metadata
    
    def _detect_document_type(self, pdf_metadata: Dict[str, str]) -> str:
        """Detect if document is a medical device manual"""
        
        title = pdf_metadata.get("title", "").lower()
        subject = pdf_metadata.get("subject", "").lower()
        
        # Medical device indicators
        medical_indicators = [
            "service manual", "maintenance manual", "user manual",
            "mlci", "linear accelerator", "elekta", "varian",
            "medical device", "radiotherapy", "radiation therapy"
        ]
        
        for indicator in medical_indicators:
            if indicator in title or indicator in subject:
                return "medical_device_manual"
        
        return "technical_document"
    
    def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of file for caching"""
        
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
        
        except Exception as e:
            logger.error(f"Error generating file hash: {str(e)}")
            return ""
    
    def _check_cache(self, file_hash: str) -> Optional[PDFDocument]:
        """Check if processed result exists in cache"""
        
        cache_dir = self.config.get("cache_directory", "./cache")
        cache_file = os.path.join(cache_dir, f"{file_hash}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                
                # Reconstruct PDFDocument object
                # Note: This is simplified - in production you'd want proper deserialization
                return None  # For now, return None to force reprocessing
                
            except Exception as e:
                logger.warning(f"Error loading cached result: {str(e)}")
        
        return None
    
    def _cache_result(self, file_hash: str, pdf_document: PDFDocument):
        """Cache processed result"""
        
        cache_dir = self.config.get("cache_directory", "./cache")
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        cache_file = os.path.join(cache_dir, f"{file_hash}.json")
        
        try:
            # Convert PDFDocument to dictionary for caching
            # Note: This is simplified - in production you'd want proper serialization
            cached_data = {
                "filename": pdf_document.filename,
                "total_pages": pdf_document.total_pages,
                "processing_timestamp": pdf_document.processing_timestamp,
                "file_hash": pdf_document.file_hash
                # Add more fields as needed
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Error caching result: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for PDF processor"""
        
        return {
            "enable_cache": True,
            "cache_directory": "./data/temp/pdf_cache",
            "max_file_size": 200 * 1024 * 1024,  # 200MB
            "enable_ocr": False,  # OCR for scanned PDFs
            "table_extraction_method": "hybrid",  # fitz, pdfplumber, or hybrid
            "preserve_formatting": True,
            "extract_images": True,
            "extract_annotations": True,
            "timeout_per_page": 30  # seconds
        }
    
    def get_error_code_pages(self, pdf_document: PDFDocument) -> List[PDFPage]:
        """Get pages that contain error codes"""
        
        error_code_pages = []
        
        for page in pdf_document.pages:
            if page.metadata.get("is_error_code_page", False):
                error_code_pages.append(page)
        
        return error_code_pages
    
    def get_table_heavy_pages(self, pdf_document: PDFDocument) -> List[PDFPage]:
        """Get pages with multiple tables"""
        
        table_pages = []
        
        for page in pdf_document.pages:
            if page.metadata.get("is_table_heavy", False):
                table_pages.append(page)
        
        return table_pages
    
    def extract_all_tables(self, pdf_document: PDFDocument) -> List[Dict[str, Any]]:
        """Extract all tables from document with context"""
        
        all_tables = []
        
        for page in pdf_document.pages:
            for table in page.tables:
                table_with_context = {
                    "page_number": page.page_number,
                    "table_data": table,
                    "medical_classification": table.get("medical_classification", "unknown"),
                    "surrounding_text": page.text_content[:500]  # Context
                }
                all_tables.append(table_with_context)
        
        return all_tables
    
    def search_content(self, pdf_document: PDFDocument, pattern: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for specific patterns in document content"""
        
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for page in pdf_document.pages:
            matches = list(re.finditer(pattern, page.text_content, flags))
            
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(page.text_content), match.end() + 100)
                context = page.text_content[start:end]
                
                result = {
                    "page_number": page.page_number,
                    "match": match.group(0),
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "context": context,
                    "medical_content": page.metadata.get("medical_content", {})
                }
                
                results.append(result)
        
        return results
    
    def get_processing_summary(self, pdf_document: PDFDocument) -> Dict[str, Any]:
        """Get summary of PDF processing results"""
        
        total_error_codes = 0
        total_tables = 0
        total_images = 0
        total_safety_notices = 0
        
        table_types = {}
        
        for page in pdf_document.pages:
            medical_content = page.metadata.get("medical_content", {})
            
            total_error_codes += len(medical_content.get("error_codes", []))
            total_tables += len(page.tables)
            total_images += len(page.images)
            total_safety_notices += len(medical_content.get("safety_notices", []))
            
            # Count table types
            for table in page.tables:
                table_type = table.get("medical_classification", "unknown")
                table_types[table_type] = table_types.get(table_type, 0) + 1
        
        return {
            "document_info": {
                "filename": pdf_document.filename,
                "total_pages": pdf_document.total_pages,
                "file_hash": pdf_document.file_hash,
                "document_type": pdf_document.document_metadata.get("document_type", "unknown")
            },
            "content_summary": {
                "total_error_codes": total_error_codes,
                "total_tables": total_tables,
                "total_images": total_images,
                "total_safety_notices": total_safety_notices,
                "table_types": table_types
            },
            "processing_info": {
                "processing_timestamp": pdf_document.processing_timestamp,
                "extraction_methods_used": list(set([page.extraction_method for page in pdf_document.pages]))
            }
        }


# Utility functions

def validate_pdf_file(file_path: str) -> Dict[str, Any]:
    """Validate PDF file before processing"""
    
    validation_result = {
        "is_valid": False,
        "file_exists": False,
        "is_readable": False,
        "file_size": 0,
        "page_count": 0,
        "errors": []
    }
    
    try:
        # Check file existence
        if not os.path.exists(file_path):
            validation_result["errors"].append("File does not exist")
            return validation_result
        
        validation_result["file_exists"] = True
        validation_result["file_size"] = os.path.getsize(file_path)
        
        # Check if file is readable as PDF
        with fitz.open(file_path) as doc:
            validation_result["page_count"] = len(doc)
            validation_result["is_readable"] = True
        
        # Check file size limits (200MB default)
        if validation_result["file_size"] > 200 * 1024 * 1024:
            validation_result["errors"].append("File size exceeds 200MB limit")
        else:
            validation_result["is_valid"] = True
    
    except Exception as e:
        validation_result["errors"].append(f"PDF validation error: {str(e)}")
    
    return validation_result


if __name__ == "__main__":
    # Test the PDF processor
    
    processor = MedicalDevicePDFProcessor()
    
    # Example usage
    test_file = "data/medical_manuals/sample_manual.pdf"
    
    if os.path.exists(test_file):
        # Validate file first
        validation = validate_pdf_file(test_file)
        
        if validation["is_valid"]:
            print("✅ PDF file is valid")
            
            # Process PDF
            pdf_doc = processor.process_pdf(test_file)
            
            # Get processing summary
            summary = processor.get_processing_summary(pdf_doc)
            
            print(f"📄 Processed: {summary['document_info']['filename']}")
            print(f"📊 Pages: {summary['document_info']['total_pages']}")
            print(f"🔢 Error codes found: {summary['content_summary']['total_error_codes']}")
            print(f"📋 Tables found: {summary['content_summary']['total_tables']}")
            
        else:
            print("❌ PDF file validation failed:")
            for error in validation["errors"]:
                print(f"  - {error}")
    else:
        print(f"⚠️ Test file not found: {test_file}")
        print("Place a medical device PDF in the data/medical_manuals/ directory to test")
