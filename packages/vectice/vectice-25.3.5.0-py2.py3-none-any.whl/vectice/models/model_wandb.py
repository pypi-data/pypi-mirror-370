from __future__ import annotations

import logging
import os
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd
import requests
from matplotlib import pyplot as plt
from PIL import Image

from vectice.models import AdditionalInfo, Framework
from vectice.models.dataset import TDerivedFrom
from vectice.models.model_exp_tracker import ModelExpTracker
from vectice.utils.common_utils import check_image_path

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import wandb
    from wandb.apis.public.runs import Run


class WandbModel(ModelExpTracker):
    def __init__(
        self,
        run_id: str,
        client: wandb.Api | None = None,
        url: str | None = None,
        derived_from: list[TDerivedFrom] | None = None,
        entity: str | None = None,
        project: str | None = None,
    ):
        """Args:
        run_id: Either 'entity/project/run_id' or just the run hash.
        client: Optional wandb.Api client. If not provided, a new one is created.
        url: Optional public or internal URL to the run.
        derived_from: Optional lineage.
        entity: Required if using short run_id.
        project: Required if using short run_id.
        """
        if client is None:
            client = wandb.Api()

        if run_id.count("/") == 2:
            run_path = run_id
        elif entity and project:
            run_path = f"{entity}/{project}/{run_id}"
        else:
            raise ValueError(
                "If 'run_id' is not in 'entity/project/run_id' format, you must also provide 'entity' and 'project'."
            )

        super().__init__(run_id=run_path, client=client, derived_from=derived_from)
        self.url = url
        self._run: Run = self.client.run(run_path)

    def get_metrics(self) -> Dict[str, Any]:
        excluded_keys = {"_step", "_runtime", "_timestamp", "_wandb"}
        metrics = {
            str(key): value
            for key, value in self._run.summary._json_dict.items()  # pyright: ignore[reportPrivateUsage]
            if isinstance(value, (int, float)) and key not in excluded_keys
        }
        return metrics

    def get_properties(self) -> Dict[str, Any]:
        props = dict(self._run.config)

        props.update(
            {
                "run_id": self._run.id,
                "state": self._run.state,
                "created_at": str(self._run.created_at),
                "project": self._run.project,
                "entity": self._run.entity,
                "tags": ", ".join(self._run.tags) if self._run.tags else None,
            }
        )

        if hasattr(self._run, "commit"):
            props["git_commit"] = self._run.commit
        if hasattr(self._run, "repo") and self._run.repo:
            props["git_repo_url"] = self._run.repo.get("repo_url")
            props["git_branch"] = self._run.repo.get("branch")
            props["git_tag"] = self._run.repo.get("tag")

        if self._run.sweep:
            props["sweep_id"] = self._run.sweep.id
            props["sweep_name"] = self._run.sweep.name
            props["sweep_config"] = str(self._run.sweep.config)

        return props

    def get_attachments(self) -> list[str] | None:
        try:

            output_dir = "wandb_attachments"
            os.makedirs(output_dir, exist_ok=True)
            image_paths = []

            # 1. Download image and media files
            for file in self._run.files():
                if file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                    downloaded = file.download(root=output_dir, replace=True)
                    if check_image_path(downloaded.name):
                        image_paths.append(downloaded.name)

            # 2. Download media images (e.g., wandb.Image(...))
            for file in self._run.files():
                if file.name.startswith("media/images/"):
                    try:
                        response = requests.get(file.url, stream=True)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content)).convert("RGB")
                        base_name = os.path.splitext(os.path.basename(file.name))[0]
                        save_path = os.path.join(output_dir, f"{base_name}.png")
                        image.save(save_path, format="PNG")
                        image_paths.append(save_path)
                    except Exception:
                        continue  # skip broken media

            # 3. Regenerate history plots per metric
            try:
                history_df = cast(pd.DataFrame, self._run.history(samples=1000, pandas=True))
                excluded_keys = {"_step", "_runtime", "_timestamp", "_wandb", "step"}

                metric_columns = [
                    col
                    for col in history_df.columns
                    if col not in excluded_keys and history_df[col].dtype.kind in {"i", "f"}
                ]

                for metric in metric_columns:
                    series = history_df[metric].dropna()
                    if series.empty:
                        continue

                    fig, ax = plt.subplots()
                    ax.plot(series.index, series.values)  # pyright: ignore
                    ax.set_title(metric)
                    ax.set_xlabel("Index (step/epoch)")
                    ax.set_ylabel("Value")
                    safe_name = metric.replace("/", "_")
                    chart_path = os.path.join(output_dir, f"{safe_name}.png")
                    fig.savefig(chart_path)
                    plt.close(fig)
                    image_paths.append(chart_path)

            except Exception as e:
                _logger.warning(f"Could not regenerate charts from history: {e}")

            return image_paths

        except Exception as e:
            _logger.warning(f"Could not extract W&B images: {e}")
            return None

    def get_name(self) -> str | None:
        return self._run.name

    def get_additional_info(self) -> AdditionalInfo:
        return AdditionalInfo(url=self.url, run=self.run, framework=Framework.WANDB)
