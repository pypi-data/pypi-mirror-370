import os
import jinja2

from typing import Dict, Any, Optional
from pydantic import BaseModel

class Context(BaseModel):
    """
    NOTE: Not used yet
    A context object for rendering templates.

    This class provides a base context that can be extended with additional context data for each render operation.
    """
    
    args: Dict[str, Any]
    env: Dict[str, Any]
    context: Dict[str, Any]

class Jinja2TemplateEngine(object):
    """A Jinja2-based template engine for rendering templates.

    This class provides functionality to render templates using Jinja2, with support for both
    file-based templates and string templates. It maintains a base context that can be extended
    with additional context data for each render operation.

    Attributes:
        template_dir (str): Directory containing template files.
        environment (jinja2.Environment): The Jinja2 environment for template processing.
        context (Dict[str, Any]): Base context dictionary used in all render operations.
    """
    
    def __init__(self, template_dir: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """Initializes the template engine with a template directory and base context.

        Args:
            template_dir (str, optional): Directory path containing template files. If None,
                uses current directory.
            context (Dict[str, Any], optional): Base context dictionary that will be used in
                all render operations. If None, an empty dictionary is used.
        """
        self.template_dir = template_dir or os.path.join(os.getcwd(), 'templates')
        self.environment = self._create_environment()
        self.context = context or {}
        
    def _create_environment(self) -> jinja2.Environment:
        """Creates and configures the Jinja2 environment.

        Returns:
            jinja2.Environment: Configured Jinja2 environment with file system loader and
                default settings.
        """
        # Create a file system loader for the template directory
        loader = jinja2.FileSystemLoader(self.template_dir)
        
        # Create the environment with the loader
        env = jinja2.Environment(
            loader=loader,
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add any custom filters or globals here
        # env.filters['my_filter'] = my_filter_function
        
        return env
    
    def render_template(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Renders a template with the provided context data.

        Args:
            template_name (str): Name of the template file (e.g., 'email.html').
            context (Dict[str, Any], optional): Dictionary of variables to pass to the template.
                These will be merged with the base context.

        Returns:
            str: Rendered template as string.

        Raises:
            jinja2.exceptions.TemplateNotFound: If the template file doesn't exist.
        """
        # Merge the base context with the provided context
        merged_context = {**self.context}
        if context:
            merged_context.update(context)
            
        template = self.environment.get_template(template_name)
        return template.render(**merged_context)
    
    def render_string(self, template_string: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Renders a template string with the provided context data.

        Args:
            template_string (str): String containing Jinja2 template syntax.
            context (Dict[str, Any], optional): Dictionary of variables to pass to the template.
                These will be merged with the base context.

        Returns:
            str: Rendered template as string.
        """
        # Merge the base context with the provided context
        merged_context = {**self.context}
        if context:
            merged_context.update(context)
            
        template = self.environment.from_string(template_string)
        return template.render(**merged_context)
