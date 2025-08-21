import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VariableParser:
    def __init__(self):
        self._regexp = re.compile(r"\{(.+?)\}")
        self._variables = {}

    def set(self, variable: str, value):
        self._variables[variable] = value

    def replace(self, input):
        if isinstance(input, dict):
            return {k: self.replace(v) for k, v in input.items()}
        elif isinstance(input, list):
            return [self.replace(i) for i in input]
        elif isinstance(input, str):
            return self._replace_string(input)
        else:
            return input

    def _replace_string(self, input: str):
        matches = self._regexp.findall(input)
        result = input
        for match in matches:
            logger.debug(
                f'Replacing variable "{match}" with {str(self._variables.get(match))}'
            )
            result = result.replace(f"{{{match}}}", str(self._variables.get(match)))
        return result
