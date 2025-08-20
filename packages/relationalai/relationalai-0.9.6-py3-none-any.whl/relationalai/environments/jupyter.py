from relationalai.environments.base import except_return
from relationalai.environments.ipython import IPythonEnvironment

class JupyterEnvironment(IPythonEnvironment):
    @classmethod
    @except_return(ImportError, False)
    def detect(cls):
        from IPython import get_ipython # type: ignore
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
