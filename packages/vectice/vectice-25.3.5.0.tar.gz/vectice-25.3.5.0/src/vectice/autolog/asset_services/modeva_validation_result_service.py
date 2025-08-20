from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.service_types.modeva_types import ModevaType


class ModevaValidationResult:
    def __init__(self, key: str, asset: Any, data: dict):
        self._asset = asset
        self._key = key

    def get_asset(self):
        try:
            plot = self._get_plot(self._asset)
            table = self._get_table()
            return {
                "variable": self._key,
                "table": table,
                "plot": plot,
                "asset": self._asset,
                "asset_type": ModevaType.VALIDATION_RESULT,
            }
        except Exception:
            pass

    def _normalize_dataframe(self, dataframe: Any) -> Any:
        # normalize dataframe so FE can parse the df
        # this is for compare tests aswell
        if "diagnose_robustness" == self._asset.key:
            return dataframe.reset_index().melt(id_vars=["Repeats"], value_name="Value")
        if "reliability" in self._asset.key:
            # FE can't parse col name with a .
            try:
                dataframe.columns = dataframe.columns.str.replace("[^A-Za-z0-9_]+", "_", regex=True)
            except Exception:
                pass
            return dataframe
        return dataframe

    def _get_table(self) -> list:
        df = self._asset.table if hasattr(self._asset, "table") else None
        if df is None:
            return []
        multi_index = df.columns.nlevels > 1
        if not multi_index:
            return [self._normalize_dataframe(df)]
        dataframes = []
        # split multi-index into separate dfs
        for _, group in df.groupby(level=0, axis=1):
            dataframes.append(self._normalize_dataframe(group))
        return dataframes

    def _get_plot(self, result: Any) -> list[str]:
        # no plots
        if result.options is None:
            return []
        plot_suffixes = result.options.keys()
        # chart_id only appears in single plots
        multiple_plots = len(plot_suffixes) > 1 and "chart_id" not in plot_suffixes
        full_path = f"vectice_modeva/{result.key}"
        # temp_file_path = rf"{temp_dir.name}\{file_name}"
        result.plot_save(file_name=full_path, format="png", figsize=(6, 4))
        if multiple_plots:
            all_plot_paths = [f"{full_path}-{suffix}.png" for suffix in plot_suffixes]
            # full path will be a prefix
            return all_plot_paths
        return [full_path + ".png"]
