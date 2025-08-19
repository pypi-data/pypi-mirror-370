from abc import abstractmethod, ABC
from typing import Dict, Any

from appodus_utils.config.settings import TemplatingEngine


class ITemplateEngineProvider(ABC):
    """Abstract base class for all template engines"""

    @property
    @abstractmethod
    def template_engine(self) -> TemplatingEngine:
        pass

    @property
    @abstractmethod
    def template_extension(self) -> str:
        pass

    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        pass

    @abstractmethod
    def supports_template(self, template_name: str) -> bool:
        """Check if template exists in the engine"""
        pass
