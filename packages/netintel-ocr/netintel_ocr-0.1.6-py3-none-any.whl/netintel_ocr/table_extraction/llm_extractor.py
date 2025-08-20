"""
Table extraction using vision language models.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from ..ollama import transcribe_image
from ..timeout_utils import retry_with_timeout
from .prompts import get_prompt_for_table_type

logger = logging.getLogger(__name__)


class LLMTableExtractor:
    """Extract tables using vision language models."""
    
    def __init__(self, model: str):
        """
        Initialize the LLM-based extractor.
        
        Args:
            model: The vision model to use for extraction
        """
        self.model = model
    
    def extract_from_image(
        self, 
        image_path: str, 
        table_type: str = 'simple',
        fast_mode: bool = False,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Extract table using appropriate prompt for table type.
        
        Args:
            image_path: Path to the image containing the table
            table_type: Type of table to extract
            fast_mode: Use fast extraction mode
            timeout: Timeout in seconds
            
        Returns:
            Extracted table data
        """
        try:
            # Get appropriate prompt
            prompt = get_prompt_for_table_type(table_type, fast_mode)
            
            # Use retry wrapper with timeout
            extract_with_timeout = retry_with_timeout(timeout_seconds=timeout)
            result = extract_with_timeout(self._extract_table)(
                image_path, prompt, table_type, fast_mode
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM table extraction failed: {e}")
            return {
                'type': table_type,
                'error': str(e),
                'extraction_method': 'llm_failed',
                'data': []
            }
    
    def _extract_table(
        self, 
        image_path: str, 
        prompt: str, 
        table_type: str,
        fast_mode: bool
    ) -> Dict[str, Any]:
        """Internal method to extract table using LLM."""
        try:
            # Call LLM with extraction prompt
            response = transcribe_image(image_path, self.model, prompt)
            
            # Parse response based on mode
            if fast_mode:
                return self._parse_fast_response(response, table_type)
            else:
                return self._parse_json_response(response, table_type)
                
        except Exception as e:
            logger.error(f"Table extraction error: {e}")
            raise
    
    def _parse_json_response(self, response: str, table_type: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Extract JSON from response
            if isinstance(response, dict):
                data = response
            else:
                # Try to find JSON in string response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '{' in response and '}' in response:
                    start = response.index('{')
                    end = response.rindex('}') + 1
                    json_str = response[start:end]
                else:
                    raise ValueError("No JSON found in response")
                
                data = json.loads(json_str)
            
            # Structure the result based on table type
            if table_type == 'simple':
                return self._structure_simple_table(data)
            elif table_type == 'complex':
                return self._structure_complex_table(data)
            elif table_type == 'multi_row':
                return self._structure_multi_row_table(data)
            else:
                return {
                    'type': table_type,
                    'data': data,
                    'extraction_method': 'llm'
                }
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return {
                'type': table_type,
                'error': 'parse_error',
                'raw_response': response[:500],
                'extraction_method': 'llm_failed'
            }
    
    def _parse_fast_response(self, response: str, table_type: str) -> Dict[str, Any]:
        """Parse fast mode pipe-delimited response."""
        try:
            lines = response.strip().split('\n')
            if len(lines) < 2:
                raise ValueError("Insufficient data in fast response")
            
            # First line should be headers
            headers = [h.strip() for h in lines[0].split('|')]
            
            # Parse data rows
            data = []
            for line in lines[1:]:
                if '|' in line:
                    values = [v.strip() for v in line.split('|')]
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            row_dict[header] = values[i]
                        else:
                            row_dict[header] = None
                    data.append(row_dict)
            
            return {
                'type': table_type,
                'headers': headers,
                'data': data,
                'extraction_method': 'llm_fast',
                'metadata': {
                    'rows': len(data),
                    'columns': len(headers)
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse fast response: {e}")
            return {
                'type': table_type,
                'error': 'fast_parse_error',
                'extraction_method': 'llm_fast_failed'
            }
    
    def _structure_simple_table(self, data: Dict) -> Dict[str, Any]:
        """Structure a simple table response."""
        return {
            'type': 'simple',
            'headers': data.get('headers', []),
            'data': data.get('data', []),
            'extraction_method': 'llm',
            'metadata': {
                'rows': len(data.get('data', [])),
                'columns': len(data.get('headers', [])),
                'confidence': 0.85
            }
        }
    
    def _structure_complex_table(self, data: Dict) -> Dict[str, Any]:
        """Structure a complex table response."""
        return {
            'type': 'complex',
            'structure': data.get('structure', {}),
            'data': data.get('data', []),
            'extraction_method': 'llm',
            'metadata': {
                'has_merged_cells': bool(data.get('structure', {}).get('merged_cells')),
                'header_levels': len(data.get('structure', {}).get('headers', {})),
                'confidence': 0.75
            }
        }
    
    def _structure_multi_row_table(self, data: Dict) -> Dict[str, Any]:
        """Structure a multi-row field table response."""
        return {
            'type': 'multi_row',
            'fields': data.get('fields', {}),
            'extraction_method': 'llm',
            'metadata': {
                'field_groups': len(data.get('fields', {})),
                'confidence': 0.80
            }
        }
    
    def enhance_library_results(
        self, 
        image_path: str,
        library_results: List[Dict],
        timeout: int = 30
    ) -> List[Dict]:
        """
        Enhance library extraction results with LLM analysis.
        
        Args:
            image_path: Path to the image
            library_results: Results from library extraction
            timeout: Timeout in seconds
            
        Returns:
            Enhanced table results
        """
        enhanced_results = []
        
        for table in library_results:
            try:
                # Determine if enhancement is needed
                table_type = table.get('type', 'simple')
                confidence = table.get('metadata', {}).get('confidence', 0)
                
                if confidence < 0.7 or table_type in ['complex', 'multi_row']:
                    # Extract with LLM
                    llm_result = self.extract_from_image(
                        image_path, table_type, False, timeout
                    )
                    
                    # Merge results
                    if not llm_result.get('error'):
                        # Use LLM data but keep library metadata
                        enhanced = {
                            **llm_result,
                            'extraction_method': 'hybrid',
                            'library_confidence': confidence,
                            'llm_confidence': llm_result.get('metadata', {}).get('confidence', 0)
                        }
                        enhanced_results.append(enhanced)
                    else:
                        # Keep library result if LLM fails
                        enhanced_results.append(table)
                else:
                    # Keep library result as is
                    enhanced_results.append(table)
                    
            except Exception as e:
                logger.warning(f"Enhancement failed for table: {e}")
                enhanced_results.append(table)
        
        return enhanced_results