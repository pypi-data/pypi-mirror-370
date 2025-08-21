from common.secretmanager import SecretManager

EXPERIMENTS_SECRET_NAME = "experiments"
ENABLED_TREATMENT = "enabled"
CONTROL_TREATMENT = "control"


class Experiment:

    def __init__(self, access_key, secret_key, region_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region_name = region_name

    def get_experiment(self, experiment):
        aws_secret_manager = SecretManager(self.access_key, self.secret_key, self.region_name)
        experiment_values = aws_secret_manager.get_secret_key_value(EXPERIMENTS_SECRET_NAME)
        return experiment_values.get(experiment)

    def is_enabled(self, experiment):
        return ENABLED_TREATMENT == self.get_experiment(experiment)

    def is_control(self, experiment):
        return CONTROL_TREATMENT == self.get_experiment(experiment)
