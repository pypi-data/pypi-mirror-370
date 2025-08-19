from contextlib import suppress

import pandas as pd
import requests
from django.db.models import Q
from dynamic_preferences.registries import global_preferences_registry
from wbfdm.models import Instrument


def get_timedelta_import_instrument_price():
    return global_preferences_registry.manager()["wbportfolio__timedelta_import_instrument_price"]


def process_request(authentication_token: str, endpoint: str | None = None, kwargs={}) -> pd.DataFrame:
    headers = {"Authorization": authentication_token}
    r = requests.get(endpoint, params=kwargs, headers=headers)
    if r.status_code == requests.codes.ok:
        with suppress(
            requests.exceptions.JSONDecodeError
        ):  # we catch any json decode error because the UBS api doesn't seem to respect HTTP status code rule (i.e. returns 200 even though the http content is malformed)
            r_json = r.json()
            if r_json.get("status", "") == "SUCCESS":
                return r_json
    raise ValueError(f"Issue while processing request: {r.content}")


def filter_active_instruments(_date, queryset=None):
    if not queryset:
        queryset = Instrument.objects
    queryset = queryset.filter(Q(delisted_date__isnull=True) | Q(delisted_date__gte=_date))
    queryset = queryset.filter(
        Q(refinitiv_mnemonic_code__isnull=False) | Q(refinitiv_identifier_code__isnull=False) | Q(isin__isnull=False)
    )
    return queryset.distinct()


def chunked_queryset(queryset, chunk_size):
    """Slice a queryset into chunks."""

    start_pk = 0
    queryset = queryset.order_by("pk")

    while True:
        # No entry left
        if not queryset.filter(pk__gt=start_pk).exists():
            break

        try:
            # Fetch chunk_size entries if possible
            end_pk = queryset.filter(pk__gt=start_pk).values_list("pk", flat=True)[chunk_size - 1]

            # Fetch rest entries if less than chunk_size left
        except IndexError:
            end_pk = queryset.values_list("pk", flat=True).last()

        yield queryset.filter(pk__gt=start_pk).filter(pk__lte=end_pk)

        start_pk = end_pk
