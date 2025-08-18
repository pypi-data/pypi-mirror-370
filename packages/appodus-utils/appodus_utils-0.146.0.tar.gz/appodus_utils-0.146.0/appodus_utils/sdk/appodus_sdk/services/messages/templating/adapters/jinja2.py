import os
from typing import Dict, Any, Optional

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from kink import inject

from appodus_utils import Utils
from appodus_utils.config.settings import TemplatingEngine
from appodus_utils.exception.exceptions import TemplateRenderingException
from appodus_utils.sdk.appodus_sdk.services.messages.templating.interface import ITemplateEngineProvider


@inject
class Jinja2ITemplateEngineProvider(ITemplateEngineProvider):
    def __init__(self):
        self.BASE_URL = Utils.get_from_env_fail_if_not_exists('BASE_DIR')
        self.MESSAGE_TEMPLATE_DIR = Utils.get_from_env_fail_if_not_exists('MESSAGE_TEMPLATE_DIR')

        self.template_dir = Path(f"{self.BASE_URL}/{self.MESSAGE_TEMPLATE_DIR}")

        self.env = self._create_environment()

        super().__init__()

    @property
    def template_engine(self) -> TemplatingEngine:
        return TemplatingEngine.JINJA2

    @property
    def template_extension(self) -> str:
        return "jinja2"

    def _create_environment(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            raise TemplateRenderingException(f"Template not found: {template_name}")
        except Exception as e:
            raise TemplateRenderingException(f"Template rendering failed: {str(e)}")

    def supports_template(self, template_name: str) -> bool:
        """
        Check if the specified template is available in the environment.
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
