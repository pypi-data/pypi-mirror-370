import re

class SpecValidator:
    """
    Validates the parsed specification for correctness and best practices.
    """
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _add_error(self, message: str):
        self.errors.append(message)

    def _add_warning(self, message: str):
        self.warnings.append(message)

    def validate(self, spec: dict, spec_content: str) -> bool:
        """Runs all validation checks and returns True if valid."""
        self.errors = []
        self.warnings = []

        models = spec.get('models', [])
        if not models:
            self._add_error("Specification must contain at least one model.")

        self._validate_model_names(models)
        self._validate_models(models)
        self._validate_relationships(models)
        self._validate_sections(spec_content)
        self._validate_auth(spec)

        return not self.has_errors()

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def get_report(self) -> str:
        """Formats errors and warnings into a user-friendly report."""
        report_parts = []
        if self.errors:
            report_parts.append("❌ ERRORS:\n" + "\n".join(f"  • {e}" for e in self.errors))
        if self.warnings:
            report_parts.append("⚠️  WARNINGS:\n" + "\n".join(f"  • {w}" for w in self.warnings))
        return "\n\n".join(report_parts)

    def _validate_model_names(self, models: list):
        names = [model.name for model in models]
        duplicates = {name for name in names if names.count(name) > 1}
        for name in duplicates:
            self._add_error(f"Duplicate model name: '{name}'")

    def _validate_models(self, models: list):
        supported_types = [
            'integer', 'string', 'text', 'boolean', 'datetime', 'float',
            'date', 'time', 'json', 'uuid', 'email', 'url', 'bigint', 'decimal'
        ]
        for model in models:
            if not model.primary_key_name:
                self._add_warning(f"Model '{model.name}' has no primary key field.")
            for field in model.fields:
                if field.name != to_snake_case(field.name):
                    self._add_warning(f"Field '{field.name}' in model '{model.name}' should use snake_case.")
                if field.type not in supported_types:
                    self._add_error(f"Invalid field type '{field.type}' for field '{field.name}' in model '{model.name}'.")

    def _validate_relationships(self, models: list):
        """Validates that relationships point to existing models."""
        model_names = {m.name for m in models}
        for model in models:
            # This now correctly iterates over Relationship objects
            for rel in model.relationships:
                if rel.target_model not in model_names:
                    self._add_error(f"In model '{model.name}', relationship '{rel.name}' points to an undefined model '{rel.target_model}'.")

    def _validate_auth(self, spec: dict):
        """Validates that the spec is correctly configured for authentication."""
        config = spec.get('config', {})
        if config.get('auth_type', 'none') != 'none':
            models = spec.get('models', [])
            user_model = next((m for m in models if m.name == 'User'), None)
            if not user_model:
                self._add_error("Authentication is enabled, but no 'User' model was found in the specification.")
                return

            field_names = {f.name for f in user_model.fields}
            if 'password' not in field_names:
                self._add_error("The 'User' model must have a 'password' field when authentication is enabled.")
            if 'username' not in field_names:
                self._add_error("The 'User' model must have a 'username' field when authentication is enabled.")

            # Check for role field if permissions are used
            endpoints = spec.get('endpoints', [])
            if any(e.permissions for e in endpoints):
                if 'role' not in field_names:
                    self._add_error("Endpoints with 'Permissions' are defined, but the 'User' model is missing a 'role' field.")

    def _validate_sections(self, spec_content: str):
        if "## Data Models" not in spec_content:
            self._add_warning("Missing '## Data Models' section.")

def to_snake_case(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()