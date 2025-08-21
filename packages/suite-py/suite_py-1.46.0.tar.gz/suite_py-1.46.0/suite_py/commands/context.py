import dataclasses
from inspect import signature

from suite_py.lib.config import Config
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.okta_handler import Okta
from suite_py.lib.tokens import Tokens


@dataclasses.dataclass
class Context:
    project: str
    config: Config
    captainhook: CaptainHook
    tokens: Tokens
    okta: Okta

    # Call the function to_call with kwargs, injecting fields from self as default arguments
    def call(self, to_call, **kwargs):
        provided = self.shallow_dict()
        needed = signature(to_call).parameters.keys()
        provided = {k: provided[k] for k in needed if k in provided}

        kwargs = provided | kwargs

        return to_call(**kwargs)

    def shallow_dict(self):
        """
        Converts the dataclass to a dict.

        Unlike dataclasses.asdict this function only shallow copies the fields
        instead of using copy.deepcopy()
        """
        return {
            field.name: getattr(self, field.name) for field in dataclasses.fields(self)
        }
