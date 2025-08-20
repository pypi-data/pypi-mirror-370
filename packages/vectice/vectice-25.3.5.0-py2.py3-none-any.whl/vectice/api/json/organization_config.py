from __future__ import annotations

from vectice.api.json.json_type import TJSON


class OrganizationConfigOutput(TJSON):
    @property
    def df_statistics_row_threshold(self) -> int:
        return int(self["dfStatisticsRowThreshold"])

    @property
    def df_statistics_row_sample(self) -> int:
        return int(self["dfStatisticsSampleRows"])

    @property
    def df_statistics_colmns_threshold(self) -> int:
        return int(self["dfStatisticsMaxColumns"])


class OrgConfigOutput(TJSON):
    @property
    def configuration(self) -> OrganizationConfigOutput:
        return OrganizationConfigOutput(self["organization"]["configuration"])
