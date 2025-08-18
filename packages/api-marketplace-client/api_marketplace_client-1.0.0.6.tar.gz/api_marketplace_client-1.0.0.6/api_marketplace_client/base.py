from abc import ABC, abstractmethod
from typing import Dict, Any

from .exceptions import APIError, AuthError, ForbiddenError


class BaseClient(ABC):
    def __init__(self, api_key: str, base_url: str = "https://api.autovenil.ru"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def _handle_response_errors(self, status_code: int, response_data: Dict[str, Any] = None):
        if status_code == 401:
            raise AuthError("Invalid API key or unauthorized access")
        if status_code == 403:
            raise ForbiddenError("Invalid API key or unauthorized access")
        if status_code >= 400:
            error_msg = "Unknown error occurred"
            if response_data:
                error_msg = response_data.get('detail', error_msg)
            raise APIError(f"API Error {status_code}: {error_msg}", status_code)

    @abstractmethod
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        pass


class EncarMixin:
    def _get_brands_endpoint(self) -> str:
        return '/v1/encar/brands/'

    def _get_brand_endpoint(self, brand_code: str) -> str:
        return f'/v1/encar/brands/{brand_code}'

    def _get_models_endpoint(self, brand_code: str) -> str:
        return f'/v1/encar/brands/{brand_code}/models'

    def _get_model_endpoint(self, model_code: str) -> str:
        return f'/v1/encar/models/{model_code}'

    def _get_generations_endpoint(self, model_code: str) -> str:
        return f'/v1/encar/models/{model_code}/generations'

    def _get_generation_endpoint(self, generation_code: str) -> str:
        return f'/v1/encar/generations/{generation_code}'

    def _get_drive_types_endpoint(self, generation_code: str) -> str:
        return f'/v1/encar/generations/{generation_code}/drive-types'

    def _get_drive_type_endpoint(self, drive_type_code: str) -> str:
        return f'/v1/encar/drive-types/{drive_type_code}'

    def _get_trims_endpoint(self, drive_type_code: str) -> str:
        return f'/v1/encar/drive-types/{drive_type_code}/trims'

    def _get_trim_endpoint(self, trim_code: str) -> str:
        return f'/v1/encar/trims/{trim_code}'

    def _get_fuel_types_endpoint(self) -> str:
        return '/v1/encar/fuel-types/'

    def _get_fuel_type_endpoint(self, fuel_type_code: str) -> str:
        return f'/v1/encar/fuel-types/{fuel_type_code}'

    def _get_cars_endpoint(self) -> str:
        return '/v1/encar/cars/'

    def _get_car_endpoint(self, car_id: str | int) -> str:
        return f'/v1/encar/cars/{car_id}'


class KBchachachaMixin:
    def _get_brands_endpoint(self) -> str:
        return '/v1/kb-chachacha/brands/'

    def _get_brand_endpoint(self, brand_code: str) -> str:
        return f'/v1/kb-chachacha/brands/{brand_code}'

    def _get_models_endpoint(self, brand_code: str) -> str:
        return f'/v1/kb-chachacha/brands/{brand_code}/models'

    def _get_model_endpoint(self, model_code: str) -> str:
        return f'/v1/kb-chachacha/models/{model_code}'

    def _get_generations_endpoint(self, model_code: str) -> str:
        return f'/v1/kb-chachacha/models/{model_code}/generations'

    def _get_generation_endpoint(self, generation_code: str) -> str:
        return f'/v1/kb-chachacha/generations/{generation_code}'

    def _get_trims_endpoint(self, generation_code: str) -> str:
        return f'/v1/kb-chachacha/generations/{generation_code}/trims'

    def _get_trim_endpoint(self, trim_code: str) -> str:
        return f'/v1/kb-chachacha/trims/{trim_code}'

    def _get_cars_endpoint(self) -> str:
        return '/v1/kb-chachacha/cars/'

    def _get_car_endpoint(self, car_id: str | int) -> str:
        return f'/v1/kb-chachacha/cars/{car_id}'
