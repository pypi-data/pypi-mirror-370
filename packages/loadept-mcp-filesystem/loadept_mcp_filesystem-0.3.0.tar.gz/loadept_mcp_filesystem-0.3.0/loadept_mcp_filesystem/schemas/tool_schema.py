from pydantic import BaseModel
from ..utils.decorators import SchemaRegister


@SchemaRegister.register(
    name='list_directory',
    description='Tool for listing the contents of a directory.'
)
class ListDirectoryTool(BaseModel):
    dirname: str

@SchemaRegister.register(
    name='find_results',
    description='Tool for finding files in a directory that match a specific pattern.'
)
class FindResultsTool(BaseModel):
    dirname: str
    keyword: str

@SchemaRegister.register(
    name='read_content',
    description='Tool for reading the contents of a file.'
)
class ReadContentTool(BaseModel):
    dirname: str
    filename: str

@SchemaRegister.register(
    name='open_file',
    description='Tool for opening a file with the default application.'
)
class OpenFileTool(BaseModel):
    dirname: str
    filename: str

@SchemaRegister.register(
    name='write_content',
    description='Tool for writing content to a file.'
)
class WriteContentTool(BaseModel):
    dirname: str
    filename: str
    content: str

@SchemaRegister.register(
    name='create_directory',
    description='Tool for creating a new directory.'
)
class CreateDirectoryTool(BaseModel):
    dirpath: str
    dirname: str
