from hape.logging import Logging

class ModelController():

    def __init__(self, base_model_class):
        self.logger = Logging.get_logger('hape.base.model_controller')
        self._base_model_class = base_model_class
    
    def save(self, base_model):
        self.logger.debug(f"save()")
        if base_model.validate():
            try:
                if base_model.save():
                    return True
                raise RuntimeError(f"Couldn't save {base_model.json()}")
            except Exception as e:
                raise RuntimeError(f"An error occurred while saving: {e}")
        
        raise ValueError("Model validation failed.")

    def get(self, **filters):
        self.logger.debug(f"get({filters})")
        if not filters:
            raise ValueError("Filters cannot be empty for get operation.")
        return self._base_model_class.get(**filters)
    
    def get_all(self, **filters):
        self.logger.debug(f"get_all({filters})")
        return self._base_model_class.get_all(**filters)
    
    def delete(self, base_model):
        self.logger.debug(f"delete()")
        if not isinstance(base_model, self._base_model_class):
            raise TypeError("Invalid base_model instance for deletion.")
        return base_model.delete()
    
    def delete_all(self, **filters):
        self.logger.debug(f"delete_all({filters})")
        if not filters:
            raise ValueError("Filters cannot be empty for delete_all operation.")
        return self._base_model_class.delete_all(**filters)
