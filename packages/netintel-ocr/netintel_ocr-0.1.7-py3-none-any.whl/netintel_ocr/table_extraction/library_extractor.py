"""
Table extraction using PDF libraries (pdfplumber, tabula-py).
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LibraryTableExtractor:
    """Extract tables using PDF processing libraries."""
    
    def __init__(self, method: str = 'pdfplumber'):
        """
        Initialize the library-based extractor.
        
        Args:
            method: Extraction method ('pdfplumber' or 'tabula')
        """
        self.method = method
        self._init_extractor()
    
    def _init_extractor(self):
        """Initialize the selected extraction library."""
        if self.method == 'pdfplumber':
            try:
                import pdfplumber
                self.pdfplumber = pdfplumber
                logger.info("Initialized pdfplumber for table extraction")
            except ImportError:
                logger.warning("pdfplumber not available, falling back to LLM extraction")
                self.pdfplumber = None
        elif self.method == 'tabula':
            try:
                import tabula
                self.tabula = tabula
                logger.info("Initialized tabula-py for table extraction")
            except ImportError:
                logger.warning("tabula-py not available, falling back to pdfplumber")
                self.tabula = None
                self.method = 'pdfplumber'
                self._init_extractor()
    
    def extract_from_pdf(self, pdf_path: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract tables directly from PDF without image conversion.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number (0-indexed)
            
        Returns:
            List of extracted tables with metadata
        """
        if self.method == 'pdfplumber' and self.pdfplumber:
            return self._extract_with_pdfplumber(pdf_path, page_num)
        elif self.method == 'tabula' and self.tabula:
            return self._extract_with_tabula(pdf_path, page_num)
        else:
            logger.warning(f"No library available for method {self.method}")
            return []
    
    def _extract_with_pdfplumber(self, pdf_path: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber."""
        tables = []
        
        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    logger.warning(f"Page {page_num} out of range")
                    return []
                
                page = pdf.pages[page_num]
                extracted_tables = page.extract_tables()
                
                for idx, table_data in enumerate(extracted_tables):
                    if not table_data or len(table_data) < 2:
                        continue
                    
                    # Process the table
                    processed = self._process_table(table_data)
                    if processed:
                        processed['extraction_method'] = 'pdfplumber'
                        processed['table_index'] = idx
                        tables.append(processed)
                
        except Exception as e:
            logger.error(f"Error extracting with pdfplumber: {e}")
        
        return tables
    
    def _extract_with_tabula(self, pdf_path: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables using tabula-py."""
        tables = []
        
        try:
            # Tabula uses 1-indexed pages
            dfs = self.tabula.read_pdf(
                pdf_path,
                pages=page_num + 1,
                multiple_tables=True,
                pandas_options={'header': None}
            )
            
            for idx, df in enumerate(dfs):
                if df.empty:
                    continue
                
                # Convert DataFrame to list format
                table_data = [df.columns.tolist()] + df.values.tolist()
                
                processed = self._process_table(table_data)
                if processed:
                    processed['extraction_method'] = 'tabula'
                    processed['table_index'] = idx
                    tables.append(processed)
                    
        except Exception as e:
            logger.error(f"Error extracting with tabula: {e}")
        
        return tables
    
    def _process_table(self, table_data: List[List]) -> Optional[Dict[str, Any]]:
        """
        Process raw table data into structured format.
        
        Args:
            table_data: Raw table as list of lists
            
        Returns:
            Processed table dictionary or None if invalid
        """
        if not table_data or len(table_data) < 2:
            return None
        
        # Clean the data
        cleaned_data = []
        for row in table_data:
            if row and any(cell for cell in row if cell):
                # Clean cells
                cleaned_row = [
                    str(cell).strip() if cell is not None else ""
                    for cell in row
                ]
                cleaned_data.append(cleaned_row)
        
        if len(cleaned_data) < 2:
            return None
        
        # Assume first row is headers
        headers = cleaned_data[0]
        data_rows = cleaned_data[1:]
        
        # Convert to structured format
        structured_data = []
        for row in data_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    value = row[i]
                    # Try to convert to appropriate type
                    row_dict[header] = self._convert_value(value)
                else:
                    row_dict[header] = None
            structured_data.append(row_dict)
        
        # Determine table type
        table_type = self._classify_table(cleaned_data)
        
        return {
            'type': table_type,
            'headers': headers,
            'data': structured_data,
            'metadata': {
                'rows': len(data_rows),
                'columns': len(headers),
                'has_headers': True,
                'confidence': 0.8  # Library extraction typically has good confidence
            }
        }
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value (int, float, bool, or string)
        """
        if not value or value == "":
            return None
        
        # Remove common formatting
        clean_value = value.replace(',', '').replace('$', '').strip()
        
        # Try conversions
        try:
            # Check for boolean
            if clean_value.lower() in ['true', 'yes', 'y']:
                return True
            elif clean_value.lower() in ['false', 'no', 'n']:
                return False
            
            # Try integer
            if '.' not in clean_value:
                return int(clean_value)
            
            # Try float
            return float(clean_value)
            
        except ValueError:
            # Return as string if conversion fails
            return value
    
    def _classify_table(self, table_data: List[List]) -> str:
        """
        Classify the table type based on structure.
        
        Args:
            table_data: Cleaned table data
            
        Returns:
            Table type classification
        """
        if not table_data:
            return 'unknown'
        
        # Check for consistent column count
        col_counts = [len(row) for row in table_data]
        consistent_cols = len(set(col_counts)) == 1
        
        # Check for merged cells (inconsistent columns)
        if not consistent_cols:
            return 'complex'
        
        # Check for multi-row patterns
        # (e.g., repeated patterns in first column)
        if len(table_data) > 3:
            first_col = [row[0] if row else "" for row in table_data]
            if any(not val for val in first_col[1:]):
                return 'multi_row'
        
        return 'simple'
    
    def needs_enhancement(self, tables: List[Dict]) -> bool:
        """
        Determine if extracted tables need LLM enhancement.
        
        Args:
            tables: List of extracted tables
            
        Returns:
            True if enhancement is recommended
        """
        if not tables:
            return True
        
        for table in tables:
            # Check confidence
            confidence = table.get('metadata', {}).get('confidence', 0)
            if confidence < 0.7:
                return True
            
            # Check for complex structures
            if table.get('type') in ['complex', 'multi_row']:
                return True
            
            # Check for empty data
            if not table.get('data'):
                return True
        
        return False