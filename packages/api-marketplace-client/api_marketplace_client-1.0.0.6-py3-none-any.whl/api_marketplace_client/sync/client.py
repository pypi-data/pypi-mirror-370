from typing import Optional, Dict, Any
from urllib3.util.retry import Retry

import requests
from requests.adapters import HTTPAdapter

from ..base import BaseClient, EncarMixin, KBchachachaMixin
from ..exceptions import APIError


class SyncClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = "https://api.autovenil.ru"):
        super().__init__(api_key, base_url)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._setup_retry_strategy()

    def _setup_retry_strategy(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self._build_url(endpoint)

        try:
            response = self.session.request(method, url, **kwargs)
            self._handle_response_errors(response.status_code, response.json() if response.content else None)
            return response.json()

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class EncarClient(SyncClient, EncarMixin):
    """Клиент для работы с API Encar"""

    def get_brands(self) -> Dict[str, Any]:
        """Получить список всех брендов"""
        return self._request("GET", self._get_brands_endpoint())

    def get_brand(self, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретном бренде"""
        return self._request("GET", self._get_brand_endpoint(brand_code))

    def get_models(self, brand_code: str) -> Dict[str, Any]:
        """Получить список всех моделей бренда"""
        return self._request("GET", self._get_models_endpoint(brand_code))

    def get_model(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретной модели"""
        params = {'brandCode': brand_code}
        return self._request("GET", self._get_model_endpoint(model_code), params=params)

    def get_generations(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список всех поколений модели"""
        params = {'brandCode': brand_code}
        return self._request("GET", self._get_generations_endpoint(model_code), params=params)

    def get_generation(self, generation_code: str, brand_code: str, model_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретном поколении"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return self._request("GET", self._get_generation_endpoint(generation_code), params=params)

    def get_drive_types(self, generation_code: str, brand_code: str, model_code: str) -> Dict[str, Any]:
        """Получить список всех видов приводов поколения"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return self._request("GET", self._get_drive_types_endpoint(generation_code), params=params)

    def get_drive_type(
            self,
            drive_type_code: str,
            generation_code: str,
            model_code: str,
            brand_code: str
    ) -> Dict[str, Any]:
        """Получить информацию о конкретном виде привода"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code,
            'generationCode': generation_code
        }
        return self._request("GET", self._get_drive_type_endpoint(drive_type_code), params=params)

    def get_trims(
            self,
            drive_type_code: str,
            generation_code: str,
            model_code: str,
            brand_code: str
    ) -> Dict[str, Any]:
        """Получить список всех комплектаций"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code,
            'generationCode': generation_code
        }
        return self._request("GET", self._get_trims_endpoint(drive_type_code), params=params)

    def get_trim(
            self,
            trim_code: str,
            drive_type_code: str,
            generation_code: str,
            model_code: str,
            brand_code: str
    ) -> Dict[str, Any]:
        """Получить информацию о конкретной комплектации"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code,
            'generationCode': generation_code,
            'driveTypeCode': drive_type_code
        }
        return self._request("GET", self._get_trim_endpoint(trim_code), params=params)

    def get_fuel_types(
            self,
            brand_code: str,
            model_code: Optional[str] = None,
            generation_code: Optional[str] = None,
            drive_type_code: Optional[str] = None,
            trim_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список всех видов топлива"""
        params = {'brandCode': brand_code}
        optional_params = {
            'modelCode': model_code,
            'generationCode': generation_code,
            'driveTypeCode': drive_type_code,
            'trimCode': trim_code
        }

        for key, value in optional_params.items():
            if value is not None:
                params[key] = value

        return self._request("GET", self._get_fuel_types_endpoint(), params=params)

    def get_fuel_type(
            self,
            fuel_type_code: str,
            brand_code: str,
            model_code: Optional[str] = None,
            generation_code: Optional[str] = None,
            drive_type_code: Optional[str] = None,
            trim_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить информацию о конкретном виде топлива"""
        params = {'brandCode': brand_code}
        optional_params = {
            'modelCode': model_code,
            'generationCode': generation_code,
            'driveTypeCode': drive_type_code,
            'trimCode': trim_code
        }

        for key, value in optional_params.items():
            if value is not None:
                params[key] = value

        return self._request("GET", self._get_fuel_type_endpoint(fuel_type_code), params=params)

    def get_cars(
            self,
            brand_code: str,
            page: int = 1,
            per_page: int = 20,
            model_code: Optional[str] = None,
            generation_code: Optional[str] = None,
            drive_type_code: Optional[str] = None,
            trim_code: Optional[str] = None,
            fuel_type_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список автомобилей с пагинацией"""
        params = {
            'brandCode': brand_code,
            'page': page,
            'perPage': per_page
        }

        optional_params = {
            'modelCode': model_code,
            'generationCode': generation_code,
            'driveTypeCode': drive_type_code,
            'trimCode': trim_code,
            'fuelTypeCode': fuel_type_code
        }

        for key, value in optional_params.items():
            if value is not None:
                params[key] = value

        return self._request("GET", self._get_cars_endpoint(), params=params)

    def get_car(self, car_id: str | int) -> Dict[str, Any]:
        """Получить информацию об автомобиле по ID"""
        return self._request("GET", self._get_car_endpoint(car_id))


class KBchachachaClient(SyncClient, KBchachachaMixin):
    """Клиент для работы с API KBchachacha"""

    def get_brands(self) -> Dict[str, Any]:
        """Получить список всех производителей"""
        return self._request("GET", self._get_brands_endpoint())

    def get_brand(self, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о производителе"""
        return self._request("GET", self._get_brand_endpoint(brand_code))

    def get_models(self, brand_code: str) -> Dict[str, Any]:
        """Получить список моделей производителя"""
        return self._request("GET", self._get_models_endpoint(brand_code))

    def get_model(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о модели"""
        params = {'brandCode': brand_code}
        return self._request("GET", self._get_model_endpoint(model_code), params=params)

    def get_generations(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список поколений модели"""
        params = {'brandCode': brand_code}
        return self._request("GET", self._get_generations_endpoint(model_code), params=params)

    def get_generation(self, generation_code: str, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о поколении"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return self._request("GET", self._get_generation_endpoint(generation_code), params=params)

    def get_trims(self, generation_code: str, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список модификаций поколения"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return self._request("GET", self._get_trims_endpoint(generation_code), params=params)

    def get_trim(self, trim_code: str, generation_code: str, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о модификации"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code,
            'generationCode': generation_code
        }
        return self._request("GET", self._get_trim_endpoint(trim_code), params=params)

    def get_cars(
            self,
            brand_code: str,
            page: int = 1,
            per_page: int = 40,
            model_code: Optional[str] = None,
            generation_code: Optional[int] = None,
            trim_code: Optional[int] = None,
            grade_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список автомобилей с фильтрацией"""
        params = {
            'brandCode': brand_code,
            'page': page,
            'perPage': per_page
        }

        optional_params = {
            'modelCode': model_code,
            'generationCode': generation_code,
            'trimCode': trim_code,
            'gradeCode': grade_code
        }

        for key, value in optional_params.items():
            if value is not None:
                params[key] = value

        return self._request("GET", self._get_cars_endpoint(), params=params)

    def get_car(self, car_id: str | int) -> Dict[str, Any]:
        """Получить детальную информацию об автомобиле"""
        return self._request("GET", self._get_car_endpoint(car_id))


# class MarketplaceAPI:
#     """Основной клиент для работы с API Marketplace"""
#
#     def __init__(self, api_key: str, base_url: str = "https://api.marketplace.com"):
#         self.encar = EncarClient(api_key, base_url)
#         self.kb_chachacha = KBchachachaClient(api_key, base_url)
#
#     def health_check(self) -> Dict[str, Any]:
#         """Проверка здоровья API"""
#         return self._request('GET', '/health')
#
#     def root(self) -> Dict[str, Any]:
#         """Корневой эндпоинт"""
#         return self._request('GET', '/')
