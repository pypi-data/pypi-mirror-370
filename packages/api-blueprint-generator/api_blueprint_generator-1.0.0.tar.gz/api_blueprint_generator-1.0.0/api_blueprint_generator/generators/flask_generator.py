from pathlib import Path
from typing import Dict, Any, List
from .base_generator import BaseGenerator

class FlaskGenerator(BaseGenerator):
    def __init__(self, spec: Dict[str, Any], output_dir: str, template_dir: str = None):
        super().__init__(spec, output_dir, template_dir)
        self._setup_flask_specifics()

    def _get_template_dir(self) -> Path:
        """Get the directory containing Flask templates."""
        return Path(__file__).parent.parent / 'templates' / 'flask'

    def _setup_flask_specifics(self):
        """Initialize Flask-specific configurations."""
        pass  # Placeholder for any flask-specific setup

    def generate(self):
        """Generate Flask project with enhanced features."""
        print(f"🌶️  Generating Flask project...")
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
        """Get Flask-specific requirements."""
        reqs = [
            'Flask',
            'Flask-SQLAlchemy',
            'Flask-Migrate',
            'Flask-Cors',
        ]
        if self.spec.get('config', {}).get('auth_type') == 'jwt':
            reqs.append('Flask-JWT-Extended')
        return reqs

    def _generate_routes(self):
        """Generate Flask Blueprints for each model."""
        if not self.spec.get('models'):
            return

        routes_dir = self.output_dir / 'app' / 'routes'
        routes_dir.mkdir(exist_ok=True)

        # Generate individual blueprint files for each model
        for model in self.spec['models']:
            self._generate_model_blueprint(model)

        # Generate auth routes if auth is enabled
        if self.spec.get('config', {}).get('auth_type', 'none') != 'none':
            self._generate_auth_routes()

        print(f"✓ Generated Blueprints for {len(self.spec['models'])} models")

    def _generate_model_blueprint(self, model: Any):
        """Generate CRUD routes for a specific model as a Blueprint."""
        if not self._template_exists('model_routes.py.j2'):
            print(f"⚠️  Warning: Template 'model_routes.py.j2' not found for Flask. Skipping route generation for {model.name}.")
            return

        template = self.template_env.get_template('model_routes.py.j2')
        auth_enabled = self.spec.get('config', {}).get('auth_type', 'none') != 'none'

        routes_code = template.render(
            model=model,
            auth_enabled=auth_enabled
        )

        self._write_file(f"app/routes/{model.name_snake}_routes.py", routes_code)

    def _generate_auth_routes(self):
        """Generate authentication routes as a Blueprint."""
        if self._template_exists('auth_routes.py.j2'):
            template = self.template_env.get_template('auth_routes.py.j2')
            auth_code = template.render()
            self._write_file('app/routes/auth_routes.py', auth_code)
            print("✓ Generated auth_routes.py")

    def _generate_main_app(self):
        """Generate the main Flask application file using an app factory."""
        if not self._template_exists('__init__.py.j2'):
            return

        template = self.template_env.get_template('__init__.py.j2')

        # Collect all blueprints to register
        blueprints = []
        for model in self.spec.get('models', []):
            blueprints.append({
                'name': f"{model.name_snake}_bp",
                'module': f".routes.{model.name_snake}_routes",
                'url_prefix': f"{self.spec.get('config', {}).get('api_prefix', '/api/v1')}/{model.name_plural_snake}"
            })

        auth_enabled = self.spec.get('config', {}).get('auth_type', 'none') != 'none'
        if auth_enabled:
            blueprints.append({
                'name': 'auth_bp',
                'module': '.routes.auth_routes',
                'url_prefix': '/auth'
            })

        init_code = template.render(blueprints=blueprints)
        self._write_file('app/__init__.py', init_code)
        print("✓ Generated app/__init__.py (app factory)")