import asyncio
import threading
from typing import Any, Callable, Set, Type, Awaitable, Optional, Union
import P4


class P4Async(P4.P4):
    """
    An async extension to P4.P4.
    This class is a placeholder for future async methods.
    """

    # Methods that are simply wrapped to a thread for async execution.  These are methods
    # that do not use `self.run` for execution.
    simple_wrap_methods: Set[str] = {
        "connect",
        "disconnect",
        "run_tickets",
    }

    # Methods that are wrapped by adding `with_async=True` to the underlying
    # call to 'self.run', leaving other processing to happen in the current Task.
    run_wrap_methods: Set[str] = {
        "run_submit",
        "run_shelve",
        "delete_shelve",
        "run_login",
        "run_password",
        "run_filelog",
        "run_print",
        "run_resolve",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # A lock to synchronize access to the P4 adapter.
        # The P4 adapter can only have one operation executing at a time.
        # Can't use direct attribute setter on a P4 object.
        self.__dict__["lock"] = threading.Lock()

    async def execute(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """
        Default method to run a synchronous Perforce command.
        Override this method for customized thread scheduling.
        """

        def helper():
            # Ensure thread safety: the P4 adapter can only have one operation at a time.
            with self.lock:
                return func(*args, **kwargs)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, helper)

    def run(
        self, *args: Any, with_async: bool = False, **kwargs: Any
    ) -> Union[Any, Awaitable[Any]]:
        """
        Run a Perforce command.

        If `with_async` is True, the command will return an awaitable that can be awaited
        to execute the command asynchronously. If `with_async` is False, the command will
        execute directly in the current thread.
        """
        if with_async:
            # return an awaitable
            return self.execute(self.sync_run, *args, **kwargs)
        else:
            # execute directly
            return self.sync_run(*args, **kwargs)

    def sync_run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Run a Perforce command.
        
        A hook to call the original synchronous `run` method.  Child classes who want to wrap
        extra functionality to the underlying `run` method can override this method.
        It will be called on a worker thread as appropriate.
        """
        return super().run(*args, **kwargs)

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        """
        Asynchronous  version of the `run` method.
        """
        return await self.execute(self.sync_run, *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("arun_"):
            cmd = name[len("arun_") :]
            return lambda *args, **kargs: self.arun(cmd, *args, **kargs)
        elif name.startswith("adelete_"):
            cmd = name[len("adelete_") :]
            return lambda *args, **kargs: self.arun(cmd, "-d", *args, **kargs)
        elif name.startswith("afetch_"):
            cmd = name[len("afetch_") :]
            return lambda *args, **kargs: self.__afetch(cmd, *args, **kargs)
        elif name.startswith("asave_"):
            cmd = name[len("asave_") :]
            return lambda *args, **kargs: self.__asave(cmd, *args, **kargs)
        elif name.startswith("aiterate_"):
            cmd = name[len("aiterate_") :]
            return lambda *args, **kargs: self.__aiterate(cmd, *args, **kargs)
        if name.startswith("a") and name[1:] in self.simple_wrap_methods:
            method = name[1:]
            return lambda *args, **kwargs: self.execute(
                getattr(self, method), *args, **kwargs
            )
        elif name.startswith("a") and name[1:] in self.run_wrap_methods:
            method = name[1:]
            return lambda *args, **kwargs: getattr(self, method)(
                *args, with_async=True, **kwargs
            )
        return super().__getattr__(name)

    async def __afetch(self, cmd: str, *args: Any, **kargs: Any) -> Any:
        """
        Handle async versions of fetch commands.
        """
        result = await self.arun(cmd, "-o", *args, **kargs)
        for r in result:
            if isinstance(r, tuple) or isinstance(r, dict):
                return r
        return result[0]

    async def __aiterate(self, cmd: str, *args: Any, **kargs: Any):
        """
        Handle async versions of iterate commands.
        """
        if cmd not in self.specfields:
            raise Exception("Unknown spec list command: %s", cmd)

        specs = await self.arun(cmd, *args, **kargs)
        spec = self.specfields[cmd][0]
        field = self.specfields[cmd][1]
        for spec in specs:
            yield await self.arun(spec, "-o", spec[field])[0]

    async def __asave(self, cmd: str, *args: Any, **kargs: Any) -> Any:
        self.input = args[0]
        return await self.arun(cmd, "-i", args[1:], **kargs)

    async def __aenter__(self) -> "P4Async":
        """
        Asynchronous context manager enter method.
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """
        Asynchronous context manager exit method.
        """
        if self.connected():
            await self.adisconnect()
