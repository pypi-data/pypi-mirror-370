# File: generators/base_generator.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
import json
import yaml

def pluralize(value):
    """A simple Jinja2 filter to pluralize a word."""
    if value.endswith('y'):
        return value[:-1] + 'ies'
    if value.endswith('s'):
        return value + 'es'
    return value + 's'
class BaseGenerator:
    def __init__(self, spec: Dict[str, Any], output_dir: str, template_dir: str = None, dry_run: bool = False):
        self.spec = spec
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.planned_files: List[Path] = []

        # Determine template path
        if template_dir:
            self.template_path = Path(template_dir)
        else:
            self.template_path = self._get_template_dir()

        # Setup Jinja2 environment
        self.template_env = Environment(
            loader=FileSystemLoader(self.template_path),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # Register custom filters
        self.template_env.filters['pluralize'] = pluralize
        
    def _get_template_dir(self) -> Path:
        """Get the template directory for this generator. Must be implemented by subclasses."""
        raise NotImplementedError
        
    def generate(self):
        """Generate the complete API project."""
        print(f"Generating API project in {self.output_dir}")
        self._create_project_structure()
        self._generate_models()
        self._generate_routes()
        self._generate_schemas()
        self._generate_crud()
        self._generate_database()
        self._generate_auth()
        self._generate_config()
        self._generate_app_config()
        if self.spec.get('config', {}).get('background_tasks', False):
            self._generate_tasks()
        self._generate_migrations()
        self._generate_main_app()
        self._generate_requirements()
        self._generate_readme()

        if self.spec.get('config', {}).get('docker_setup', False):
            self._generate_docker_files()
            self._generate_ci()
        if self.spec.get('config', {}).get('include_tests', False):
            self._generate_tests()

        if self.dry_run:
            # Return the list of files that would have been created
            return sorted(list(set(self.planned_files)))
        else:
            print("API project generated successfully!")
        
    def _create_project_structure(self):
        """Create the basic directory structure for the project."""
        directories = [
            'app',
            'app/routes', 
            'tests',
            'tests/unit',
            'tests/integration'
        ]
        
        for directory in directories:
            dir_path = self.output_dir / directory
            if self.dry_run:
                self.planned_files.append(dir_path)
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
            
        # Create __init__.py files
        init_files = [
            'app/__init__.py',
            'app/routes/__init__.py',
            'tests/__init__.py',
        ]
        
        for init_file in init_files:
            self._write_file(init_file, "")
            
    def _generate_models(self):
        """Generate SQLAlchemy models from the specification."""
        if not self.spec.get('models'):
            return
            
        template = self.template_env.get_template('models.py.j2')
        model_map = {m.name: m for m in self.spec['models']}
        models_code = template.render(
            spec=self.spec,
            models=self.spec['models'],
            model_map=model_map
        )
        self._write_file('app/models.py', models_code)
        print("✓ Generated models.py")
        
    def _generate_routes(self):
        """Generate route files for each model/endpoint. Must be implemented by subclasses."""
        pass
        
    def _generate_schemas(self):
        """Generate Pydantic schemas. Override in subclasses if needed."""
        pass
        
    def _generate_crud(self):
        """Generate CRUD operations. Override in subclasses if needed."""
        pass
        
    def _generate_database(self):
        """Generate database configuration. Override in subclasses if needed."""
        pass
        
    def _generate_auth(self):
        """Generate authentication modules. Override in subclasses if needed."""
        pass

    def _generate_main_app(self):
        """Generate the main application entrypoint file. Override in subclasses."""
        pass

    def _generate_migrations(self):
        """Generate database migration setup using Alembic."""
        pass

    def _generate_tests(self):
        """Generate test files. Override in subclasses if needed."""
        pass
        
    def _generate_ci(self):
        """Generate CI/CD configuration files (e.g., GitHub Actions)."""
        pass

    def _generate_app_config(self):
        """Generate application configuration files (e.g., settings management)."""
        pass

    def _generate_tasks(self):
        """Generate background task worker setup (e.g., Celery)."""
        pass

    def _generate_config(self):
        """Generate configuration files."""
        # Generate .env template
        if self._template_exists('.env.j2'):
            template = self.template_env.get_template('.env.j2')
            db_type = self.spec.get('config', {}).get('database', 'sqlite')
            env_content = template.render(
                database_url=self._get_database_url(db_type, for_docker=False),
                spec=self.spec,
                secret_key="your-super-secret-key-change-in-production", # This should be changed by the user
                algorithm="HS256"
            )
            self._write_file('.env.example', env_content)
            print("✓ Generated .env.example")
            
    def _generate_requirements(self):
        """Generate requirements.txt file."""
        requirements = self._get_base_requirements()
        requirements.extend(self._get_framework_specific_requirements())
        
        # Add database-specific requirements
        db_type = self.spec.get('config', {}).get('database', 'sqlite')
        requirements.extend(self._get_database_requirements(db_type))
        
        # Add auth requirements if auth is enabled
        if self.spec.get('config', {}).get('auth_type') != 'none':
            requirements.extend(self._get_auth_requirements())
            
        # Add test requirements if tests are included
        if self.spec.get('config', {}).get('include_tests', False):
            requirements.extend(self._get_test_requirements())

        # Add background task requirements if enabled
        if self.spec.get('config', {}).get('background_tasks', False):
            requirements.extend(self._get_task_requirements())
            
        # Remove duplicates and sort
        requirements = sorted(list(set(requirements)))
        
        self._write_file('requirements.txt', '\n'.join(requirements))
        print("✓ Generated requirements.txt")
        
    def _generate_docker_files(self):
        """Generate Docker configuration files."""
        # Generate docker-entrypoint.sh
        if self._template_exists('docker-entrypoint.sh.j2'):
            template = self.template_env.get_template('docker-entrypoint.sh.j2')
            content = template.render(spec=self.spec)
            self._write_file('docker-entrypoint.sh', content)
            print("✓ Generated docker-entrypoint.sh")

        # Generate Dockerfile
        if self._template_exists('Dockerfile.j2'):
            template = self.template_env.get_template('Dockerfile.j2')
            dockerfile_content = template.render(spec=self.spec)
            self._write_file('Dockerfile', dockerfile_content)
            print("✓ Generated Dockerfile")
            
        # Generate docker-compose.yml
        if self._template_exists('docker-compose.yml.j2'):
            template = self.template_env.get_template('docker-compose.yml.j2')
            db_config = self._get_database_config()
            compose_content = template.render(
                spec=self.spec,
                db_config=db_config,
                db_volumes=bool(db_config.get('image'))
            )
            self._write_file('docker-compose.yml', compose_content)
            print("✓ Generated docker-compose.yml")
            
    def _get_base_requirements(self) -> List[str]:
        """Get base Python requirements."""
        return [
            'pydantic',
            'pydantic-settings',
            'python-dotenv',
            'sqlalchemy',
            'alembic'
        ]
        
    def _get_framework_specific_requirements(self) -> List[str]:
        """Get framework-specific requirements. Override in subclasses."""
        return []
        
    def _get_database_requirements(self, db_type: str) -> List[str]:
        """Get database-specific requirements."""
        db_requirements = {
            'postgresql': ['psycopg2-binary'],
            'mysql': ['mysql-connector-python'],
            'sqlite': []  # SQLite is built into Python
        }
        return db_requirements.get(db_type, [])
        
    def _get_auth_requirements(self) -> List[str]:
        """Get authentication-related requirements."""
        return [
            'python-jose[cryptography]',
            'passlib[bcrypt]',
            'python-multipart'
        ]

    def _get_test_requirements(self) -> List[str]:
        """Get testing-related requirements."""
        return [
            'pytest',
            'pytest-cov',
        ]
        
    def _get_task_requirements(self) -> List[str]:
        """Get background task-related requirements."""
        return [
            'celery',
            'redis'
        ]

    def _get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for docker-compose."""
        db_type = self.spec.get('config', {}).get('database', 'sqlite')
        
        db_configs = {
            'postgresql': {
                'image': 'postgres:13',
                'env': {
                    'POSTGRES_USER': 'postgres',
                    'POSTGRES_PASSWORD': 'postgres', 
                    'POSTGRES_DB': 'app_db'
                }
            },
            'mysql': {
                'image': 'mysql:8.0',
                'env': {
                    'MYSQL_ROOT_PASSWORD': 'root',
                    'MYSQL_DATABASE': 'app_db'
                }
            }
        }
        
        return db_configs.get(db_type, {})

    def _get_database_url(self, db_type: str, for_docker: bool = True) -> str:
        """Get the appropriate database URL for the database type."""
        if for_docker:
            urls = {
                'sqlite': 'sqlite:///./sql_app.db',  # Inside the container
                'postgresql': 'postgresql://postgres:postgres@db:5432/app_db',
                'mysql': 'mysql+mysqlconnector://root:root@db:3306/app_db'
            }
        else:  # For local development, e.g., .env file
            urls = {
                'sqlite': 'sqlite:///./sql_app.db',
                'postgresql': 'postgresql://postgres:postgres@localhost:5432/app_db',
                'mysql': 'mysql+mysqlconnector://root:root@localhost:3306/app_db'
            }
        return urls.get(db_type, urls['sqlite'])
        
    def _template_exists(self, template_name: str) -> bool:
        """Check if a template file exists."""
        return (self.template_path / template_name).exists()
        
    def _write_file(self, relative_path: str, content: str):
        """Write content to a file in the output directory."""
        file_path = self.output_dir / relative_path
        if self.dry_run:
            self.planned_files.append(file_path)
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # For empty __init__.py files from touch()
        if content or not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
        
    def _copy_static_files(self):
        """Copy static files that don't need template processing."""
        static_dir = self._get_template_dir() / 'static'
        if static_dir.exists():
            import shutil
            shutil.copytree(static_dir, self.output_dir, dirs_exist_ok=True)
            
    def _generate_readme(self):
        """Generate README.md file."""
        if self._template_exists('README.md.j2'):
            template = self.template_env.get_template('README.md.j2')
            readme_content = template.render(
                spec=self.spec,
                backend=self.__class__.__name__.replace('Generator', '').lower()
            )
            self._write_file('README.md', readme_content)
            print("✓ Generated README.md")
        
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of what will be generated."""
        return {
            'models': len(self.spec.get('models', [])),
            'endpoints': len(self.spec.get('endpoints', [])),
            'output_directory': str(self.output_dir),
            'backend': self.__class__.__name__.replace('Generator', ''),
            'database': self.spec.get('config', {}).get('database', 'sqlite'),
            'auth_enabled': self.spec.get('config', {}).get('auth_type', 'none') != 'none'
        }