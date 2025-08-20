from typing import Optional
from zoho_somconnexio_python_client.client import ZohoCRMClient
from zoho_somconnexio_python_client.resources.layout import ZohoCRMLayout


class ZohoCRMRecord(ZohoCRMClient):
    def __init__(self, module: str):
        super(ZohoCRMRecord, self).__init__()
        self.module = module

    def _layout_sanitization(self, data: dict) -> dict:
        layout_fields = ZohoCRMLayout(self.module).fields
        layout_data = {}

        for field, value in data.items():
            layout_field: Optional[dict] = None
            for candidate in layout_fields:
                if candidate["api_name"] == field:
                    layout_field = candidate
                    break

            if layout_field is None:
                print(f"Skip not in layout field {field}")
                continue

            if layout_field["data_type"] == "picklist":
                layout_value = None
                for candidate in layout_field["pick_list_values"]:
                    if value in [
                        candidate["display_value"],
                        candidate["reference_value"],
                        candidate["actual_value"],
                    ]:
                        layout_value = candidate

                if layout_value is None:
                    print(f"Skip not pickable value {value} for field {field}")
                    continue

            layout_data[field] = value

        return layout_data

    def list(self, fields: list, page: int = 1, per_page: int = 20) -> dict:
        endpoint = "/" + self.module
        params = {"fields": ",".join(fields), "page": page, "per_page": per_page}

        return self.get(endpoint, params)

    def create(
        self, data: dict, layout_id: Optional[int] = None, upsert: bool = False
    ) -> dict:
        endpoint = "/" + self.module

        if upsert:
            endpoint = endpoint + "/upsert"

        data = self._layout_sanitization(data)

        if layout_id is not None:
            data["Layout"] = +layout_id

        result = self.post(endpoint, data=data)
        return result["data"][0]

    def write(
        self, record_id: str, data: dict, layout_id: Optional[int] = None
    ) -> dict:
        endpoint = "/".join(("", self.module, str(record_id)))

        data = self._layout_sanitization(data)
        data["id"] = record_id

        if layout_id is not None:
            data["Layout"] = +layout_id

        result = self.put(endpoint, data=data)
        return result["data"][0]

    def drop(self, record_id: str) -> dict:
        endpoint = "/" + self.module
        return self.delete(endpoint, params={"ids": record_id})
