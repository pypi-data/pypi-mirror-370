import os
import shutil

from mosamatic.logging import LogManager

LOG = LogManager()


class Task:
    def __init__(self, input, output, params=None, overwrite=False):
        self._input = input
        self._output = os.path.join(output, self.__class__.__name__)
        self._params = params or {}
        self._overwrite = overwrite
        self._class_name = self.__class__.__name__
        if os.path.exists(self._output):
            if not self._overwrite:
                raise RuntimeError(f'Output already exists. Remove it or set "overwrite=True"')
            else:
                shutil.rmtree(self._output)
        os.makedirs(self._output, exist_ok=False)
        if params and not isinstance(params, dict):
            raise RuntimeError('Parameters must be dictionary of name/value pairs')

    def input(self, name=None):
        if isinstance(self._input, dict):
            if name in self._input.keys():
                return self._input[name]
            if name is None and len(self._input.keys()) > 0:
                return self._input[next(iter(self._input))] # Return first element if no name provided
        return self._input
    
    def output(self):
        return self._output
    
    def param(self, name=None):
        if self._params and name in self._params.keys():
            return self._params[name]
        if name is None and len(self._params.keys()) > 0:
            return self._params[next(iter(self._params))] # Return first element if no name provided
        raise RuntimeError(f'Parameter "{name}" does not exist')
    
    def overwrite(self):
        return self._overwrite
    
    def set_progress(self, step, nr_steps):
        LOG.info(f'[{self._class_name}] step {step} from {nr_steps}')
    
    def run(self):
        raise NotImplementedError()