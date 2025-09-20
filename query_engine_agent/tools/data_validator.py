"""
Data Validator Tool - Validates and sanitizes query results
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataValidator:
    """Tool for validating and sanitizing query results"""

    def validate_data(self, data: List[Dict[str, Any]], query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize query results"""

        logger.info(f"Validating {len(data)} records...")

        try:
            validation_result = {
                'is_valid': True,
                'cleaned_data': [],
                'warnings': [],
                'stats': {}
            }

            if not data:
                validation_result['warnings'].append("No data returned from query")
                return validation_result

            # Clean and validate each record
            cleaned_data = []
            null_count = 0
            numeric_fields = set()

            for i, record in enumerate(data):
                cleaned_record = {}

                for key, value in record.items():
                    cleaned_value = self._clean_value(value)

                    if cleaned_value is None:
                        null_count += 1

                    # Track numeric fields
                    if isinstance(cleaned_value, (int, float)):
                        numeric_fields.add(key)

                    cleaned_record[key] = cleaned_value

                cleaned_data.append(cleaned_record)

            validation_result['cleaned_data'] = cleaned_data

            # Generate statistics
            validation_result['stats'] = {
                'total_records': len(data),
                'null_values': null_count,
                'numeric_fields': list(numeric_fields),
                'field_count': len(data[0]) if data else 0
            }

            # Validation warnings
            if null_count > len(data) * 0.1:  # More than 10% nulls
                validation_result['warnings'].append(f"High null value rate: {null_count}/{len(data)} values")

            if len(data) == 0:
                validation_result['warnings'].append("Empty result set")

            logger.info(f"✅ Validation complete: {len(cleaned_data)} records, {len(validation_result['warnings'])} warnings")

            return validation_result

        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {
                'is_valid': False,
                'cleaned_data': data,  # Return original data on validation failure
                'warnings': [f"Validation error: {str(e)}"],
                'stats': {}
            }

    def _clean_value(self, value: Any) -> Any:
        """Clean individual values"""

        # Handle None/NULL values
        if value is None or value == '' or value == 'NULL':
            return None

        # Handle numeric strings
        if isinstance(value, str):
            # Try to convert to number
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                # Keep as string, but clean whitespace
                return value.strip()

        # Handle boolean strings
        if isinstance(value, str):
            lower_val = value.lower()
            if lower_val in ['true', 'yes', '1']:
                return True
            elif lower_val in ['false', 'no', '0']:
                return False

        return value

    def validate_schema(self, data: List[Dict[str, Any]], expected_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate data schema against expected fields"""

        if not data:
            return {'valid': True, 'missing_fields': [], 'extra_fields': []}

        actual_fields = set(data[0].keys()) if data else set()

        if expected_fields:
            expected_set = set(expected_fields)
            missing_fields = list(expected_set - actual_fields)
            extra_fields = list(actual_fields - expected_set)

            return {
                'valid': len(missing_fields) == 0,
                'missing_fields': missing_fields,
                'extra_fields': extra_fields,
                'actual_fields': list(actual_fields)
            }

        return {
            'valid': True,
            'missing_fields': [],
            'extra_fields': [],
            'actual_fields': list(actual_fields)
        }