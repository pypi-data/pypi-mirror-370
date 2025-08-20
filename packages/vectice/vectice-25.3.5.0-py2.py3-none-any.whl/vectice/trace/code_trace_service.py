from __future__ import annotations

import inspect
import logging
import re
import sys
import threading
from inspect import FrameInfo
from types import FrameType
from typing import Any, Dict, Set

_logger = logging.getLogger(__name__)


class CodeTraceService:
    """A service that automatically captures source code and variables of functions called within its context.

    The purpose of this service is to trace the execution of Python code, capturing the source code of functions
    as they are called, and to collect variables that are defined or modified during the execution of the traced code.

    This service is designed to be used as a context manager, allowing you to easily start and stop tracing
    without needing to manually manage the tracing state.

    See: https://docs.python.org/3/library/trace.html
    """

    def __init__(self, warn_on_trace: bool = True):
        self.warn_on_trace = warn_on_trace

        self._code = set()
        self._captured_functions = set()

        self._initial_globals = {}
        self._initial_locals = {}
        self._captured_variables = {}

        self._original_trace = None
        self._thread_id = None
        self._vectice_frame_index = 2

    @property
    def code(self) -> Set[str]:
        """Get all captured source code."""
        return self._code

    @property
    def captured_variables(self) -> Dict[str, Any]:
        """Get all captured variables."""
        return self._captured_variables

    def __enter__(self):
        """Enter the context manager and start tracing.

        Important notes:
        - This method sets the global trace function to capture function calls and their source code.
        - It also captures the initial global and local variables in the current frame.
        - If another trace function is already active, it will warn the user unless `warn_on_trace` is set to False.
        - The tracing is limited to the current thread to avoid interference with other threads or debugggers.

        Technical details:
        - Uses `sys.settrace()` to set a custom trace function that captures function calls.
        - Uses `sys._getframe()` to access the current frame and capture initial global and local variables.
        - Most importantly, the depth of the frame is set to 1 to capture the caller's frame, which is where the context manager is invoked.
        """
        # Flush any previously captured data, allows re-use of the service
        self.flush()
        # Check if tracing is already active
        current_trace = sys.gettrace()
        if current_trace is not None:
            # This warning will help for debugging purposes, but can be disabled if needed.
            if self.warn_on_trace:
                _logger.warning(
                    "Another trace function is already active. This may interfere with Vectice Trace.",
                )
            self._original_trace = current_trace

        try:
            stack = inspect.stack()
            vectice_frame: FrameType = self._find_vectice_trace_frame(stack)

            # Inital globals and locals, we use the difference between the initial and final globals/locals to capture changes.
            self._initial_globals = dict(vectice_frame.f_globals)
            self._initial_locals = dict(vectice_frame.f_locals)
            # We need to find the module name to get the source code of the module.
            module_name = vectice_frame.f_globals.get("__name__", "__main__")
            self._code.add(self._get_module_source_code(module_name))
            # Store the thread ID to ensure we only trace this thread
            self._thread_id = threading.get_ident()
            sys.settrace(self._safe_trace_calls)
        except Exception as e:
            # Restore original trace on error
            if self._original_trace:
                sys.settrace(self._original_trace)
            _logger.warning(f"Error during Vectice trace setup: {e}", exc_info=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pyright: ignore[reportMissingParameterType]
        """Exit the context manager and stop tracing.

        Important notes:
        - This method restores the original trace function and captures the final global and local variables.
        - It ensures that the tracing state is cleaned up properly, even if an error occurs during tracing.
        - The final global and local variables are captured to allow inspection of the state after the traced code has executed.

        Technical details:
        - Uses `sys.settrace()` to restore the original trace function.
        - Uses `sys._getframe()` to access the caller's frame and capture the final global and local variables.
        - The depth of the frame is set to 2 to capture the caller's frame, which is where the context manager is invoked.
        - We clear local and global variables to prevent memory leaks.
        - Finally, it clears references to prevent memory leaks.
        - If an error occurs during cleanup, it logs a warning but does not prevent the cleanup from completing.
        """
        try:
            # Always restore the original trace function
            sys.settrace(self._original_trace)

            # Capture the final global and local variables
            vectice_frame: FrameType = sys._getframe(self._vectice_frame_index)  # pyright: ignore[reportPrivateUsage]

            final_globals = dict(vectice_frame.f_globals)
            self._capture_variables(final_globals)
            del final_globals

            final_locals = dict(vectice_frame.f_locals)
            self._capture_variables(final_locals)
            del final_locals

        except Exception as e:
            _logger.warning(f"Error during Vectice trace cleanup: {e}")

        finally:
            # Always clear references to prevent memory leaks
            self._original_trace = None
            self._thread_id = None

        return False

    #### Utility Methods ####

    def _find_vectice_trace_frame(self, frames: list[FrameInfo]) -> FrameType:
        """Find the frame where the Vectice trace context manager was invoked.

        The frames are added to the stack in reverse order, so the frame where the context manager is invoked
        is actually the frame after all the __enter__ frames.

        We look for the the context manager frames with `__enter__`.
        stack = [__enter__, __enter__, with vectice.trace(), ...]

        The length of the __enter__ frames `len(stack)` will be the index we entered the context manager.
        """
        frame_index = len([frame for frame in frames if re.search("__enter__", str(frame.function))])
        # set the vectice frame index to be used for __exit__
        self._vectice_frame_index = frame_index
        return frames[frame_index].frame

    def _capture_variables(self, variables: Dict[str, Any]):
        for name, value in variables.items():
            # Shallow copy of initial globals and locals to check for changes
            all_intials = {**self._initial_globals, **self._initial_locals}

            is_valid_variable = (
                not name.startswith("__")
                and "@py_assert" not in name
                and (name not in all_intials or all_intials[name] is not value)
            )
            if is_valid_variable:
                self._captured_variables[name] = value

    def _get_module_source_code(self, module_name: str = "__main__") -> str:
        """Get the source code of the specified module (defaults to main).

        This gets the code where the script was run, which is usually the main module.
        """
        module = sys.modules.get(module_name)

        if module is None:
            _logger.warning(
                "Could not get the module. It may not be loaded or does not exist.",
            )
            return ""

        try:
            return inspect.getsource(module)
        except (OSError, TypeError):
            _logger.warning(
                f"Could not get source code for module {module_name}. It may be a built-in module or not available.",
            )

        return ""

    def _is_user_function(self, filename: str | None = None, func_name: str | None = None):
        """Determine if a function is user-created vs from a library.

        Checks site-packages and standard library locations.
        """
        if not filename or not filename.endswith(".py"):
            return False

        # Skip obvious non-user functions
        if func_name and (func_name.startswith("<") or func_name == "<module>"):
            return False

        # Normalize path separators for cross-platform compatibility
        normalized_filename = filename.replace("\\", "/")

        # If it's in site-packages, it's library code
        if "site-packages" in normalized_filename:
            return False

        # we do not want to capture vectice code
        if "src/vectice" in normalized_filename:
            return False

        # Check for standard library patterns (cross-platform)
        stdlib_patterns = [
            "/lib/python",  # Unix-like systems
            "/Lib/",  # Windows
            "\\Lib\\",  # Windows with backslashes
        ]

        for pattern in stdlib_patterns:
            if pattern in filename and any(
                f"/python{version}" in filename or f"\\python{version}" in filename
                for version in ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
            ):
                return False

        # Everything else is user code
        return True

    def _capture_function_source(self, frame: FrameType, func_name: str):
        # Get the function object from the frame
        func_locals = frame.f_locals
        func_globals = frame.f_globals

        # Try to find the function in globals or locals
        func = func_globals.get(func_name) or func_locals.get(func_name)

        if func and callable(func):
            func_signature = inspect.getsource(func)
            self._code.add(func_signature)
            self._captured_functions.add(func_name)

    def flush(self):
        """Flush the captured code and variables.

        This method is a no-op in this context, as the captured code and variables are stored in memory.
        It can be used to clear the captured data if needed.
        """
        self._code.clear()
        self._captured_variables.clear()
        self._captured_functions.clear()
        self._initial_globals.clear()
        self._initial_locals.clear()

    ##### Trace Methods #####

    def _safe_trace_calls(self, frame: FrameType, event: str, arg: Any):
        """Safe wrapper around the trace function.

        The key points:
        1. **Call original first** - `self._original_trace(frame, event, arg)`
        2. **Respect original's return** - If it returns `None`, stop tracing
        3. **Chain the return** - Return your tracer or fall back to original
        4. **Error handling** - Always fall back to original tracer on errors
        """
        try:
            # Call the original tracer first (if it exists)
            if self._original_trace:
                original_result = self._original_trace(frame, event, arg)
                # If original tracer returns None, it wants to stop tracing
                if original_result is None:
                    return None

            # Only trace the correct thread
            # TODO: This might be unreliable according to the documentation
            if threading.get_ident() != self._thread_id:
                return self._safe_trace_calls

            self._trace_calls(frame, event, arg)

            # We keep calling the safe trace function to continue tracing
            return self._safe_trace_calls

        except Exception as e:
            _logger.warning(f"Error in trace function: {e}")
            # Fall back to original tracer on error
            return self._original_trace

    def _trace_calls(self, frame: FrameType, event: str, arg: Any):
        """Trace function calls and capture their source.

        A function is called (or some other code block entered). The global trace function is called; arg is None;
        the return value specifies the local trace function.

        See: https://docs.python.org/3/library/sys.html#sys.settrace
        """
        func_name = frame.f_code.co_name
        filename = frame.f_code.co_filename

        # Skip built-in, site-packages and builtins
        is_user_func = self._is_user_function(filename, func_name)
        if not is_user_func:
            return self._safe_trace_calls

        if event == "call":
            # Skip functions we have seen already
            is_function_to_capture = func_name not in self._captured_functions

            if is_function_to_capture:
                self._capture_function_source(frame, func_name)
        elif event == "return":
            # We capture the local scope of returns
            self._capture_variables(frame.f_locals)

        return self._safe_trace_calls
