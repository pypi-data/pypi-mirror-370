from .job_parameters import gather_parameters

class EtlJob:
    def __init__(self, params=None):
        if params is None:
            self.params = gather_parameters()
        else:
            self.params = params

    def get_parameter(self, parameter, required: bool, default=None):
        parameter_input_value = self.params.get(parameter.parameter_name)
        parameter.validate(parameter_input_value, default, required)
        return parameter.get_value_or_else(parameter_input_value, default)

    def run(self):
        pass
