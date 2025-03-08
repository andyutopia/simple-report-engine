import json
import os
import zipfile
from types import SimpleNamespace
from pydantic import BaseModel
from report_logger import logger  # Assuming you have a logger set up
from constants import TEMPLATE_DIR
from jinja2 import Environment, FileSystemLoader

class RecursiveNamespace(SimpleNamespace):
    """
    A subclass of SimpleNamespace that recursively converts dictionaries and lists of dictionaries
    into RecursiveNamespace instances, allowing for attribute-style access to nested data structures.
    """
    @staticmethod
    def map_entry(entry):
        if isinstance(entry, dict):
            return RecursiveNamespace(**entry)
        return entry

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, val in kwargs.items():
            if type(val) == dict:
                setattr(self, key, RecursiveNamespace(**val))
            elif type(val) == list:
                setattr(self, key, list(map(self.map_entry, val)))

class TemplateContent(BaseModel):
    html_content: str
    style_content: str | None
    options: dict | None

class TemplateInstance:
    """
    A class that represents a template instance with a name and associated CSS file.
    """

    name: str = None
    content: TemplateContent = None
    jinja2_env = None

    def __init__(self, name, content=None):
        self.name = name
        self.content = content

    def is_loaded(self) -> bool:
        return self.content is not None

    def init_env(self):
        if not self.jinja2_env:
            self.jinja2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def render_content(self, template_data) -> TemplateContent:
        if not self.is_loaded():
            logger.error('Template instance is not loaded.')
            return None
        
        self.init_env()
        return TemplateContent(
            html_content=self.jinja2_env.from_string(self.content.html_content).render(**template_data),
            style_content=self.jinja2_env.from_string(self.content.style_content).render(**template_data),
            options=self.content.options
        )        

    @staticmethod
    def load(path, debug=False):
        """
        Load the template content from the specified path.
        If debug is True, load folder content. Otherwise, load the zip file of the path.
        Return an error if it has an error.
        """
        content = None
        filenames = {
            'html': 'template.html',
            'css': 'style.css',
            'options': 'options.json'
        }

        def load_file(file_path):
            with open(file_path, 'r') as file:
                return file.read()
            
        def load_zipfile(zip_file, file_path):
            with zip_file.open(file_path) as file:
                return file.read().decode('utf-8')

        try:
            if not debug:
                # Load zip file content
                with zipfile.ZipFile(path, 'r') as zip_file:
                    is_exists = {i:bool(j in zip_file.namelist()) for i,j in filenames.items()}
                    if not is_exists.get('html'):
                        raise FileNotFoundError(f"Template file not found in zip: {filenames.get('html')}")
                    content = TemplateContent(
                        html_content=load_zipfile(zip_file, filenames.get('html')),
                        style_content=load_zipfile(zip_file, filenames.get('css')) if is_exists.get('css') else None,
                        options=json.loads(load_zipfile(zip_file, filenames.get('options'))) if is_exists.get('options') else None
                    )
            else:
                is_exists = {i:os.path.exists(os.path.join(path, j)) for i,j in filenames.items()}
                if not is_exists.get('html'):
                    raise FileNotFoundError(f"Template file not found in folder: {filenames.get('html')}")
                content = TemplateContent(
                    html_content=load_file(os.path.join(path, filenames.get('html'))),
                    style_content=load_file(os.path.join(path, filenames.get('css'))) if is_exists.get('css') else None,
                    options=json.loads(load_file(os.path.join(path, filenames.get('options')))) if is_exists.get('options') else None
                )
        except Exception as e:
            error_message = f"Error loading template from {path}: {str(e)}"
            logger.error(error_message)
            return None

        return TemplateInstance(name=os.path.basename(path), content=content)
