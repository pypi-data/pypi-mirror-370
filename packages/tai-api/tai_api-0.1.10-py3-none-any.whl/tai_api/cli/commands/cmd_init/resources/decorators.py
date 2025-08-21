"""
Decoradores para mejorar la documentación automática de endpoints que usan APIResponse.

Este módulo proporciona decoradores que enriquecen la documentación de OpenAPI
para endpoints que utilizan APIResponse o PaginatedResponse, facilitando la
comprensión de las estructuras de respuesta por parte de LLMs y herramientas MCP.
"""

from functools import wraps
from typing import get_args, get_origin, Any, Dict, Optional, Type
import inspect
from pydantic import BaseModel


def document_api_response(
    success_description: str = "Operación exitosa",
    data_description: Optional[str] = None,
    include_examples: bool = True,
    custom_examples: Optional[Dict[str, Any]] = None
):
    """
    Decorador para mejorar la documentación de endpoints que usan APIResponse.
    
    Este decorador extrae información del tipo genérico de APIResponse y 
    enriquece la documentación de OpenAPI para que los LLMs y herramientas
    puedan entender mejor la estructura de las respuestas.
    
    Args:
        success_description: Descripción para respuestas exitosas
        data_description: Descripción específica para el campo 'data'
        include_examples: Si incluir ejemplos automáticos en la documentación
        custom_examples: Ejemplos personalizados para el endpoint
        
    Returns:
        Decorador que mejora la documentación del endpoint
        
    Example:
        @router.get("/users", response_model=APIResponse[List[User]])
        @document_api_response(
            success_description="Lista de usuarios obtenida exitosamente",
            data_description="Array de objetos Usuario con información completa"
        )
        async def get_users():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # Extraer información del tipo de retorno
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation
        
        # Construir documentación mejorada
        enhanced_doc = func.__doc__ or ""
        
        if get_origin(return_annotation) is not None:
            args = get_args(return_annotation)
            if args:
                inner_type = args[0]
                type_name = getattr(inner_type, '__name__', str(inner_type))
                
                # Agregar información sobre la estructura de respuesta
                enhanced_doc += f"\n\n## Estructura de Respuesta\n\n"
                enhanced_doc += f"La respuesta sigue el formato estándar APIResponse con los siguientes campos:\n\n"
                enhanced_doc += f"- **`status`**: Estado de la operación (`success`, `error`, `warning`)\n"
                enhanced_doc += f"- **`data`**: {data_description or f'Datos del tipo {type_name} con la estructura documentada a continuación'}\n"
                enhanced_doc += f"- **`message`**: Mensaje descriptivo de la operación realizada\n"
                enhanced_doc += f"- **`errors`**: Lista de errores detallados (solo presente si status es `error`)\n"
                enhanced_doc += f"- **`meta`**: Metadatos adicionales como información de paginación\n"
                
                # Agregar documentación del modelo de datos si está disponible
                if hasattr(inner_type, '__doc__') and inner_type.__doc__:
                    enhanced_doc += f"\n## Documentación del Tipo de Datos ({type_name})\n\n"
                    enhanced_doc += inner_type.__doc__
                
                # Agregar información sobre campos del modelo si es un BaseModel
                if (hasattr(inner_type, '__fields__') or 
                    (hasattr(inner_type, '__annotations__') and 
                     issubclass(inner_type.__class__, type) and 
                     issubclass(inner_type, BaseModel))):
                    try:
                        enhanced_doc += f"\n## Campos del Modelo {type_name}\n\n"
                        if hasattr(inner_type, 'model_json_schema'):
                            schema = inner_type.model_json_schema()
                            if 'properties' in schema:
                                for field_name, field_info in schema['properties'].items():
                                    field_type = field_info.get('type', 'unknown')
                                    field_desc = field_info.get('description', 'Sin descripción')
                                    required = field_name in schema.get('required', [])
                                    req_text = " *(requerido)*" if required else " *(opcional)*"
                                    enhanced_doc += f"- **`{field_name}`** ({field_type}){req_text}: {field_desc}\n"
                    except Exception:
                        # Si no se puede extraer la información del schema, continuar sin error
                        pass
                
                # Agregar ejemplos si se solicita
                if include_examples:
                    enhanced_doc += f"\n## Ejemplos de Respuesta\n\n"
                    
                    if custom_examples:
                        for example_name, example_data in custom_examples.items():
                            enhanced_doc += f"### {example_name}\n```json\n{example_data}\n```\n\n"
                    else:
                        # Ejemplo básico de respuesta exitosa
                        enhanced_doc += f"### Respuesta Exitosa\n"
                        enhanced_doc += f"```json\n"
                        enhanced_doc += f"{{\n"
                        enhanced_doc += f'  "status": "success",\n'
                        enhanced_doc += f'  "data": "Datos del tipo {type_name} según la estructura documentada",\n'
                        enhanced_doc += f'  "message": "{success_description}",\n'
                        enhanced_doc += f'  "errors": null,\n'
                        enhanced_doc += f'  "meta": null\n'
                        enhanced_doc += f"}}\n```\n\n"
                        
                        # Ejemplo de respuesta de error
                        enhanced_doc += f"### Respuesta de Error\n"
                        enhanced_doc += f"```json\n"
                        enhanced_doc += f"{{\n"
                        enhanced_doc += f'  "status": "error",\n'
                        enhanced_doc += f'  "data": null,\n'
                        enhanced_doc += f'  "message": "Descripción del error ocurrido",\n'
                        enhanced_doc += f'  "errors": [\n'
                        enhanced_doc += f'    {{\n'
                        enhanced_doc += f'      "code": "VALIDATION_ERROR",\n'
                        enhanced_doc += f'      "message": "Descripción específica del error",\n'
                        enhanced_doc += f'      "field": "campo_problematico",\n'
                        enhanced_doc += f'      "details": null\n'
                        enhanced_doc += f'    }}\n'
                        enhanced_doc += f'  ],\n'
                        enhanced_doc += f'  "meta": null\n'
                        enhanced_doc += f"}}\n```\n"
        
        wrapper.__doc__ = enhanced_doc
        return wrapper
    
    return decorator


def document_paginated_response(
    success_description: str = "Lista obtenida exitosamente",
    data_description: Optional[str] = None,
    include_pagination_info: bool = True
):
    """
    Decorador especializado para endpoints que retornan PaginatedResponse.
    
    Este decorador es similar a document_api_response pero incluye información
    específica sobre paginación y estructura de listas.
    
    Args:
        success_description: Descripción para respuestas exitosas
        data_description: Descripción específica para los elementos de la lista
        include_pagination_info: Si incluir información detallada sobre paginación
        
    Returns:
        Decorador que mejora la documentación del endpoint paginado
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # Extraer información del tipo de retorno
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation
        
        # Construir documentación mejorada
        enhanced_doc = func.__doc__ or ""
        
        if get_origin(return_annotation) is not None:
            args = get_args(return_annotation)
            if args and len(args) > 0:
                list_type = args[0]
                if get_origin(list_type) and get_args(list_type):
                    inner_type = get_args(list_type)[0]
                    type_name = getattr(inner_type, '__name__', str(inner_type))
                    
                    enhanced_doc += f"\n\n## Respuesta Paginada\n\n"
                    enhanced_doc += f"Este endpoint retorna una respuesta paginada con la siguiente estructura:\n\n"
                    enhanced_doc += f"- **`status`**: Estado de la operación (`success`)\n"
                    enhanced_doc += f"- **`data`**: Array de objetos {type_name} {data_description or 'con la estructura documentada'}\n"
                    enhanced_doc += f"- **`message`**: Mensaje descriptivo de la operación\n"
                    enhanced_doc += f"- **`meta.pagination`**: Información de paginación\n"
                    
                    if include_pagination_info:
                        enhanced_doc += f"\n## Metadatos de Paginación\n\n"
                        enhanced_doc += f"El campo `meta.pagination` contiene:\n\n"
                        enhanced_doc += f"- **`total`**: Total de registros disponibles\n"
                        enhanced_doc += f"- **`limit`**: Número máximo de elementos por página\n"
                        enhanced_doc += f"- **`offset`**: Número de elementos omitidos desde el inicio\n"
                        enhanced_doc += f"- **`has_next`**: `true` si hay más páginas disponibles\n"
                        enhanced_doc += f"- **`has_prev`**: `true` si hay páginas anteriores\n"
                    
                    # Ejemplo de respuesta paginada
                    enhanced_doc += f"\n## Ejemplo de Respuesta Paginada\n\n"
                    enhanced_doc += f"```json\n"
                    enhanced_doc += f"{{\n"
                    enhanced_doc += f'  "status": "success",\n'
                    enhanced_doc += f'  "data": [\n'
                    enhanced_doc += f'    "Array de objetos {type_name} según estructura documentada"\n'
                    enhanced_doc += f'  ],\n'
                    enhanced_doc += f'  "message": "{success_description}",\n'
                    enhanced_doc += f'  "errors": null,\n'
                    enhanced_doc += f'  "meta": {{\n'
                    enhanced_doc += f'    "pagination": {{\n'
                    enhanced_doc += f'      "total": 150,\n'
                    enhanced_doc += f'      "limit": 20,\n'
                    enhanced_doc += f'      "offset": 0,\n'
                    enhanced_doc += f'      "has_next": true,\n'
                    enhanced_doc += f'      "has_prev": false\n'
                    enhanced_doc += f'    }}\n'
                    enhanced_doc += f'  }}\n'
                    enhanced_doc += f"}}\n```\n"
        
        wrapper.__doc__ = enhanced_doc
        return wrapper
    
    return decorator
