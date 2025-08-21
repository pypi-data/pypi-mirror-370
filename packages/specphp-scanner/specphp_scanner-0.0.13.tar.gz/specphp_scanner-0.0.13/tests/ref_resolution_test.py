"""Unit tests for $ref resolution functionality."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from specphp_scanner.cli import load_spec_file
from specphp_scanner.cli import resolve_refs_with_jsonschema


class TestRefResolution(unittest.TestCase):
    """Test cases for $ref resolution functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test API', 'version': '1.0.0'},
            'paths': {
                '/test': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/TestObject',
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'components': {
                'schemas': {
                    'TestObject': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'age': {'type': 'integer'},
                        },
                        'required': ['name'],
                    },
                },
            },
        }

        self.nested_ref_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Nested Ref API', 'version': '1.0.0'},
            'paths': {
                '/nested': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/NestedObject',
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'components': {
                'schemas': {
                    'NestedObject': {
                        'type': 'object',
                        'properties': {
                            'user': {'$ref': '#/components/schemas/User'},
                            'items': {
                                'type': 'array',
                                'items': {'$ref': '#/components/schemas/Item'},
                            },
                        },
                    },
                    'User': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                        },
                    },
                    'Item': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'value': {'type': 'number'},
                        },
                    },
                },
            },
        }

        self.array_ref_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Array Ref API', 'version': '1.0.0'},
            'paths': {
                '/array': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/ArrayItem'},
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'components': {
                'schemas': {
                    'ArrayItem': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'data': {'type': 'string'},
                        },
                    },
                },
            },
        }

    def test_simple_ref_resolution(self):
        """Test simple $ref resolution."""
        resolved = resolve_refs_with_jsonschema(self.simple_spec)

        # Check if $ref was resolved
        schema = resolved['paths']['/test']['post']['requestBody']['content']['application/json']['schema']
        self.assertNotIn('$ref', schema)
        self.assertEqual(schema['type'], 'object')
        self.assertIn('properties', schema)
        self.assertIn('name', schema['properties'])
        self.assertIn('age', schema['properties'])

    def test_nested_ref_resolution(self):
        """Test nested $ref resolution."""
        resolved = resolve_refs_with_jsonschema(self.nested_ref_spec)

        # Check if main $ref was resolved
        schema = resolved['paths']['/nested']['post']['requestBody']['content']['application/json']['schema']
        self.assertNotIn('$ref', schema)

        # Check if nested $ref in properties was resolved
        user_prop = schema['properties']['user']
        self.assertNotIn('$ref', user_prop)
        self.assertEqual(user_prop['type'], 'object')

        # Check if array items $ref was resolved
        items_prop = schema['properties']['items']
        self.assertEqual(items_prop['type'], 'array')
        items_schema = items_prop['items']
        self.assertNotIn('$ref', items_schema)
        self.assertEqual(items_schema['type'], 'object')

    def test_array_ref_resolution(self):
        """Test $ref resolution in array items."""
        resolved = resolve_refs_with_jsonschema(self.array_ref_spec)

        # Check if array items $ref was resolved
        schema = resolved['paths']['/array']['post']['requestBody']['content']['application/json']['schema']
        self.assertEqual(schema['type'], 'array')

        items_schema = schema['items']
        self.assertNotIn('$ref', items_schema)
        self.assertEqual(items_schema['type'], 'object')
        self.assertIn('id', items_schema['properties'])
        self.assertIn('data', items_schema['properties'])

    def test_no_refs_spec(self):
        """Test spec without $ref references."""
        spec_without_refs = {
            'openapi': '3.0.0',
            'info': {'title': 'No Ref API', 'version': '1.0.0'},
            'paths': {
                '/simple': {
                    'get': {
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'string',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }

        resolved = resolve_refs_with_jsonschema(spec_without_refs)
        self.assertEqual(resolved, spec_without_refs)

    def test_invalid_ref_path(self):
        """Test handling of invalid $ref paths."""
        invalid_ref_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Invalid Ref API', 'version': '1.0.0'},
            'paths': {
                '/invalid': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/NonExistentSchema',
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'components': {
                'schemas': {},
            },
        }

        # Should not raise exception, should keep original $ref
        resolved = resolve_refs_with_jsonschema(invalid_ref_spec)
        schema = resolved['paths']['/invalid']['post']['requestBody']['content']['application/json']['schema']
        self.assertIn('$ref', schema)

    def test_external_ref_handling(self):
        """Test handling of external $ref references."""
        external_ref_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'External Ref API', 'version': '1.0.0'},
            'paths': {
                '/external': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': 'https://example.com/schema.json#/definitions/User',
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }

        # External refs should be kept as-is (not resolved)
        resolved = resolve_refs_with_jsonschema(external_ref_spec)
        schema = resolved['paths']['/external']['post']['requestBody']['content']['application/json']['schema']
        self.assertIn('$ref', schema)
        self.assertTrue(schema['$ref'].startswith('https://'))

    def test_load_spec_file_json(self):
        """Test loading JSON spec file with $ref resolution."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.simple_spec, f)
            temp_file = Path(f.name)

        try:
            resolved = load_spec_file(temp_file)

            # Check if $ref was resolved
            schema = resolved['paths']['/test']['post']['requestBody']['content']['application/json']['schema']
            self.assertNotIn('$ref', schema)
            self.assertEqual(schema['type'], 'object')

        finally:
            temp_file.unlink()

    def test_load_spec_file_yaml(self):
        """Test loading YAML spec file with $ref resolution."""
        import yaml

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.simple_spec, f)
            temp_file = Path(f.name)

        try:
            resolved = load_spec_file(temp_file)

            # Check if $ref was resolved
            schema = resolved['paths']['/test']['post']['requestBody']['content']['application/json']['schema']
            self.assertNotIn('$ref', schema)
            self.assertEqual(schema['type'], 'object')

        finally:
            temp_file.unlink()

    def test_load_spec_file_unsupported_format(self):
        """Test loading unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('This is not a valid spec file')
            temp_file = Path(f.name)

        try:
            with self.assertRaises(ValueError) as context:
                load_spec_file(temp_file)

            self.assertIn('Unsupported file format', str(context.exception))

        finally:
            temp_file.unlink()

    def test_load_spec_file_not_found(self):
        """Test loading non-existent file."""
        non_existent_file = Path('/non/existent/file.yaml')

        with self.assertRaises(FileNotFoundError):
            load_spec_file(non_existent_file)

    def test_resolve_refs_recursive_structure(self):
        """Test recursive $ref resolution in complex nested structures."""
        complex_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Complex API', 'version': '1.0.0'},
            'paths': {
                '/complex': {
                    'post': {
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'main': {'$ref': '#/components/schemas/MainObject'},
                                            'secondary': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'ref': {'$ref': '#/components/schemas/SecondaryObject'},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'components': {
                'schemas': {
                    'MainObject': {
                        'type': 'object',
                        'properties': {
                            'nested': {'$ref': '#/components/schemas/NestedObject'},
                        },
                    },
                    'NestedObject': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                        },
                    },
                    'SecondaryObject': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                        },
                    },
                },
            },
        }

        resolved = resolve_refs_with_jsonschema(complex_spec)

        # Check if all $ref were resolved
        schema = resolved['paths']['/complex']['post']['requestBody']['content']['application/json']['schema']

        # Main object should be resolved
        main_prop = schema['properties']['main']
        self.assertNotIn('$ref', main_prop)

        # Nested object should be resolved
        nested_prop = main_prop['properties']['nested']
        self.assertNotIn('$ref', nested_prop)
        self.assertEqual(nested_prop['type'], 'object')

        # Secondary object in array should be resolved
        secondary_array = schema['properties']['secondary']
        secondary_item = secondary_array['items']['properties']['ref']
        self.assertNotIn('$ref', secondary_item)
        self.assertEqual(secondary_item['type'], 'object')


if __name__ == '__main__':
    unittest.main()
