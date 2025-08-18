from __future__ import annotations

import re
from http import HTTPStatus
from typing import Any, Mapping, Sequence

from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from zut.db import Db


class DataView(View):
    db: Db
    sql: str
    params: Mapping[str,Any]|Sequence[Any]|None
    paginate = False

    def get_sql_and_params(self):
        sql = self.sql
        params = getattr(self, 'params', None)
        return sql, params
    
    def get(self, request: HttpRequest, *args, **kwargs):
        sql, params = self.get_sql_and_params()

        if self.paginate or 'limit' in request.GET or 'offset' in request.GET:
            limit = request.GET.get('limit')
            if not limit:
                return JsonResponse({"error": "Parameter \"limit\" must be set"}, status=HTTPStatus.BAD_REQUEST)
            if not re.match(r'^\d+$', limit):
                return JsonResponse({"error": "Parameter \"limit\" is not an integer"}, status=HTTPStatus.BAD_REQUEST)
            limit = int(limit)

            offset = request.GET.get('offset')
            if not offset:
                return JsonResponse({"error": "Parameter \"offset\" must be set"}, status=HTTPStatus.BAD_REQUEST)
            if not re.match(r'^\d+$', offset):
                return JsonResponse({"error": "Parameter \"offset\" is not an integer"}, status=HTTPStatus.BAD_REQUEST)
            offset = int(offset)

            rows, total = self.db.get_paginated_dicts(sql, params, limit=limit, offset=offset)
            return JsonResponse({"rows": rows, "total": total})

        else:
            rows = self.db.get_dicts(sql, params)
            return JsonResponse({'rows': rows})
