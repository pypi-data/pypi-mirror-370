import json
from datetime import datetime
from io import BytesIO
from typing import Optional

from django.db import models
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.io.backends import AbstractDataBackend, register

from ..utils import process_request
from .mixin import DataBackendMixin


@register("Fees", provider_key="ubs", save_data_in_import_source=True, passive_only=True)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    def __init__(
        self, import_credential: Optional[models.Model] = None, ubs_bank: Optional[models.Model] = None, **kwargs
    ):
        if not ubs_bank:
            raise ValueError("The ubs company objects needs to be passed to this backend")
        self.ubs_bank = ubs_bank
        if not import_credential or not import_credential.authentication_token:
            raise ValueError("UBS backend needs a valid import credential object")
        self.authentication_token = import_credential.authentication_token

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()

        mngt_fees_endpoint = "https://neo.ubs.com/api/ged-amc/external/fee/v1/management/{0}"
        perf_fees_endpoint = "https://neo.ubs.com/api/ged-amc/external/fee/v1/performance/{0}"
        if obj_external_ids:
            for external_id in obj_external_ids:
                start = kwargs.get("start", None)
                if not start:
                    start = global_preferences_registry.manager()["wbfdm__default_start_date_historical_import"]
                mngt_res = process_request(
                    self.authentication_token,
                    mngt_fees_endpoint.format(external_id),
                    {"fromDate": start.strftime("%Y-%m-%d"), "toDate": execution_date.strftime("%Y-%m-%d")},
                )
                perf_res = process_request(
                    self.authentication_token,
                    perf_fees_endpoint.format(external_id),
                    {"fromDate": start.strftime("%Y-%m-%d"), "toDate": execution_date.strftime("%Y-%m-%d")},
                )

                if mngt_res or perf_res:
                    res_json = {
                        "performance_fees": perf_res.get("fees", []),
                        "management_fees": mngt_res.get("fees", []),
                        "isin": external_id,
                    }

                    if res_json:
                        content_file = BytesIO()
                        content_file.write(json.dumps(res_json).encode())
                        file_name = f"ubs_fees_{external_id}_{start:%Y-%m-%d}_{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                        yield file_name, content_file
