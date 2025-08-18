import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

# --- Helper Functions for Naming Conventions ---

def to_snake_case(name: str) -> str:
    """Converts a PascalCase or CamelCase string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def pluralize(name: str) -> str:
    """A simple pluralization helper for snake_case names."""
    if name.endswith('y'):
        return name[:-1] + 'ies'
    if name.endswith('s'):
        return name + 'es'
    return name + 's'

# --- Data Structures for Parsed Specification ---

@dataclass
class Field:
    """Represents a single field in a data model."""
    name: str
    type: str
    sqlalchemy_type: str
    options: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    is_foreign_key: bool = False
    foreign_key_to: str | None = None

@dataclass
class Relationship:
    """Represents a SQLAlchemy relationship between models."""
    name: str              # The name of the relationship attribute, e.g., "author"
    target_model: str      # The class name of the target model, e.g., "User"
    back_populates: str    # The corresponding attribute on the target model, e.g., "posts"
    is_list: bool          # True for a one-to-many relationship

@dataclass
class Model:
    """Represents a data model with various name casings."""
    name: str              # Original name from spec, e.g., "User"
    name_pascal: str       # PascalCase, e.g., "User"
    name_snake: str        # snake_case, e.g., "user"
    name_plural_snake: str # plural_snake_case, e.g., "users"
    fields: List[Field] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    primary_key_name: str | None = None
    primary_key_type: str | None = None
    description: str = ""

@dataclass
class Endpoint:
    """Represents an API endpoint (placeholder for future expansion)."""
    path: str
    method: str
    description: str = ""
    permissions: str | None = None

class SpecParser:
    """Parses a Markdown specification into a structured dictionary."""
    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines()

    def parse(self) -> Dict[str, Any]:
        """Executes the parsing process by iterating through sections."""
        title = "Untitled API"
        models: List[Model] = []
        endpoints: List[Endpoint] = []
        
        section_lines: Dict[str, List[str]] = {}
        current_section: str | None = None

        # First, group lines by section
        for line in self.lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## '):
                current_section = line[3:].strip().lower()
                section_lines[current_section] = []
            elif current_section and line.strip():
                section_lines[current_section].append(line)
        
        # Now parse each section's lines
        if 'data models' in section_lines:
            models = self._parse_models_from_lines(section_lines['data models'])
            self._resolve_relationships(models)
        
        if 'endpoints' in section_lines:
            endpoints = self._parse_endpoints_from_lines(section_lines['endpoints'])

        return {
            "title": title,
            "models": models,
            "endpoints": endpoints,
        }

    def _get_sqlalchemy_type(self, field_type: str, options: Dict[str, Any]) -> str:
        """Maps a spec type to a SQLAlchemy type string."""
        type_map = {
            'integer': 'Integer',
            'string': f"String({options.get('max_length', 255)})",
            'text': 'Text',
            'boolean': 'Boolean',
            'datetime': 'DateTime(timezone=True)',
            'float': 'Float',
            'date': 'Date',
            'time': 'Time',
            'json': 'JSON',
            'uuid': 'UUID(as_uuid=True)'
        }
        return type_map.get(field_type, 'String')

    def _parse_models_from_lines(self, lines: List[str]) -> List[Model]:
        models: List[Model] = []
        current_model: Model | None = None

        for line in lines:
            line = line.strip()
            if not line: continue

            if model_match := re.match(r'###\s+([a-zA-Z0-9_]+)', line):
                if current_model: models.append(current_model)
                model_name = model_match.group(1)
                snake_name = to_snake_case(model_name)
                current_model = Model(
                    name=model_name,
                    name_pascal=model_name,
                    name_snake=snake_name,
                    name_plural_snake=pluralize(snake_name)
                )
            elif field_match := re.match(r'-\s+([a-zA-Z0-9_]+):\s+([a-zA-Z0-9_]+)(?:\s+\((.*)\))?', line):
                if current_model:
                    name, type, options_str = field_match.groups()
                    options = {}
                    if options_str:
                        for part in options_str.split(','):
                            key, _, val = part.strip().partition(':')
                            options[key.strip()] = val.strip() if val else True
                    
                    field_obj = Field(
                        name=name, 
                        type=type, 
                        options=options,
                        sqlalchemy_type=self._get_sqlalchemy_type(type, options)
                    )

                    if 'foreign_key' in options:
                        field_obj.is_foreign_key = True
                        field_obj.foreign_key_to = options['foreign_key']

                    if 'primary_key' in options:
                        current_model.primary_key_name = name
                        current_model.primary_key_type = type

                    current_model.fields.append(field_obj)
        
        if current_model: models.append(current_model)
        return models

    def _resolve_relationships(self, models: List[Model]):
        """Second pass to build relationship attributes based on foreign keys."""
        model_map = {m.name: m for m in models}
        for model in models:
            for f in model.fields:
                if f.is_foreign_key and f.foreign_key_to:
                    target_model_name, _ = f.foreign_key_to.split('.')
                    if target_model_name in model_map:
                        target_model = model_map[target_model_name]
                        rel_name = f.name.replace('_id', '')
                        back_pop_name = pluralize(model.name_snake)
                        model.relationships.append(Relationship(rel_name, target_model_name, back_pop_name, False))
                        target_model.relationships.append(Relationship(back_pop_name, model.name, rel_name, True))

    def _parse_endpoints_from_lines(self, lines: List[str]) -> List[Endpoint]:
        endpoints: List[Endpoint] = []
        current_endpoint: Endpoint | None = None

        for line in lines:
            line = line.strip()
            if not line: continue

            if endpoint_match := re.match(r'###\s+([A-Z]+)\s+([/\w{}.-]+)', line):
                if current_endpoint: endpoints.append(current_endpoint)
                method, path = endpoint_match.groups()
                current_endpoint = Endpoint(method=method, path=path)
            
            elif desc_match := re.match(r'-\s+Description:\s+(.*)', line, re.IGNORECASE):
                if current_endpoint:
                    current_endpoint.description = desc_match.group(1).strip()
            elif perm_match := re.match(r'-\s+Permissions?:\s+(.*)', line, re.IGNORECASE):
                if current_endpoint:
                    current_endpoint.permissions = perm_match.group(1).strip()
        
        if current_endpoint: endpoints.append(current_endpoint)
        return endpoints