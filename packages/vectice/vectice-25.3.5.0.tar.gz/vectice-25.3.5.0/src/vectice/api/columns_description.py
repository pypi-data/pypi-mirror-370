from __future__ import annotations

import logging
from typing import BinaryIO

from vectice.api.http_error import HttpError
from vectice.api.rest_api import RestApi

_logger = logging.getLogger(__name__)


class ColumnsDescriptionApi(RestApi):
    def post_columns_description(self, id: str, file: tuple[str, tuple[str, BinaryIO]]):
        try:
            self._post_attachments(f"/api/columns-description/{id}", [file])
        except HttpError as e:
            self._httpErrorHandler.handle_post_http_error(e, "columns description", "update")
