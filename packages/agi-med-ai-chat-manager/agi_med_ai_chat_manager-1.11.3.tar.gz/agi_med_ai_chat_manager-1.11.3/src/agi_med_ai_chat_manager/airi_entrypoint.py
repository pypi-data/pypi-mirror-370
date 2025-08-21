import logging
from urllib.parse import urljoin

import requests

from .models import ServiceUnavailableException, UnsupportedModelException
from .open_router_entrypoint import OpenRouterEntryPoint


logger = logging.getLogger(__name__)


class AiriChatEntryPoint(OpenRouterEntryPoint):
    def __init__(
        self,
        model_id: str,
        api_key="hello_darkness",
        base_url="http://192.168.24.161:30050",
        emb_dim: int = 1024,
    ) -> None:
        server_url = urljoin(base_url, "v1")
        self.models_url = urljoin(base_url, "v1/models")
        self.check_current(model_id=model_id)
        super().__init__(model_id=model_id, base_url=server_url, api_key=api_key, emb_dim=emb_dim)

    def get_url(self):
        return self.models_url

    def check_current(self, model_id) -> None:
        model_list = self.get_available_models(self.models_url)

        if model_id not in model_list:
            logger.error("Модель '%s' не найдена. Доступные модели: %s", model_id, model_list)
            raise UnsupportedModelException(model_id, model_list)
        else:
            logger.info("Модель '%s' успешно найдена среди доступных.", model_id)

    @staticmethod
    def get_available_models(url) -> list[str]:
        response = requests.get(url)
        available_models = []
        if response.status_code == 200:
            models = response.json()
            for m in models["data"]:
                available_models.append(m["id"])
            logger.info("Доступные модели: %s", available_models)
            return available_models
        else:
            raise ServiceUnavailableException()
