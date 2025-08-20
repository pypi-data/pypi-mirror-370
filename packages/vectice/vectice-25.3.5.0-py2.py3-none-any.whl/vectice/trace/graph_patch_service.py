from __future__ import annotations

import logging
from importlib.util import find_spec

_logger = logging.getLogger(__name__)

is_plotly = find_spec("plotly") is not None
is_matplotlib = find_spec("matplotlib") is not None


class PlotlyPatcher:
    """Handles monkey patching of Plotly's write_image method."""

    def __init__(self, patched_graphs: list[str]):
        self._original_function = None
        self._is_patched = False
        self._patched_graphs = patched_graphs

    def patch(self):
        """Apply the patch to Plotly's write_image method."""
        if not is_plotly or self._is_patched:
            return

        import plotly.graph_objects as go

        original_method = go.Figure.write_image
        self._original_function = original_method
        patched_graphs = self._patched_graphs

        def patched_write_image(self, *args, **kwargs):  # pyright: ignore[reportMissingParameterType]
            try:
                graph_path = args[0] if args else kwargs.get("file")
                if graph_path:
                    patched_graphs.append(graph_path)
            except Exception:
                pass
            return original_method(self, *args, **kwargs)

        go.Figure.write_image = patched_write_image
        self._is_patched = True

    def unpatch(self):
        """Restore the original write_image method."""
        if not is_plotly or not self._is_patched or not self._original_function:
            return

        import plotly.graph_objects as go

        go.Figure.write_image = self._original_function
        self._is_patched = False


class MatplotlibPatcher:
    """Handles monkey patching of Matplotlib's savefig function."""

    def __init__(self, patched_graphs: list[str]):
        self._original_function = None
        self._is_patched = False
        self._patched_graphs = patched_graphs

    def patch(self):
        """Apply the patch to matplotlib's savefig function."""
        import matplotlib.pyplot as plt

        if not is_matplotlib or self._is_patched:
            return

        original_function = plt.savefig
        self._original_function = original_function

        def patched_savefig(fname, *args, **kwargs):  # pyright: ignore[reportMissingParameterType]
            """A patched version of matplotlib's savefig function that tracks the file path."""
            try:
                if fname:
                    self._patched_graphs.append(fname)
            except Exception:
                pass
            return original_function(fname, *args, **kwargs)

        plt.savefig = patched_savefig
        self._is_patched = True

    def unpatch(self):
        """Restore the original savefig function."""
        import matplotlib.pyplot as plt

        if not is_matplotlib or not self._is_patched or not self._original_function:
            return

        plt.savefig = self._original_function
        self._is_patched = False


class GraphPatchService:
    """Manages all graph library patches."""

    def __init__(self):
        self._patched_graphs: list[str] = []
        self.plotly_patcher = PlotlyPatcher(self._patched_graphs)
        self.matplotlib_patcher = MatplotlibPatcher(self._patched_graphs)

    @property
    def graphs(self) -> list[str]:
        """Get the list of captured graph file paths."""
        return self._patched_graphs.copy()

    def clear_graphs(self):
        """Clear the collected graphs list."""
        self._patched_graphs.clear()

    def patch_all(self):
        """Apply all patches."""
        self.clear_graphs()

        self.plotly_patcher.patch()
        self.matplotlib_patcher.patch()

    def unpatch_all(self):
        """Remove all patches."""
        self.plotly_patcher.unpatch()
        self.matplotlib_patcher.unpatch()
