"""
Table detection module for identifying tables in PDF pages.
"""

import json
import logging
from typing import Dict, Optional, Any
from ..ollama import transcribe_image
from ..timeout_utils import retry_with_timeout
from .prompts import TABLE_DETECTION_PROMPT

logger = logging.getLogger(__name__)


class TableDetector:
    """Detects tables in PDF pages using vision models."""
    
    def __init__(self, model: str, confidence_threshold: float = 0.7):
        """
        Initialize the table detector.
        
        Args:
            model: The vision model to use for detection
            confidence_threshold: Minimum confidence to consider a table detected
        """
        self.model = model
        self.confidence_threshold = confidence_threshold
    
    def detect(self, image_path: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Detect tables in the given image.
        
        Args:
            image_path: Path to the image file
            timeout: Timeout in seconds for detection
            
        Returns:
            Dictionary containing detection results
        """
        try:
            # Use retry wrapper with timeout
            detect_with_timeout = retry_with_timeout(timeout_seconds=timeout)
            result = detect_with_timeout(self._detect_tables)(image_path)
            return result
        except Exception as e:
            logger.warning(f"Table detection failed: {e}")
            return {
                'has_tables': False,
                'confidence': 0.0,
                'table_count': 0,
                'table_types': [],
                'error': str(e)
            }
    
    def _detect_tables(self, image_path: str) -> Dict[str, Any]:
        """Internal method to detect tables using LLM."""
        try:
            # Call LLM with detection prompt
            response = transcribe_image(image_path, self.model, TABLE_DETECTION_PROMPT)
            
            # Parse response
            if isinstance(response, str):
                # Try to extract JSON from response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '{' in response and '}' in response:
                    # Find JSON object in response
                    start = response.index('{')
                    end = response.rindex('}') + 1
                    json_str = response[start:end]
                else:
                    # Fallback: assume no tables
                    return {
                        'has_tables': False,
                        'confidence': 0.0,
                        'table_count': 0,
                        'table_types': []
                    }
                
                result = json.loads(json_str)
            else:
                result = response
            
            # Ensure required fields
            has_tables = result.get('has_tables', False)
            confidence = result.get('confidence', 0.0)
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                has_tables = False
            
            return {
                'has_tables': has_tables,
                'confidence': confidence,
                'table_count': result.get('table_count', 0),
                'table_types': result.get('table_types', []),
                'table_regions': result.get('table_regions', [])
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse table detection response: {e}")
            return {
                'has_tables': False,
                'confidence': 0.0,
                'table_count': 0,
                'table_types': []
            }
        except Exception as e:
            logger.error(f"Table detection error: {e}")
            raise
    
    def classify_table_type(self, table_structure: Dict) -> str:
        """
        Classify the type of table based on its structure.
        
        Args:
            table_structure: Dictionary describing table structure
            
        Returns:
            Table type: 'simple', 'complex', or 'multi_row'
        """
        # Check for merged cells
        has_merged = table_structure.get('has_merged_cells', False)
        
        # Check for multi-level headers
        header_levels = table_structure.get('header_levels', 1)
        
        # Check for multi-row fields
        has_multi_row = table_structure.get('has_multi_row_fields', False)
        
        if has_multi_row:
            return 'multi_row'
        elif has_merged or header_levels > 1:
            return 'complex'
        else:
            return 'simple'