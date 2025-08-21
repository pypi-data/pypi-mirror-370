"""Unit tests for scanner functionality."""
from __future__ import annotations

import unittest

from specphp_scanner.core.scanner import _generate_array_body
from specphp_scanner.core.scanner import _generate_boolean_value
from specphp_scanner.core.scanner import _generate_integer_value
from specphp_scanner.core.scanner import _generate_number_value
from specphp_scanner.core.scanner import _generate_object_body
from specphp_scanner.core.scanner import _generate_string_value
from specphp_scanner.core.scanner import _generate_value_from_schema
from specphp_scanner.core.scanner import generate_request_body


class TestRequestBodyGeneration(unittest.TestCase):
    """Test cases for request body generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_object_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'active': {'type': 'boolean'},
            },
            'required': ['name'],
        }

        self.array_schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'value': {'type': 'number'},
                },
                'required': ['id'],
            },
            'minItems': 1,
            'maxItems': 3,
        }

        self.string_schema = {
            'type': 'string',
            'minLength': 3,
            'maxLength': 10,
        }

        self.enum_schema = {
            'type': 'string',
            'enum': ['option1', 'option2', 'option3'],
        }

        self.format_schema = {
            'type': 'string',
            'format': 'email',
        }

        self.integer_schema = {
            'type': 'integer',
            'minimum': 10,
            'maximum': 100,
        }

        self.number_schema = {
            'type': 'number',
            'minimum': 0.5,
            'maximum': 10.5,
        }

    def test_generate_request_body_object(self):
        """Test generating request body for object type schema."""
        result = generate_request_body(self.simple_object_schema)

        self.assertIsInstance(result, dict)
        self.assertIn('name', result)  # Required field should be included
        self.assertIsInstance(result['name'], str)

        # Optional fields may or may not be present
        if 'age' in result:
            self.assertIsInstance(result['age'], int)
        if 'active' in result:
            self.assertIsInstance(result['active'], bool)

    def test_generate_request_body_array(self):
        """Test generating request body for array type schema."""
        result = generate_request_body(self.array_schema)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertLessEqual(len(result), 3)

        for item in result:
            self.assertIsInstance(item, dict)
            # Required field should always be present
            self.assertIn('id', item)
            self.assertIsInstance(item['id'], str)
            # Optional field may or may not be present
            if 'value' in item:
                self.assertIsInstance(item['value'], (int, float))

    def test_generate_request_body_string(self):
        """Test generating request body for string type schema."""
        result = generate_request_body(self.string_schema)

        self.assertIsInstance(result, str)
        self.assertGreaterEqual(len(result), 3)
        self.assertLessEqual(len(result), 10)

    def test_generate_request_body_enum(self):
        """Test generating request body for enum string schema."""
        result = generate_request_body(self.enum_schema)

        self.assertIn(result, ['option1', 'option2', 'option3'])

    def test_generate_request_body_format(self):
        """Test generating request body for formatted string schema."""
        result = generate_request_body(self.format_schema)

        self.assertIsInstance(result, str)
        self.assertIn('@', result)  # Should be an email format

    def test_generate_request_body_integer(self):
        """Test generating request body for integer type schema."""
        result = generate_request_body(self.integer_schema)

        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 10)
        self.assertLessEqual(result, 100)

    def test_generate_request_body_number(self):
        """Test generating request body for number type schema."""
        result = generate_request_body(self.number_schema)

        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.5)
        self.assertLessEqual(result, 10.5)

    def test_generate_request_body_boolean(self):
        """Test generating request body for boolean type schema."""
        result = generate_request_body({'type': 'boolean'})

        self.assertIsInstance(result, bool)

    def test_generate_request_body_empty_schema(self):
        """Test generating request body for empty schema."""
        result = generate_request_body({})

        self.assertEqual(result, {})

    def test_generate_request_body_none_schema(self):
        """Test generating request body for None schema."""
        result = generate_request_body(None)

        self.assertEqual(result, {})

    def test_generate_request_body_unsupported_type(self):
        """Test generating request body for unsupported schema type."""
        result = generate_request_body({'type': 'unsupported'})

        self.assertEqual(result, {})

    def test_generate_object_body_with_required_fields(self):
        """Test generating object body with required fields."""
        result = _generate_object_body(self.simple_object_schema)

        # Required field should always be included
        self.assertIn('name', result)
        self.assertIsInstance(result['name'], str)

    def test_generate_array_body_with_constraints(self):
        """Test generating array body with min/max constraints."""
        result = _generate_array_body(self.array_schema)

        self.assertGreaterEqual(len(result), 1)
        self.assertLessEqual(len(result), 3)

    def test_generate_string_value_with_constraints(self):
        """Test generating string value with length constraints."""
        result = _generate_string_value(self.string_schema)

        self.assertGreaterEqual(len(result), 3)
        self.assertLessEqual(len(result), 10)

    def test_generate_integer_value_with_constraints(self):
        """Test generating integer value with range constraints."""
        result = _generate_integer_value(self.integer_schema)

        self.assertGreaterEqual(result, 10)
        self.assertLessEqual(result, 100)

    def test_generate_number_value_with_constraints(self):
        """Test generating number value with range constraints."""
        result = _generate_number_value(self.number_schema)

        self.assertGreaterEqual(result, 0.5)
        self.assertLessEqual(result, 10.5)

    def test_generate_boolean_value(self):
        """Test generating boolean value."""
        result = _generate_boolean_value()

        self.assertIsInstance(result, bool)

    def test_generate_value_from_schema_recursive(self):
        """Test generating value from schema with recursive types."""
        recursive_schema = {
            'type': 'object',
            'properties': {
                'nested': {
                    'type': 'object',
                    'properties': {
                        'value': {'type': 'string'},
                    },
                },
            },
        }

        result = _generate_value_from_schema(recursive_schema)

        self.assertIsInstance(result, dict)
        # Fields may or may not be present due to random generation
        if 'nested' in result:
            self.assertIsInstance(result['nested'], dict)
            if 'value' in result['nested']:
                self.assertIsInstance(result['nested']['value'], str)

    def test_generate_value_from_schema_array_recursive(self):
        """Test generating value from schema with array of objects."""
        array_schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                },
            },
        }

        result = _generate_value_from_schema(array_schema)

        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, dict)
            self.assertIn('id', item)
            self.assertIsInstance(item['id'], int)


if __name__ == '__main__':
    unittest.main()
