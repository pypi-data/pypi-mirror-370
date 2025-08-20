MODEL_TEMPLATE = """
from hape.logging import Logging
from sqlalchemy import Column, Integer, String, Float, Boolean, BigInteger, ForeignKey, Index, Date, DateTime, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from hape.base.model import Model

class {{model_name_pascal_case}}(Model):
    __tablename__ = '{{model_name_snake_case}}'
    logger = Logging.get_logger('{{project_name_snake_case}}.models.{{model_name_snake_case}}')
    
    {{model_columns}}
    {{model_relationships}}
    def __init__(self, **kwargs):
        filtered_kwargs = {key: kwargs[key] for key in self.__table__.columns.keys() if key in kwargs}
        super().__init__(**filtered_kwargs)
        for key, value in filtered_kwargs.items():
            setattr(self, key, value)
        self.logger = Logging.get_logger('{{project_name_snake_case}}.models.{{model_name_snake_case}}')
""".strip()