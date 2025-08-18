# File: generators/fastapi_generator.py (enhanced version)
from pathlib import Path
from typing import Dict, Any, List
from api_blueprint_generator.generators.base_generator import BaseGenerator

class FastAPIGenerator(BaseGenerator):
    def __init__(self, spec: Dict[str, Any], output_dir: str, template_dir: str = None, dry_run: bool = False):
        super().__init__(spec, output_dir, template_dir, dry_run)
        self._setup_fastapi_specifics()
        
    def _get_template_dir(self) -> Path:
        """Get the directory containing FastAPI templates."""
        return Path(__file__).parent.parent / 'templates' / 'fastapi'
    
    def _setup_fastapi_specifics(self):
        """Initialize FastAPI-specific configurations."""
        pass  # No specific setup needed at the moment
        
    def generate(self):
        """Generate FastAPI project with enhanced features."""
        print(f"🚀 Generating FastAPI project...")
        
        # The base class now orchestrates all generation steps
        super().generate()
        
        # Print summary
        summary = self.get_generation_summary()
        print(f"\n📊 Generation Summary:")
        print(f"   • Backend: {summary['backend']}")
        print(f"   • Models: {summary['models']}")
        print(f"   • Endpoints: {summary['endpoints']}")
        print(f"   • Database: {summary['database']}")
        print(f"   • Auth: {'Enabled' if summary['auth_enabled'] else 'Disabled'}")
        print(f"   • Output: {summary['output_directory']}")
        
    def _get_framework_specific_requirements(self) -> List[str]:
        """Get FastAPI-specific requirements."""
        return [
            'fastapi',
            'uvicorn[standard]',
            'pydantic[email]'
        ]
        
    def _generate_routes(self):
        """Generate FastAPI route handlers."""
        if not self.spec.get('models'):
            return
            
        routes_dir = self.output_dir / 'app' / 'routes'
        routes_dir.mkdir(exist_ok=True)
        
        # Generate individual route files for each model
        for model in self.spec['models']:
            self._generate_model_routes(model)
            
        # Generate auth routes if auth is enabled
        if self.spec.get('config', {}).get('auth_type', 'none') != 'none':
            self._generate_auth_routes()
            
        print(f"✓ Generated {len(self.spec['models'])} route files")
        
    def _generate_model_routes(self, model: Any):
        """Generate CRUD routes for a specific model."""
        template = self.template_env.get_template('model_routes.py.j2')
        auth_enabled = self.spec.get('config', {}).get('auth_type', 'none') != 'none'
        api_prefix = self.spec.get('config', {}).get('api_prefix', '/api/v1').rstrip('/')
        
        # Find endpoint-specific configurations like permissions
        endpoint_map = {(e.method.upper(), e.path): e for e in self.spec.get('endpoints', [])}
        
        def get_endpoint_prop(method: str, path_suffix: str, prop: str):
            # Note: The spec path might not include the full API prefix, so we check both
            full_path = f"{api_prefix}/{path_suffix}"
            endpoint = endpoint_map.get((method, full_path)) or endpoint_map.get((method, f"/{path_suffix}"))
            return getattr(endpoint, prop, None) if endpoint else None

        permissions = {
            'create': get_endpoint_prop('POST', model.name_plural_snake, 'permissions'),
            'update': get_endpoint_prop('PUT', f"{model.name_plural_snake}/{{{model.name_snake}_id}}", 'permissions'),
            'delete': get_endpoint_prop('DELETE', f"{model.name_plural_snake}/{{{model.name_snake}_id}}", 'permissions'),
        }
        
        routes_code = template.render(
            model=model,
            auth_enabled=auth_enabled,
            imports=self._get_route_imports(auth_enabled),
            permissions=permissions
        )
            
        self._write_file(f"app/routes/{model.name_snake}_routes.py", routes_code)
        
    def _generate_auth_routes(self):
        """Generate authentication routes."""
        if self._template_exists('auth_routes.py.j2'):
            template = self.template_env.get_template('auth_routes.py.j2')
            auth_code = template.render()
            self._write_file('app/routes/auth_routes.py', auth_code)
            print("✓ Generated auth_routes.py")
        
    def _generate_schemas(self):
        """Generate Pydantic schemas for request/response validation."""
        if not self.spec.get('models'):
            return
            
        template = self.template_env.get_template('schemas.py.j2')
        
        # Dynamically determine necessary imports for the schemas file
        schema_imports = self._get_schema_imports()

        # Prepare schemas data
        schemas_data = []
        for model in self.spec['models']:
            schemas_data.extend(self._create_model_schemas(model))
            
        # Get a list of response schema names that might have forward refs
        response_schema_names = [f"{m.name_pascal}Response" for m in self.spec['models']]
            
        schemas_code = template.render(
            imports=schema_imports,
            schemas=schemas_data,
            auth_enabled=self.spec.get('config', {}).get('auth_type', 'none') != 'none',
            response_schema_names=response_schema_names
        )
        
        self._write_file('app/schemas.py', schemas_code)
        print("✓ Generated schemas.py")
        
    def _create_model_schemas(self, model: Any) -> List[Dict[str, Any]]:
        """Create Pydantic schema definitions for a model."""
        schemas = []
        model_name_pascal = model.name_pascal
        
        # Base schema
        schemas.append({
            'name': f"{model_name_pascal}Base",
            'fields': [
                self._convert_field_to_schema(field) 
                for field in model.fields 
                if not field.options.get('primary_key') 
                   and not field.is_foreign_key
                   and not field.options.get('write_only')
            ],
            'config': {'from_attributes': True}
        })
        
        # Create schema
        create_extra_fields = [
            self._convert_field_to_schema(field)
            for field in model.fields if field.is_foreign_key
        ]
        create_extra_fields.extend([
            self._convert_field_to_schema(field)
            for field in model.fields if field.options.get('write_only')
        ])
        schemas.append({
            'name': f"{model_name_pascal}Create",
            'base': f"{model_name_pascal}Base",
            'fields': create_extra_fields
        })
        
        # Update schema
        schemas.append({
            'name': f"{model_name_pascal}Update",
            'base': 'BaseModel',  # Does not inherit, all fields are optional
            'fields': [
                {**self._convert_field_to_schema(field), 'optional': True} 
                for field in model.fields 
                if not field.options.get('primary_key') and not field.options.get('read_only')
            ]
        })
        
        # Response schema
        response_extra_fields = [
            self._convert_field_to_schema(field) 
            for field in model.fields 
            if field.options.get('primary_key')
        ]
        for rel in model.relationships:
            response_extra_fields.append({
                'name': rel.name,
                'type': f"'{rel.target_model}Response'" if not rel.is_list else f"List['{rel.target_model}Response']",
                'optional': True,
                'default': None
            })

        schemas.append({
            'name': f"{model_name_pascal}Response",
            'base': f"{model_name_pascal}Base",
            'fields': response_extra_fields
        })
        
        return schemas
        
    def _convert_field_to_schema(self, field: Any) -> Dict[str, Any]:
        """Convert a model field to schema field definition."""
        return {
            'name': field.name,
            'type': self._get_pydantic_type(field.type),
            'required': field.options.get('required', False),
            'default': field.options.get('default'),
            'description': getattr(field, 'description', None)
        }
        
    def _get_pydantic_type(self, field_type: str) -> str:
        """Map SQLAlchemy types to Pydantic schema types."""
        type_mapping = {
            'integer': 'int',
            'bigint': 'int', 
            'string': 'str',
            'text': 'str',
            'boolean': 'bool',
            'decimal': 'float',
            'float': 'float',
            'datetime': 'datetime',
            'date': 'date',
            'time': 'time',
            'email': 'EmailStr',
            'url': 'HttpUrl',
            'uuid': 'UUID',
            'json': 'Dict'
        }
        return type_mapping.get(field_type.lower(), 'str')

    def _get_schema_imports(self) -> List[str]:
        """Collect necessary imports for the schemas.py file based on used types."""
        pydantic_imports = {"BaseModel"}
        typing_imports = {"Optional", "List", "Dict"}
        datetime_imports = set()
        other_imports = set()

        type_to_module = {
            'datetime': ('datetime', 'datetime'),
            'date': ('datetime', 'date'),
            'time': ('datetime', 'time'),
            'email': ('pydantic', 'EmailStr'),
            'url': ('pydantic', 'HttpUrl'),
            'uuid': ('uuid', 'UUID'),
        }

        for model in self.spec.get('models', []):
            for field in model.fields:
                if field.type.lower() in type_to_module:
                    module, class_name = type_to_module[field.type.lower()]
                    if module == 'pydantic': pydantic_imports.add(class_name)
                    elif module == 'datetime': datetime_imports.add(class_name)
                    elif module == 'uuid': other_imports.add("from uuid import UUID")

        final_imports = []
        if pydantic_imports:
            final_imports.append(f"from pydantic import {', '.join(sorted(list(pydantic_imports)))}")
        if typing_imports:
            final_imports.append(f"from typing import {', '.join(sorted(list(typing_imports)))}")
        if datetime_imports:
            final_imports.append(f"from datetime import {', '.join(sorted(list(datetime_imports)))}")
        final_imports.extend(sorted(list(other_imports)))
        return final_imports
        
    def _generate_crud(self):
        """Generate CRUD operations."""
        if not self.spec.get('models'):
            return
            
        template = self.template_env.get_template('crud.py.j2')
        # The template expects the full 'spec' object to access its properties
        crud_code = template.render(spec=self.spec)
        
        self._write_file('app/crud.py', crud_code)
        print("✓ Generated crud.py")
        
    def _generate_database(self):
        """Generate database configuration."""
        template = self.template_env.get_template('database.py.j2')
        db_type = self.spec.get('config', {}).get('database', 'sqlite')
        
        database_code = template.render(
            database_type=db_type,
            database_url=self._get_database_url(db_type)
        )
        
        self._write_file('app/database.py', database_code)
        print("✓ Generated database.py")
        
    def _generate_auth(self):
        """Generate authentication module."""
        if self.spec.get('config', {}).get('auth_type', 'none') == 'none':
            return
            
        template = self.template_env.get_template('auth.py.j2')
        auth_code = template.render(
            auth_type=self.spec.get('config', {}).get('auth_type', 'jwt'),
            secret_key_env='SECRET_KEY'
        )
        
        self._write_file('app/auth.py', auth_code)
        print("✓ Generated auth.py")
        
    def _generate_main_app(self):
        """Generate main FastAPI application file."""
        template = self.template_env.get_template('main.py.j2')
        api_prefix = self.spec.get('config', {}).get('api_prefix', '/api/v1').rstrip('/')
        
        # Collect all routers
        routers = []
        for model in self.spec.get('models', []):
            routers.append({
                'name': f"{model.name_snake}_router",
                'module': f"{model.name_snake}_routes",
                'prefix': f"{api_prefix}/{model.name_plural_snake}",
                'tags': [model.name_plural_snake]
            })
        
        # Add auth router if enabled
        auth_enabled = self.spec.get('config', {}).get('auth_type', 'none') != 'none'
        if auth_enabled:
            routers.append({
                'name': 'auth_router',
                'module': 'auth_routes', 
                'prefix': '/auth',
                'tags': ['authentication']
            })
        
        main_code = template.render(
            app_name=self.spec.get('title', 'FastAPI Application'),
            routers=routers,
            auth_enabled=auth_enabled,
            cors_enabled=self.spec.get('config', {}).get('cors_enabled', True)
        )
            
        self._write_file('app/main.py', main_code)
        print("✓ Generated main.py")
        
    def _generate_app_config(self):
        """Generate the Pydantic Settings configuration file."""
        print("✓ Generating application settings...")
        if self._template_exists('app/config.py.j2'):
            template = self.template_env.get_template('app/config.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('app/config.py', content)

    def _generate_migrations(self):
        """Generate Alembic migration configuration for the project."""
        print("✓ Generating database migration setup...")
        alembic_dir = self.output_dir / 'alembic'
        versions_dir = alembic_dir / 'versions'
        if self.dry_run:
            self.planned_files.append(alembic_dir)
            self.planned_files.append(versions_dir)
        else:
            alembic_dir.mkdir(exist_ok=True)
            versions_dir.mkdir(exist_ok=True)

        # alembic.ini
        if self._template_exists('alembic.ini.j2'):
            template = self.template_env.get_template('alembic.ini.j2')
            content = template.render(spec=self.spec)
            self._write_file('alembic.ini', content)

        # alembic/env.py
        if self._template_exists('alembic/env.py.j2'):
            template = self.template_env.get_template('alembic/env.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('alembic/env.py', content)

    def _generate_ci(self):
        """Generate a GitHub Actions CI workflow file."""
        print("✓ Generating CI/CD workflow...")
        workflow_dir = self.output_dir / '.github' / 'workflows'
        if self.dry_run:
            self.planned_files.append(workflow_dir)
        else:
            workflow_dir.mkdir(parents=True, exist_ok=True)

        if self._template_exists('.github/workflows/ci.yml.j2'):
            template = self.template_env.get_template('.github/workflows/ci.yml.j2')
            content = template.render(spec=self.spec)
            self._write_file('.github/workflows/ci.yml', content)

    def _generate_tasks(self):
        """Generate Celery worker and task files."""
        print("✓ Generating background worker setup...")

        # Generate app/worker.py
        if self._template_exists('app/worker.py.j2'):
            template = self.template_env.get_template('app/worker.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('app/worker.py', content)

        # Generate app/tasks.py with an example task
        if self._template_exists('app/tasks.py.j2'):
            template = self.template_env.get_template('app/tasks.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('app/tasks.py', content)

    def _generate_tests(self):
        """Generate a comprehensive test suite for the FastAPI application."""
        if not self.spec.get('config', {}).get('include_tests', False):
            return

        print("✓ Generating test suite...")
        tests_dir = self.output_dir / 'tests'
        tests_dir.mkdir(exist_ok=True)

        # Generate conftest.py for test fixtures
        if self._template_exists('tests/conftest.py.j2'):
            template = self.template_env.get_template('tests/conftest.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('tests/conftest.py', content)

        # Generate authentication tests if auth is enabled
        auth_enabled = self.spec.get('config', {}).get('auth_type', 'none') != 'none'
        if auth_enabled and self._template_exists('tests/test_auth.py.j2'):
            template = self.template_env.get_template('tests/test_auth.py.j2')
            content = template.render(spec=self.spec)
            self._write_file('tests/test_auth.py', content)

        # Generate model-specific CRUD and RBAC tests
        api_prefix = self.spec.get('config', {}).get('api_prefix', '/api/v1').rstrip('/')
        if self._template_exists('tests/test_model_crud.py.j2'):
            template = self.template_env.get_template('tests/test_model_crud.py.j2')
            endpoint_map = {(e.method.upper(), e.path): e for e in self.spec.get('endpoints', [])}

            for model in self.spec.get('models', []):
                # Skip User model tests if auth is on, as they are covered by test_auth.py
                if model.name == 'User' and auth_enabled:
                    continue

                def get_endpoint_prop(method: str, path_suffix: str, prop: str):
                    full_path = f"{api_prefix}/{path_suffix}"
                    endpoint = endpoint_map.get((method, full_path)) or endpoint_map.get((method, f"/{path_suffix}"))
                    return getattr(endpoint, prop, None) if endpoint else None

                permissions = {
                    'delete': get_endpoint_prop('DELETE', f"{model.name_plural_snake}/{{{model.name_snake}_id}}", 'permissions'),
                }

                content = template.render(spec=self.spec, model=model, api_prefix=api_prefix, auth_enabled=auth_enabled, permissions=permissions)
                self._write_file(f'tests/test_{model.name_snake}_crud.py', content)
        
    def _get_route_imports(self, auth_enabled: bool) -> List[str]:
        """Get necessary imports for route files."""
        imports = [
            "from typing import List",
            "from fastapi import APIRouter, Depends, HTTPException, status", 
            "from sqlalchemy.orm import Session",
            "from ..database import get_db",
            "from .. import crud, schemas"
        ]
        
        if auth_enabled:
            imports.extend([
                "from ..auth import get_current_active_user",
                "from .. import models"
            ])
            
        return imports