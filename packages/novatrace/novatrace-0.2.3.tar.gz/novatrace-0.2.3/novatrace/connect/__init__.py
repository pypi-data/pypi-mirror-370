from sqlalchemy import create_engine
from decouple import config as deconfig

from datetime import datetime
import pytz
import os

hora = pytz.utc

def _find_connect_db():
    """Buscar connect.db dinámicamente en el directorio actual y directorios padre."""
    current_dir = os.getcwd()

    # Primero intentar en el directorio actual
    db_path = os.path.join(current_dir, 'connect.db')
    if os.path.exists(db_path):
        return db_path

    # Buscar hacia arriba en la estructura de directorios
    search_dir = current_dir
    max_levels = 5  # Limitar la búsqueda a 5 niveles hacia arriba

    for level in range(max_levels):
        parent_dir = os.path.dirname(search_dir)
        if parent_dir == search_dir:  # Llegamos a la raíz del sistema
            break

        db_path = os.path.join(parent_dir, 'connect.db')
        if os.path.exists(db_path):
            return db_path

        search_dir = parent_dir

    # Si no encontramos el archivo, crear uno en el directorio actual
    return os.path.join(current_dir, 'connect.db')

# Buscar dinámicamente la base de datos
db_path = _find_connect_db()
database_url = f"sqlite:///{db_path}"

#engine a sqlite
engine = create_engine(deconfig("DATABASE_URL", default=database_url))