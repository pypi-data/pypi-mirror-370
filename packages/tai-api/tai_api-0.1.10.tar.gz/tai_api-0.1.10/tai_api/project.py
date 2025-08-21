"""
Manejo de configuración de proyecto TAI-API
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from tai_sql import pm as sqlpm

class RuntimeMode(str, Enum):
    """Modos de ejecución del proyecto TAI-API"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AuthType(str, Enum):
    """Tipos de autenticación soportados"""
    DATABASE = "database"
    KEYCLOAK = "keycloak"


@dataclass
class DatabaseAuthConfig:
    """Configuración de autenticación basada en base de datos"""
    table_name: str
    username_field: str
    password_field: str
    session_id_field: Optional[str] = None  # Campo opcional para manejar sesiones
    password_expiration_field: Optional[str] = None
    expiration: Optional[int] = 30  # Tiempo de expiración del token en minutos
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseAuthConfig':
        """Crea DatabaseAuthConfig desde diccionario"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte DatabaseAuthConfig a diccionario"""
        return asdict(self)
    
    @property
    def has_session_management(self) -> bool:
        """Verifica si se configuró manejo de sesiones"""
        return self.session_id_field is not None
    
    @property
    def has_password_expiration(self) -> bool:
        """Verifica si se configuró expiración de contraseñas"""
        return self.password_expiration_field is not None


@dataclass
class KeycloakAuthConfig:
    """Configuración de autenticación con Keycloak"""
    server_url: str
    realm: str
    client_id: str
    client_secret: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeycloakAuthConfig':
        """Crea KeycloakAuthConfig desde diccionario"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte KeycloakAuthConfig a diccionario"""
        return asdict(self)


