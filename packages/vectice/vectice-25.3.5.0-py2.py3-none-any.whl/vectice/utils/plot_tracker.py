from __future__ import annotations

import logging
import re
import uuid
from importlib.util import find_spec
from io import BytesIO

import matplotlib.pyplot as plt
import PIL.Image as Image
from IPython.core.getipython import get_ipython
from matplotlib._pylab_helpers import Gcf
from PIL.Image import Image as PILImage

from vectice.autolog.autolog_class import GRAPHS, _get_cell_id  # pyright: ignore[reportPrivateUsage]
from vectice.utils.common_utils import suppress_logging

_logger = logging.getLogger(__name__)

is_h2o = find_spec("h2o") is not None
is_plotly = find_spec("plotly") is not None

# ipython shell
ipython = get_ipython()  # type: ignore

if is_plotly:
    import plotly.graph_objects as go

    # Save the original method
    default_write_image = go.Figure.write_image

    def patched_write_image(self, *args, **kwargs):  # pyright: ignore[reportMissingParameterType]
        try:
            cell_id = _get_cell_id(ipython)
            graph_path = args[0] if args else kwargs.get("file")
            GRAPHS[cell_id]["saved"].append(graph_path)
        except Exception:
            pass
        default_write_image(self, *args, **kwargs)

    # Replace the original write_image with the custom one
    go.Figure.write_image = patched_write_image  # pyright: ignore[reportAttributeAccessIssue]

# default savefig and show
default_savefig = plt.savefig


class PlotTracker:
    """If plt.show() is called before plt.savefig(), the saved figure is a blank canvas.
    See: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html

    Matplotlib backends:
    - Supported jupyter backends (activated via %matplotlib inline, %matplotlib notebook, or %matplotlib widget)
    - Other backends, which use a GUI pop up window. For example, `TKAgg` will not be capture by `plt.show()`
        - This is due to jupyter not handling the publish.

    See: https://matplotlib.org/stable/users/explain/figure/backends.html#the-builtin-backends
    """

    def __init__(self, is_line: bool = True):
        self.captured_figures = set()
        self.current_cell = None
        self.is_inline = is_line

    def _log_figures(self, figures: list[PILImage]):
        from vectice.autolog.autolog import LOGIN

        iteration = None
        if LOGIN.get("phase"):
            phase = LOGIN["phase"]
            iteration = phase._current_iteration if phase else None  # pyright: ignore[reportPrivateUsage]
        if iteration:
            for fig in figures:
                with suppress_logging("vectice.models.iteration"):
                    iteration.log(fig)
                _logger.info(
                    f"Graph {fig.filename!r} logged in iteration {iteration.name!r}."  # pyright: ignore[reportAttributeAccessIssue]
                )

    def get_all_figures(self):
        """IPython event which mimics what is done by matplotlibs inline display event to get all active figures.
        This is a post execute event, this is why we suppress standard iteration logs and log the PIL Image.
        """
        from vectice.autolog.autolog_class import NOTEBOOK_CELLS
        from vectice.utils.code_parser import preprocess_code

        # TODO: H2o matplotlib integration is not supported yet for unsaved graphs
        if is_h2o:
            return

        cell_id = _get_cell_id(ipython)
        try:
            # remove possible false positives
            processed_code = preprocess_code(NOTEBOOK_CELLS[cell_id])
            # check if autolog was called in the current cell
            is_autolog_cell = bool(re.search(r"autolog\.|\.cell\(|\.notebook\(", processed_code))
            self._reset_for_new_cell(cell_id)
            # Get the list of active figure managers
            active_figures = Gcf.get_all_fig_managers()
            figures = []
            for fig_manager in active_figures:
                current_fig = fig_manager.canvas.figure
                if current_fig not in self.captured_figures:
                    # Convert the figure to a PNG in memory
                    buf = BytesIO()
                    current_fig.savefig(buf, format="png")

                    figure_title = current_fig.get_suptitle()
                    graph_name = f"{figure_title}.png" if figure_title else f"vect_plot_{uuid.uuid4().hex[-8:]}.png"
                    buf.seek(0)
                    image = Image.open(buf)

                    image.filename = graph_name
                    GRAPHS[cell_id]["displayed"].append(image)
                    self.captured_figures.add(current_fig)
                    figures.append(image)
            if self.is_inline and is_autolog_cell:
                self._log_figures(figures)
        except Exception:
            pass

    def patched_savefig(self, fname, *args, **kwargs):  # pyright: ignore[reportMissingParameterType]
        """A patched version of matplotlib's savefig function that tracks the file path."""
        try:
            cell_id = _get_cell_id(ipython)
            self._reset_for_new_cell(cell_id)
            current_fig = plt.gcf()

            if current_fig not in self.captured_figures:
                GRAPHS[cell_id]["saved"].append(fname)
                self.captured_figures.add(current_fig)
        except Exception:
            pass
        default_savefig(fname, *args, **kwargs)

    def _reset_for_new_cell(self, cell_id: str | None):
        """Reset the captured_figures set for a new cell."""
        if self.current_cell and cell_id != self.current_cell:
            self.captured_figures.clear()
            self.current_cell = cell_id
