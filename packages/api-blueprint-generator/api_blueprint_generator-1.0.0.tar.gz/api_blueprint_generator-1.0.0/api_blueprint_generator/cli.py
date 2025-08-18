# File: cli.py (enhanced version)
import click
import yaml
import sys
from pathlib import Path

import frontmatter
from api_blueprint_generator.generators.fastapi_generator import FastAPIGenerator
from api_blueprint_generator.parser import SpecParser
from api_blueprint_generator.generators.flask_generator import FlaskGenerator
from api_blueprint_generator.utils import load_config
from api_blueprint_generator.validation import SpecValidator

@click.group()
def cli():
    """API Blueprint Generator - Generate APIs from Markdown specifications."""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='./generated_api', help='Output directory')
@click.option('--backend', '-b', type=click.Choice(['flask', 'fastapi']), help='Backend framework')
@click.option('--database', '-d', type=click.Choice(['sqlite', 'postgresql', 'mysql']), help='Database type')
@click.option('--auth', type=click.Choice(['none', 'jwt', 'session']), help='Authentication type')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.option('--template-dir', type=click.Path(exists=True), help='Path to custom templates directory.')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating files')
def generate(spec_file, output, backend, database, auth, config, overwrite, template_dir, dry_run):
    """Generate API from specification file."""

    # Parse specification file with front matter
    try:
        post = frontmatter.load(spec_file)
        spec_content = post.content
        user_config = post.metadata
    except Exception as e:
        click.echo(click.style(f"Error reading or parsing front matter from {spec_file}: {e}", fg='red'), err=True)
        sys.exit(1)

    # Load external configuration if provided, and merge it (external file takes precedence)
    if config:
        external_config = load_config(config)
        user_config.update(external_config)

    # Override config with CLI options (CLI takes highest precedence)
    if backend: user_config['backend'] = backend
    if database: user_config['database'] = database
    if auth: user_config['auth_type'] = auth

    # Ensure essential config keys exist from a default blueprint.yml if no other source is found
    if not user_config:
        user_config = load_config()

    # Parse the main markdown content
    try:
        parser = SpecParser(spec_content)
        spec = parser.parse()
    except Exception as e:
        click.echo(click.style(f"Error parsing specification: {e}", fg='red'), err=True)
        sys.exit(1)

    # --- New Validation Step ---
    validator = SpecValidator()
    if not validator.validate(spec, spec_content):
        click.echo(click.style("\nValidation failed. Please fix the following issues in your spec file:", fg='red'))
        click.echo(validator.get_report())
        sys.exit(1)
    elif validator.has_warnings():
        click.echo(click.style("\nValidation passed with warnings:", fg='yellow'))
        click.echo(validator.get_report())
        if not click.confirm("\nDo you want to continue with generation anyway?"):
            click.echo("Generation cancelled.")
            return
    
    # Add config to spec
    spec['config'] = user_config
    
    # Check if output directory exists
    output_path = Path(output)
    if output_path.exists() and not overwrite:
        if not click.confirm(f"Directory '{output}' already exists. Continue?"):
            return
    
    # Select generator
    try:
        if user_config['backend'] == 'flask':
            generator = FlaskGenerator(spec, output, template_dir=template_dir, dry_run=dry_run)
        elif user_config['backend'] == 'fastapi':
            generator = FastAPIGenerator(spec, output, template_dir=template_dir, dry_run=dry_run)
        else:
            click.echo(click.style(f"Error: Backend '{user_config['backend']}' is not supported.", fg='red'), err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error initializing generator: {e}", fg='red'), err=True)
        sys.exit(1)

    # Show generation summary
    summary = generator.get_generation_summary()
    
    click.echo("\n" + "="*50)
    click.echo("🚀 API Blueprint Generator")
    click.echo("="*50)
    click.echo(f"📁 Output: {summary['output_directory']}")
    click.echo(f"🔧 Backend: {summary['backend']}")
    click.echo(f"🗄️  Database: {summary['database']}")
    click.echo(f"📊 Models: {summary['models']}")
    click.echo(f"🛣️  Endpoints: {summary['endpoints']}")
    click.echo(f"🔐 Auth: {'Enabled' if summary['auth_enabled'] else 'Disabled'}")
    
    if dry_run:
        click.echo("\n🔍 Dry run mode - no files will be created.")
        # The generator now handles the dry run logic and returns the planned files
        planned_files = generator.generate()
        if planned_files:
            click.echo("\nThe following files and directories would be created:")
            for file_path in planned_files:
                relative_path = file_path.relative_to(Path(output).parent)
                click.echo(f"  - {relative_path}")
            
        return
    
    # Generate the API
    if not click.confirm("\nProceed with generation?"):
        click.echo("Generation cancelled.")
        return
        
    try:
        generator.generate()
        
        click.echo("\n" + "="*50)
        click.echo(click.style("✅ Generation completed successfully!", fg='green', bold=True))
        click.echo("="*50)
        
        # Show next steps
        click.echo("\n📋 Next steps:")
        click.echo(f"1. cd {output}")
        click.echo("2. cp .env.example .env")
        click.echo("3. Edit .env with your configuration")
        click.echo("4. docker-compose up --build")
        click.echo("5. Open http://localhost:8000/docs")
        
    except Exception as e:
        click.echo(click.style(f"❌ Generation failed: {e}", fg='red'), err=True)

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
def validate(spec_file):
    """Validate a specification file using the advanced validator."""
    click.echo(f"🔍 Validating specification file: {spec_file}")
    try:
        spec_content = Path(spec_file).read_text()
        parser = SpecParser(spec_content)
        spec = parser.parse()
        
        validator = SpecValidator()
        validator.validate(spec, spec_content)
        
        click.echo("\n" + "="*50)
        click.echo("📊 Validation Report")
        click.echo("="*50)
        click.echo(validator.get_report())
        
        if validator.has_errors():
            click.echo(click.style("\nValidation failed.", fg='red'))
            sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ An unexpected error occurred during validation: {e}", fg='red'), err=True)
        sys.exit(1)

@cli.command()
@click.option('--output', '-o', default='blueprint.yml', help='Output config file')
def init(output):
    """Initialize a new blueprint configuration file."""
    
    config = {
        'backend': click.prompt('Backend framework', 
                              type=click.Choice(['flask', 'fastapi']), 
                              default='fastapi'),
        'database': click.prompt('Database type', 
                               type=click.Choice(['sqlite', 'postgresql', 'mysql']), 
                               default='sqlite'),
        'auth_type': click.prompt('Authentication type', 
                                type=click.Choice(['none', 'jwt', 'session']), 
                                default='jwt'),
        'cors_enabled': click.confirm('Enable CORS?', default=True),
        'rate_limiting': click.confirm('Enable rate limiting?', default=False),
        'include_tests': click.confirm('Generate tests?', default=True),
        'docker_setup': click.confirm('Generate Docker files?', default=True),
        'api_prefix': click.prompt('API prefix', default='/api/v1'),
        'background_tasks': click.confirm('Enable background tasks (Celery & Redis)?', default=False)
    }
    
    with open(output, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    click.echo(f"✅ Configuration saved to {output}")
    click.echo("Edit this file and use with: blueprint generate spec.md -c blueprint.yml")

@cli.command() 
def templates():
    """Show information about available templates."""
    templates_dir = Path(__file__).parent / 'templates'
    
    click.echo("📋 Available Templates:")
    click.echo("="*30)
    
    if (templates_dir / 'fastapi').exists():
        click.echo("🚀 FastAPI Templates:")
        fastapi_templates = list((templates_dir / 'fastapi').glob('*.j2'))
        for template in sorted(fastapi_templates):
            click.echo(f"  • {template.name}")
    
    if (templates_dir / 'flask').exists():
        click.echo("\n🌶️  Flask Templates:")
        flask_templates = list((templates_dir / 'flask').glob('*.j2'))
        for template in sorted(flask_templates):
            click.echo(f"  • {template.name}")

@cli.command()
@click.argument('template_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
def copy_templates(template_dir, output_dir):
    """Copy templates to customize them."""
    import shutil
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    shutil.copytree(template_dir, output_path, dirs_exist_ok=True)
    click.echo(f"✅ Templates copied to {output_dir}")
    click.echo("Edit templates and use with: blueprint generate spec.md --template-dir custom-templates")

@cli.command()
def version():
    """Show version information."""
    click.echo("API Blueprint Generator v1.0.0")
    click.echo("Generate production-ready APIs from Markdown specifications")

if __name__ == '__main__':
    cli()