@dataclass
class AuthConfig:
    """Configuración general de autenticación"""
    type: AuthType
    config: Union[DatabaseAuthConfig, KeycloakAuthConfig]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthConfig':
        """Crea AuthConfig desde diccionario"""
        auth_type = AuthType(data['type'])
        
        if auth_type == AuthType.DATABASE:
            config = DatabaseAuthConfig.from_dict(data['config'])
        elif auth_type == AuthType.KEYCLOAK:
            config = KeycloakAuthConfig.from_dict(data['config'])
        else:
            raise ValueError(f"Tipo de autenticación no soportado: {auth_type}")
        
        return cls(type=auth_type, config=config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte AuthConfig a diccionario"""
        return {
            'type': self.type.value,
            'config': self.config.to_dict()
        }


@dataclass
class ProjectConfig:
    """Configuración del proyecto TAI-API"""
    name: str
    namespace: str
    current_version: str = "0.1.0"
    mode: RuntimeMode = RuntimeMode.DEVELOPMENT
    auth: Optional[AuthConfig] = None
    secret_key_name: Optional[str] = 'SECRET_KEY'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Crea ProjectConfig desde diccionario"""
        # Manejar auth como opcional
        auth_data = data.pop('auth', None)
        auth_config = None
        
        if auth_data:
            auth_config = AuthConfig.from_dict(auth_data)
        
        return cls(auth=auth_config, **data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte ProjectConfig a diccionario"""
        result = asdict(self)
        
        # Convertir auth si existe
        if self.auth:
            result['auth'] = self.auth.to_dict()
        
        return result
    
    @property
    def subnamespace(self) -> str:
        """Retorna el namespace del proyecto"""
        return self.namespace.replace('-', '_')

    @property
    def main_namespace(self) -> Path:
        """Retorna el namespace principal del proyecto"""
        return Path(self.namespace) / self.subnamespace

    @property
    def database_namespace(self) -> Path:
        """Retorna el namespace para la base de datos"""
        return Path(self.namespace) / self.subnamespace / "database"
    
    @property
    def diagrams_namespace(self) -> Path:
        """Retorna el namespace para diagramas"""
        return Path(self.namespace) / self.subnamespace / "diagrams"
    
    @property
    def routers_namespace(self) -> Path:
        """Retorna el namespace para routers"""
        return Path(self.namespace) / self.subnamespace / "routers" / "database"

    @property
    def auth_namespace(self) -> Path:
        """Retorna el namespace para autenticación"""
        return Path(self.namespace) / self.subnamespace / "auth"
    
    @property
    def resources_namespace(self) -> Path:
        """Retorna el namespace para respuestas"""
        return Path(self.namespace) / self.subnamespace / "resources"
    
    @property
    def models_import_path(self) -> str:
        """Retorna la ruta de importación para modelos"""
        return f"{self.subnamespace}.database.{sqlpm.db.schema_name}.models"
    
    @property
    def crud_import_path(self) -> str:
        """Retorna la ruta de importación para CRUD"""
        return f"{self.subnamespace}.database.{sqlpm.db.schema_name}.crud.asyn"
    
    @property
    def routers_import_path(self) -> str:
        """Retorna la ruta de importación para routers"""
        return f"{self.subnamespace}.routers.database"
    
    @property
    def resources_import_path(self) -> str:
        """Retorna la ruta de importación para respuestas"""
        return f"{self.subnamespace}.resources"
    
    @property
    def auth_import_path(self) -> str:
        """Retorna la ruta de importación para autenticación"""
        return f"{self.subnamespace}.auth"
    
    @property
    def has_auth(self) -> bool:
        """Verifica si el proyecto tiene configuración de autenticación"""
        return self.auth is not None
    
    @property
    def auth_type(self) -> Optional[AuthType]:
        """Retorna el tipo de autenticación configurado"""
        return self.auth.type if self.auth else None
    
    @property
    def database_auth_config(self) -> Optional[DatabaseAuthConfig]:
        """Retorna la configuración de autenticación de base de datos si existe"""
        if self.auth and self.auth.type == AuthType.DATABASE:
            return self.auth.config
        return None
    
    @property
    def keycloak_auth_config(self) -> Optional[KeycloakAuthConfig]:
        """Retorna la configuración de autenticación de Keycloak si existe"""
        if self.auth and self.auth.type == AuthType.KEYCLOAK:
            return self.auth.config
        return None

class ProjectManager:
    """
    Gestor central de proyectos TAI-API con soporte para múltiples SchemaManager
    """
    
    PROJECT_FILE = '.taiapiproject'

    config: Optional[ProjectConfig] = None
    
    _project_root_cache: Optional[Path] = None

    @classmethod
    def find_project_root(cls, start_path: str = '.') -> Optional[Path]:
        """Busca el directorio raíz del proyecto TAI-API"""
        if cls._project_root_cache is not None:
            return cls._project_root_cache
            
        current_path = Path(start_path).resolve()

        # Buscar en el directorio actual y subcarpetas
        for dir_path in [current_path] + [p for p in current_path.rglob("*") if p.is_dir()]:
            project_file = dir_path / cls.PROJECT_FILE
            if project_file.exists():
                cls._project_root_cache = dir_path
                return dir_path
        
        return None
    
    @classmethod
    def clear_cache(cls) -> None:
        """Limpia toda la caché del ProjectManager"""
        cls._project_root_cache = None
        cls.config = None

    @classmethod
    def get_project_config(cls) -> Optional[ProjectConfig]:
        """Obtiene la configuración del proyecto con caché"""
        if cls.config is None:
            cls.load_config()
        return cls.config

    @classmethod
    def create_config(cls, name: str, namespace: str, current_version: str = '0.1.0') -> ProjectConfig:
        """Crea un nuevo proyecto con configuración inicial"""
        config = ProjectConfig(
            name=name,
            namespace=namespace,
            current_version=current_version,
        )
        
        cls.save_config(config, Path(namespace))
        return config
    
    @classmethod
    def load_config(cls, project_root: Optional[Path] = None) -> Optional[ProjectConfig]:
        """Carga la configuración del proyecto"""

        if cls.config is not None:
            return cls.config
        
        if project_root is None:
            project_root = cls.find_project_root()
        
        if not project_root:
            return None
        
        project_file = project_root / cls.PROJECT_FILE
        
        if not project_file.exists():
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                config = ProjectConfig.from_dict(data)

            cls.config = config  # Guardar en caché
            
            return config
        
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Error al leer {cls.PROJECT_FILE}: {e}")
    
    @classmethod
    def save_config(cls, config: ProjectConfig, project_root: Path) -> None:
        """Guarda la configuración del proyecto"""
        project_file = project_root / cls.PROJECT_FILE
        
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            cls.config = config  # Actualizar caché
        
        except Exception as e:
            raise ValueError(f"Error al escribir {cls.PROJECT_FILE}: {e}")
    
    @classmethod
    def update_config(cls, project_root: Path, **updates) -> ProjectConfig:
        """Actualiza la configuración del proyecto"""
        config = cls.load_config(project_root)
        
        if not config:
            raise ValueError("No se encontró configuración de proyecto")
        
        # Actualizar campos
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        cls.save_config(config, project_root)

        return config
    
    @classmethod
    def update_auth_config(cls, auth_config: AuthConfig, project_root: Optional[Path] = None) -> ProjectConfig:
        """Actualiza específicamente la configuración de autenticación"""
        if project_root is None:
            project_root = cls.find_project_root()
        
        if not project_root:
            raise ValueError("No se encontró la raíz del proyecto")
        
        config = cls.load_config(project_root)
        
        if not config:
            raise ValueError("No se encontró configuración de proyecto")
        
        config.auth = auth_config
        cls.save_config(config, project_root)
        
        return config
    
    @classmethod
    def get_project_info(cls) -> Dict[str, Any]:
        """Obtiene información completa del proyecto"""
        config = cls.get_project_config()
        project_root = cls.find_project_root()
        
        info = {
            'project_root': str(project_root) if project_root else None,
            'config': config.to_dict() if config else None
        }
        
        return info
    