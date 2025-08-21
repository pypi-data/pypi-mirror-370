import sys
import click

from tai_sql import pm as sqlpm
from tai_api import pm
from .funcs import run_generate

@click.command()
@click.option('--schema', '-s', help='Nombre del esquema')
def generate(schema: str=None):
    """Genera recursos para la API."""

    if schema:
        sqlpm.set_current_schema(schema)
    
    else:
        sqlconfig = sqlpm.get_project_config()
        if sqlconfig:
            sqlpm.set_current_schema(sqlconfig.default_schema)

    if not schema and not sqlpm.db:
        click.echo(f"❌ No existe ningún esquema por defecto", err=True)
        click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
        click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
        sys.exit(1)

    config = pm.get_project_config()

    if not config:
        click.echo("❌ No se encontró la configuración del proyecto. Asegúrate de haber inicializado el proyecto con tai-api init.", err=True)
        sys.exit(1)

    run_generate(config)