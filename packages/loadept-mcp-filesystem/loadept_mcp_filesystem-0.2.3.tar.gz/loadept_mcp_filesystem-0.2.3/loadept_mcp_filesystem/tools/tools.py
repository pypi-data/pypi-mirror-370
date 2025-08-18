from ..utils import base_path, ToolRegister
from os import makedirs, listdir
from os.path import join, isdir, exists
from mcp.types import TextContent
import json


@ToolRegister.register
def list_directory(dirname: str) -> list[TextContent]:
    dir_path = join(base_path, dirname)
    content = listdir(dir_path)
    content_info = [
        {
            "type": "directory" if isdir(join(dir_path, item)) else "file",
            "name": item
        }
        for item in content
    ]

    return [TextContent(
        type="text",
        text=f"Directorio {dirname} contiene:\n{json.dumps(content_info, indent=2)}"
    )]

@ToolRegister.register
def find_results(dirname: str, keyword: str) -> list[TextContent]:
    keyword_lower = keyword.lower()
    dir_path = join(base_path, dirname)
    if not exists(dir_path):
        return [TextContent(
            type="text",
            text=f"El directorio {dirname} no existe."
        )]

    dir_content = listdir(dir_path)
    results = [
        file
        for file in dir_content
        if (file_lower := file.lower()).startswith(keyword_lower)
        or keyword_lower in file_lower
    ]
    if not results:
        return [TextContent(
            type="text",
            text=f"Archivo {keyword} no encontrado en {dirname}."
        )]

    return [TextContent(
        type="text",
        text=f"Resultados de busqueda en {dirname}:\n{', '.join(results)}"
    )]

@ToolRegister.register
def read_content(dirname: str, filename: str) -> list[TextContent]:
    dir_content = listdir(join(base_path, dirname))
    if filename not in dir_content:
        return [TextContent(
            type="text",
            text=f"Archivo {filename} no encontrado en {dirname}."
        )]

    with open(join(base_path, dirname, filename), 'r') as file:
        content = file.read()

    if not content:
        return [TextContent(
            type="text",
            text=f"El archivo {filename} en {dirname} está vacío."
        )]

    return [TextContent(
        type="text",
        text=f"Contenido de {filename} en {dirname}:\n{content}"
    )]

@ToolRegister.register
def write_content(dirname: str, filename: str, content: str) -> list[TextContent]:
    with open(join(base_path, dirname, filename), 'w') as file:
        file.write(content)

    return [TextContent(
        type="text",
        text=f"Contenido escrito en {filename} dentro de {dirname}."
    )]

@ToolRegister.register
def create_directory(dirpath: str, dirname: str) -> list[TextContent]:
    try:
        new_dir_path = join(base_path, dirpath, dirname)
        makedirs(new_dir_path, exist_ok=True)
        return [TextContent(
            type="text",
            text=f"Directorio {dirname} creado exitosamente en {dirpath}."
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error al crear el directorio {dirname}: {str(e)}"
        )]
