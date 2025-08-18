import os
import re
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with defaults.
    
    Args:
        config_path: Path to config file. If None, looks for blueprint.yml in current dir.
    
    Returns:
        Dictionary containing configuration
    """
    default_config = {
        'backend': 'flask',
        'database': 'sqlite',
        'auth_type': 'none',
        'include_tests': True,
        'docker_setup': True,
        'api_prefix': '/api/v1',
        'cors_enabled': True,
        'rate_limiting': False
    }
    
    if config_path is None:
        config_path = 'blueprint.yml'
    
    if not os.path.exists(config_path):
        return default_config
    
    with open(config_path, 'r') as f:
        user_config = yaml.safe_load(f) or {}
    
    return {**default_config, **user_config}

def sanitize_name(name: str) -> str:
    """
    Convert a string to a valid Python identifier.
    
    Args:
        name: Input string to sanitize
        
    Returns:
        Sanitized string suitable for use as Python identifier
    """
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Remove leading numbers
    name = re.sub(r'^[0-9]+', '', name)
    return name.lower()

def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> None:
    """
    Create a directory structure from a nested dictionary.
    
    Args:
        base_path: Root directory where structure should be created
        structure: Nested dictionary representing directory structure
                  (keys are dir/file names, values are contents or nested structures)
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a directory
            path.mkdir(exist_ok=True)
            create_directory_structure(path, content)
        else:
            # It's a file
            if isinstance(content, str):
                path.write_text(content)
            else:
                # Assume content is binary
                path.write_bytes(content)

def convert_to_snake_case(name: str) -> str:
    """
    Convert CamelCase or mixedCase to snake_case.
    
    Args:
        name: String to convert
        
    Returns:
        snake_case version of input string
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()

def get_foreign_key_reference(model_name: str) -> str:
    """
    Generate proper foreign key reference for a model.
    
    Args:
        model_name: Name of the referenced model
        
    Returns:
        String representing foreign key reference
    """
    return f"{convert_to_snake_case(model_name)}_id"

def validate_spec(spec: Dict[str, Any]) -> bool:
    """
    Validate the parsed specification for required fields and structure.
    
    Args:
        spec: Parsed specification dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_sections = ['models', 'endpoints']
    for section in required_sections:
        if section not in spec:
            return False
    
    # Validate models
    for model in spec['models']:
        if not hasattr(model, 'name') or not hasattr(model, 'fields'):
            return False
    
    # Validate endpoints
    for endpoint in spec['endpoints']:
        if not hasattr(endpoint, 'method') or not hasattr(endpoint, 'path'):
            return False
    
    return True

def copy_template_files(source_dir: Path, dest_dir: Path, context: Dict[str, Any] = None) -> None:
    """
    Copy template files from source to destination, processing any templated files.
    
    Args:
        source_dir: Directory containing template files
        dest_dir: Destination directory
        context: Dictionary of variables to use when processing templates
    """
    if context is None:
        context = {}
    
    for item in source_dir.iterdir():
        dest_path = dest_dir / item.name
        
        if item.is_dir():
            dest_path.mkdir(exist_ok=True)
            copy_template_files(item, dest_path, context)
        else:
            if item.suffix == '.j2':
                # Process Jinja2 template
                from jinja2 import Template
                template = Template(item.read_text())
                rendered = template.render(**context)
                dest_path = dest_dir / item.stem  # Remove .j2 extension
                dest_path.write_text(rendered)
            else:
                # Copy regular file
                shutil.copy2(item, dest_path)

def get_python_type(field_type: str) -> str:
    """
    Map field types from spec to Python types.
    
    Args:
        field_type: Field type from specification
        
    Returns:
        Corresponding Python type
    """
    type_mapping = {
        'integer': 'int',
        'bigint': 'int',
        'string': 'str',
        'text': 'str',
        'boolean': 'bool',
        'decimal': 'float',
        'float': 'float',
        'datetime': 'datetime.datetime',
        'date': 'datetime.date',
        'time': 'datetime.time',
        'email': 'str',
        'url': 'str',
        'uuid': 'uuid.UUID',
        'json': 'dict'
    }
    return type_mapping.get(field_type.lower(), 'Any')

def generate_random_data(model: Any, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate random test data for a model.
    
    Args:
        model: Model class to generate data for
        count: Number of records to generate
        
    Returns:
        List of dictionaries with random data
    """
    from faker import Faker
    fake = Faker()
    data = []
    
    for _ in range(count):
        record = {}
        for field in model.__table__.columns:
            field_type = str(field.type).lower()
            
            if field_type.startswith('integer'):
                record[field.name] = fake.random_int()
            elif field_type.startswith('varchar') or field_type.startswith('string'):
                record[field.name] = fake.word()
            elif field_type.startswith('text'):
                record[field.name] = fake.text()
            elif field_type.startswith('boolean'):
                record[field.name] = fake.boolean()
            elif field_type.startswith('datetime'):
                record[field.name] = fake.date_time_this_decade()
            elif field_type.startswith('date'):
                record[field.name] = fake.date_this_decade()
            elif field_type.startswith('float'):
                record[field.name] = fake.pyfloat()
            else:
                record[field.name] = None
                
        data.append(record)
    
    return data

def get_required_packages(backend: str, database: str) -> List[str]:
    """
    Get required Python packages based on backend and database choices.
    
    Args:
        backend: API framework ('flask', 'fastapi')
        database: Database type ('sqlite', 'postgresql', 'mysql')
        
    Returns:
        List of required package strings
    """
    packages = []
    
    # Backend packages
    if backend == 'flask':
        packages.extend(['flask', 'flask-sqlalchemy', 'flask-migrate'])
    elif backend == 'fastapi':
        packages.extend(['fastapi', 'sqlalchemy', 'alembic'])
    
    # Database packages
    if database == 'postgresql':
        packages.append('psycopg2-binary')
    elif database == 'mysql':
        packages.append('mysql-connector-python')
    
    # Common packages
    packages.extend([
        'pydantic',
        'python-dotenv',
        'python-jose[cryptography]',  # For JWT
        'passlib'  # For password hashing
    ])
    
    return packages

def format_validation_error(errors: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format validation errors for API responses.
    
    Args:
        errors: Validation errors from Pydantic or similar
        
    Returns:
        Formatted error response dictionary
    """
    formatted = {'error': 'Validation failed', 'details': {}}
    for field, field_errors in errors.items():
        if isinstance(field_errors, list):
            formatted['details'][field] = field_errors[0]
        else:
            formatted['details'][field] = str(field_errors)
    return formatted