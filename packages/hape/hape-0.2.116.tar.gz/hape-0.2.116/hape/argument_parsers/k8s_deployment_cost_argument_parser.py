from hape.logging import Logging
from hape.base.model_argument_parser import ModelArgumentParser
from hape.models.k8s_deployment_cost_model import K8SDeploymentCost
from hape.controllers.k8s_deployment_cost_controller import K8SDeploymentCostController

class K8SDeploymentCostArgumentParser(ModelArgumentParser):
    def __init__(self):
        super().__init__(K8SDeploymentCost, K8SDeploymentCostController)
        self.logger = Logging.get_logger('hape.argument_parsers.k8s_deployment_cost_argument_parser')

    def extend_subparser(self):
        pass
    
    def extend_actions(self):
        pass