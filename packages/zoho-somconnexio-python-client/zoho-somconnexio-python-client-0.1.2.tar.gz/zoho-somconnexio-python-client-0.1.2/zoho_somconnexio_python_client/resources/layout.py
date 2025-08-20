import os
import json
from time import time
from typing import Optional
from zoho_somconnexio_python_client.client import ZohoCRMClient


class ZohoCRMLayout(ZohoCRMClient):
    def __init__(self, module: str):
        super(ZohoCRMLayout, self).__init__("ZohoCRM.settings.layouts.READ")
        self.module = module
        self.layout_store = os.path.join(self._crm_store(), "layouts.json")

    @property
    def fields(self) -> list:
        layout = self.get_layout()
        return [field for section in layout["sections"] for field in section["fields"]]

    def _get_layout_from_store(self) -> Optional[dict]:
        if not os.path.isfile(self.layout_store):
            return

        with open(self.layout_store, "r", encoding="utf-8") as fp:
            try:
                layouts = json.load(fp)
                layout = layouts.get(self.module)

                if not layout:
                    return

                if layout["__time"] + 3600 < int(time()):
                    return

                return layout
            except json.decoder.JSONDecodeError:
                return

    def _layout_request_token(self) -> dict:
        res = self.get("/settings/layouts", {"module": self.module})
        layout = res["layouts"][0]
        layout["__time"] = int(time())

        return layout

    def get_layout(self) -> dict:
        layout = self._get_layout_from_store()
        if not layout:
            layout = self._layout_request_token()

            if os.path.isfile(self.layout_store):
                with open(self.layout_store, "r", encoding="utf-8") as fp:
                    layouts = json.load(fp)
            else:
                layouts = {}
            with open(self.layout_store, "w", encoding="utf-8") as fp:
                layouts[self.module] = layout
                json.dump(layouts, fp)

        return layout
