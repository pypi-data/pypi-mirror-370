from hape.logging import Logging
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, TIMESTAMP, Text

class ModelArgumentParser(ABC):

    _sqlalchemy_type_map = {
        Integer: int,
        String: str,
        Float: float,
        Boolean: bool,
        Date: datetime.date,
        DateTime: datetime,
        TIMESTAMP: datetime,
        Text: str
    }

    def __init__(self, base_model_class, controller_class):
        self.logger = Logging.get_logger('hape.base.model_argument_parser')
        self._base_model_class = base_model_class
        self._base_model_name = base_model_class.__name__
        self._base_model_command = ''
        for i in range(len(self._base_model_name)):
            if self._base_model_name[i].isupper() and i != 0 and not self._base_model_name[i-1].isdigit():
                self._base_model_command += '-' + self._base_model_name[i].lower()
            else:
                self._base_model_command += self._base_model_name[i].lower()
        self._base_model_columns = {
            column.name: {
                "type": self._sqlalchemy_type_map.get(type(column.type), str),
                "nullable": column.nullable
            } for column in self._base_model_class.__table__.columns
        }
        self._controller = controller_class()
        self.base_model_subparser = None
        self.args = None
    
    @abstractmethod
    def extend_subparser(self):
        pass
    
    @abstractmethod
    def extend_actions(self):
        pass
    
    def create_subparser(self, subparsers):
        self.logger.debug(f"create_subparser(subparsers)")
        base_model_parser = subparsers.add_parser(self._base_model_command, help=f"Commands to manage {self._base_model_name} base_model")
        self.base_model_subparser = base_model_parser.add_subparsers(dest="action")

        for action in ["save", "get", "get-all", "delete", "delete-all"]:
            object_word = "objects" if "-all" in action else "object"
            action_parser = self.base_model_subparser.add_parser(action, help=f"{action.capitalize()} {self._base_model_name} {object_word} based on passed arguments or filters")
            
            for column_name, column_type_and_nullable in self._base_model_columns.items():
                column_name_dashes = column_name.replace('_', '-')
                if action == "save":
                    if column_name == "id":
                        continue
                    required_value = not column_type_and_nullable["nullable"]
                    required_text = "[REQUIRED] " if required_value else ""
                else:
                    required_value = False
                    required_text = ""
                
                help_text = f"{required_text}Value for {column_name_dashes} type {column_type_and_nullable['type']}"

                action_parser.add_argument(f"--{column_name_dashes}", required=required_value, help=help_text)

        self.extend_subparser()
    
    def run_action(self, args):
        self.logger.debug(f"run_action(args)")
        self.args = args
        if args.command != self._base_model_command:
            return
        
        filters = {}
        for column_name, column_type_and_nullable in self._base_model_columns.items():
            if hasattr(args, column_name) and getattr(args, column_name):
                column_type = column_type_and_nullable["type"]
                try:
                    filters[column_name] = column_type(getattr(args, column_name))
                except ValueError as e:
                    raise ValueError(f"Error casting {column_name}: {str(e)}")
        
        if args.action == "save":
            base_model = self._base_model_class(**filters)
            self._controller.save(base_model)
            print(base_model.json())
        
        elif args.action == "get":
            base_model = self._controller.get(**filters)
            if not base_model:
                print(f"{self._base_model_name} object not found.")
                return
            print(base_model.json())
        
        elif args.action == "get-all":
            base_model_list = self._controller.get_all(**filters)
            if not base_model_list:
                print(f"No {self._base_model_name} objects found.")
                return
            print(self._base_model_class.list_to_json(base_model_list))
        
        elif args.action == "delete":
            base_model = self._controller.get(**filters)
            if not base_model:
                print(f"{self._base_model_name} object not found.")
                return
            self._controller.delete(base_model)
            print("Deleted object:")
            print(base_model.json())
        
        elif args.action == "delete-all":
            base_model_list = self._controller.get_all(**filters)
            if not base_model_list:
                print(f"No {self._base_model_name} objects found.")
                return
            for base_model in base_model_list:
                self._controller.delete(base_model)
            print("Deleted objects:")
            print(self._base_model_class.list_to_json(base_model_list))
        
        else:
            self.extend_actions()
