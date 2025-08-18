from pydantic import BaseModel


class ToolRegister:
    TOOLS = {}

    @classmethod
    def register(cls, func):
        ToolRegister.TOOLS[func.__name__] = func
        return func

    @classmethod
    def get_tools(cls):
        return cls.TOOLS

class SchemaRegister:
    SCHEMAS = {}

    @classmethod
    def register(cls, name: str, description: str):
        def wrapper(schema: type[BaseModel]):
            cls.SCHEMAS[name] = {
                'schema': schema,
                'description': description,
                'json_schema': schema.model_json_schema()
            }
            return schema
        return wrapper

    @classmethod
    def get_schemas(cls):
        return cls.SCHEMAS