"""
Phase 4 CLI commands for multi-file project generation and enhanced git workflows.
"""

import click
from ..tools import get_tool


def add_generate_commands(cli):
    """Add Phase 4 generate commands to the CLI."""
    
    @cli.group()
    def generate():
        """Generate projects, features, and multiple files."""
        pass
    
    @generate.command()
    @click.argument('description')
    @click.option('--type', '-t', type=click.Choice(['python-api', 'react-app', 'fullstack']), 
                  help='Project type to generate')
    @click.option('--name', '-n', help='Project name (default: extracted from description)')
    def project(description, type, name):
        """Generate complete project with multiple files from description.
        
        Examples:
          metis generate project "FastAPI backend with database"
          metis generate project "React frontend application" --type react-app
          metis generate project "Full-stack e-commerce platform" --name my-shop
        """
        try:
            # Get the enhanced project generator tool
            generator_class = get_tool("EnhancedProjectGeneratorTool")
            if not generator_class:
                click.echo("+ Error: EnhancedProjectGeneratorTool not available", err=True)
                return
            
            # Instantiate the tool
            generator = generator_class()
            
            # Build query with options
            query = description
            if type:
                query = f"{type} {query}"
            if name:
                query = f"{query} named {name}"
            
            click.echo(f"+ Generating project: {description}")
            if type:
                click.echo(f"+ Project type: {type}")
            if name:
                click.echo(f"+ Project name: {name}")
            
            # Execute project generation
            result = generator.execute(query)
            
            if result.get("success"):
                click.echo(f"+ Project '{result['project_name']}' generated successfully!")
                click.echo(f"+ Type: {result['project_type']}")
                click.echo(f"+ Files created: {result['files_created']}")
                click.echo(f"+ Directories created: {result['directories_created']}")
                
                if result.get("features"):
                    click.echo(f"+ Features: {', '.join(result['features'])}")
                
                click.echo(f"+ Location: {result['project_path']}")
                
                # Show next steps
                click.echo("\n+ Next steps:")
                for step in result.get("next_steps", []):
                    click.echo(f"  - {step}")
                
                # Show some created files
                if result.get("files"):
                    click.echo("\n+ Key files created:")
                    for file_info in result["files"][:5]:  # Show first 5 files
                        click.echo(f"  - {file_info['path']}")
                    if len(result["files"]) > 5:
                        click.echo(f"  ... and {len(result['files']) - 5} more files")
                
            else:
                click.echo(f"- Error generating project: {result.get('error')}", err=True)
                if result.get("suggestions"):
                    click.echo("+ Try these alternatives:")
                    for suggestion in result["suggestions"]:
                        click.echo(f"  - {suggestion}")
                        
        except Exception as e:
            click.echo(f"- Error: {str(e)}", err=True)
    
    @generate.command()
    @click.argument('description')
    @click.option('--framework', '-f', help='Framework to use (e.g., fastapi, react, django)')
    def feature(description, framework):
        """Generate feature with multiple related files.
        
        Examples:
          metis generate feature "user authentication system"
          metis generate feature "payment processing" --framework fastapi
          metis generate feature "shopping cart component" --framework react
        """
        click.echo(f"+ Generating feature: {description}")
        if framework:
            click.echo(f"+ Framework: {framework}")
        
        # TODO: Implement MultiFileCodeGeneratorTool
        click.echo("+ Feature generation coming in next Phase 4 release!")
        click.echo("+ Currently supports: metis generate project")
    
    @generate.command()
    @click.argument('name')
    @click.option('--endpoints', '-e', multiple=True, help='API endpoints to generate')
    def api(name, endpoints):
        """Generate API with models, routes, and tests.
        
        Examples:
          metis generate api users
          metis generate api products --endpoints create,read,update,delete
          metis generate api orders --endpoints list,get,create
        """
        click.echo(f"+ Generating API: {name}")
        if endpoints:
            click.echo(f"+ Endpoints: {', '.join(endpoints)}")
        
        # TODO: Implement API generation
        click.echo("+ API generation coming in next Phase 4 release!")
        click.echo("+ Currently supports: metis generate project")
    
    @generate.command()
    @click.argument('name')
    @click.option('--style', '-s', type=click.Choice(['functional', 'class']), 
                  default='functional', help='Component style')
    def component(name, style):
        """Generate React component with styles and tests.
        
        Examples:
          metis generate component UserProfile
          metis generate component Dashboard --style class
          metis generate component PaymentForm --style functional
        """
        click.echo(f"+ Generating component: {name}")
        click.echo(f"+ Style: {style}")
        
        # TODO: Implement component generation
        click.echo("+ Component generation coming in next Phase 4 release!")
        click.echo("+ Currently supports: metis generate project")
    
    @generate.command()
    @click.argument('model')
    @click.option('--db', type=click.Choice(['sqlite', 'postgresql', 'mysql']), 
                  default='sqlite', help='Database type')
    def crud(model, db):
        """Generate full CRUD operations across multiple files.
        
        Examples:
          metis generate crud User
          metis generate crud Product --db postgresql  
          metis generate crud Order --db mysql
        """
        click.echo(f"+ Generating CRUD for: {model}")
        click.echo(f"+ Database: {db}")
        
        # TODO: Implement CRUD generation
        click.echo("+ CRUD generation coming in next Phase 4 release!")
        click.echo("+ Currently supports: metis generate project")
