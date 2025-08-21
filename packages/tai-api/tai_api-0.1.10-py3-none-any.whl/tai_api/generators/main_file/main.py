from pathlib import Path
from typing import ClassVar
import jinja2
from tai_sql.generators import BaseGenerator
from tai_api import pm, AuthType

class MainFileGenerator(BaseGenerator):
    """
    Generador del archivo __main__.py principal.
    
    Este generador crea el archivo __main__.py basándose en el estado actual
    del proyecto, incluyendo automáticamente las funcionalidades disponibles.
    """

    _jinja_env: ClassVar[jinja2.Environment] = None
    
    def __init__(self, output_dir: str = 'api/api'):
        """
        Inicializa el generador del archivo principal.
        
        Args:
            project_config: Configuración del proyecto
        """
        super().__init__(output_dir)

    @property
    def jinja_env(self) -> jinja2.Environment:
        """Retorna el entorno Jinja2 configurado"""
        if self._jinja_env is None:
            templates_dir = Path(__file__).parent / "templates"
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(templates_dir.as_posix()),
                trim_blocks=True,
                lstrip_blocks=True
            )
        return self._jinja_env
    
    def generate(self) -> str:
        """
        Genera el archivo __main__.py basándose en la configuración del proyecto.
            
        Returns:
            str: Ruta del archivo generado
        """
        
        # Obtener template apropiado
        prod_template_name, dev_template_name, with_mcp = self.select_template()
        
        # Renderizar template
        prod_template = self.jinja_env.get_template(prod_template_name)
        dev_template = self.jinja_env.get_template(dev_template_name)
        
        operations = []
        if with_mcp:
            for model in self.models:
                operations.extend([f"{ model.tablename }_find_many", f"{ model.tablename }_find"])

        context = {
            "project_name": pm.config.name if pm.config else "TAI API",
            "version": pm.config.current_version if pm.config else "0.1.0",
            "routers_import_path": pm.config.routers_import_path,
            "resources_import_path": pm.config.resources_import_path,
            "auth_import_path": pm.config.auth_import_path if pm.config.auth else None,
            "operations": operations,
        }
        prod_content = prod_template.render(**context)
        dev_content = dev_template.render(**context)
        
        # Escribir archivo
        prod_output_path = Path(self.config.output_dir) / "__main__.py"
        prod_output_path.parent.mkdir(parents=True, exist_ok=True)

        dev_output_path = Path(self.config.output_dir) / "__dev__.py"
        dev_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(prod_output_path, "w", encoding="utf-8") as f:
            f.write(prod_content)
        
        with open(dev_output_path, "w", encoding="utf-8") as f:
            f.write(dev_content)
        
        return str(prod_output_path)
    
    def select_template(self) -> tuple[str, str]:
        """
        Selecciona el template apropiado basándose en el estado del proyecto.
        
        Args:
            state: Estado del proyecto
            
        Returns:
            str: Nombre del template a usar
        """
        has_auth = pm.config.auth is not None and pm.config.auth.type == AuthType.DATABASE

        location = pm.config.routers_namespace
        has_routers = False
        if location.exists():
            if location.is_file():
                has_routers = True
            elif location.is_dir() and any(location.glob("*.py")):
                has_routers = True
        
        prod_template = ''
        dev_template = ''
        with_mcp = False

        if has_auth and has_routers:
            prod_template = "__main__.py.j2"  # Completo - auth + routers
            dev_template = "__main__generate.py.j2"
            with_mcp = True
        elif has_auth:
            prod_template = "__main__setdbauth.py.j2"  # Solo auth
            dev_template = "__main__init.py.j2"
        elif has_routers:
            prod_template = dev_template = "__main__generate.py.j2"  # Solo routers generados
            with_mcp = True
        else:
            prod_template = dev_template = "__main__init.py.j2"  # Solo básico

        return prod_template, dev_template, with_mcp