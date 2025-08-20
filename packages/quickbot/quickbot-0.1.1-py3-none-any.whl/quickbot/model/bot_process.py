import inspect
from typing_extensions import get_type_hints
from pydantic import BaseModel
from typing import ClassVar

from .descriptors import ProcessDescriptor, BotContext, Process
from .bot_metadata import BotMetadata


class BotProcessMetaclass(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        if name == "BotProcess":
            namespace.pop("run")
            return super().__new__(mcs, name, bases, namespace, **kwargs)

        run_attr = namespace.get("run", None)
        if run_attr is None or not isinstance(run_attr, staticmethod):
            raise TypeError(f"{name}.run must be defined as a @staticmethod")

        func = run_attr.__func__
        sig = inspect.signature(func)
        if list(sig.parameters.keys()) not in [["context", "parameters"], ["context"]]:
            raise TypeError(
                f"{name}.run must have exactly two arguments: context, parameters or one argument: context"
            )

        hints = get_type_hints(func, globalns=globals(), localns=namespace)

        # Check arguments
        ctx_type = hints.get("context")
        if ctx_type is None or not issubclass(ctx_type, BotContext):
            raise TypeError(f"{name}.run: 'context' must be BotContext")

        param_type = hints.get("parameters")
        if param_type is not None and not issubclass(param_type, BaseModel):
            raise TypeError(f"{name}.run: 'parameters' must be subclass of BaseModel")

        return_type = hints.get("return")

        # Auto-generation of schemas

        descriptor_kwargs = {"process_class": None}
        process_descriptor = namespace.pop("bot_process_descriptor", None)
        if process_descriptor and isinstance(process_descriptor, Process):
            descriptor_kwargs.update(process_descriptor.__dict__)

        descriptor_kwargs.update(
            name=name,
            input_schema=param_type,
            output_schema=return_type,
        )

        descriptor = ProcessDescriptor(**descriptor_kwargs)
        namespace["bot_process_descriptor"] = descriptor

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        descriptor.process_class = cls

        bot_metadata = BotMetadata()
        bot_metadata.process_descriptors[descriptor.name] = descriptor

        namespace["bot_metadata"] = bot_metadata

        return super().__new__(mcs, name, bases, namespace, **kwargs)


class BotProcess(metaclass=BotProcessMetaclass):
    """
    Base class for business logic processes.
    """

    bot_process_descriptor: ClassVar[ProcessDescriptor]
    bot_metadata: ClassVar[BotMetadata]

    @staticmethod
    def run(context: BotContext, parameters: BaseModel = None): ...
