from typing import Optional, Dict, Any

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..base import BaseClient, EncarMixin, KBchachachaMixin
from ..exceptions import APIError


class AsyncBaseAPIClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = "https://api.autovenil.ru"):
        super().__init__(api_key, base_url)
        self._session: Optional[ClientSession] = None
        self.timeout = ClientTimeout(total=30)

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            self._session = ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                connector=connector
            )

            return self._session

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self._build_url(endpoint)
        session = await self._get_session()

        try:
            async with session.request(method, url, **kwargs) as response:
                response_data = await response.json() if response.content_length else None
                self._handle_response_errors(response.status, response_data)
                return await response.json()

        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {str(e)}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AsyncEncarClient(AsyncBaseAPIClient, EncarMixin):
    """Клиент для работы с API Encar"""

    async def get_brands(self) -> Dict[str, Any]:
        """Получить список всех брендов"""
        return await self._request("GET", self._get_brands_endpoint())

    async def get_brand(self, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретном бренде"""
        return await self._request("GET", self._get_brand_endpoint(brand_code))

    async def get_models(self, brand_code: str) -> Dict[str, Any]:
        """Получить список всех моделей бренда"""
        return await self._request("GET", self._get_models_endpoint(brand_code))

    async def get_model(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретной модели"""
        params = {'brandCode': brand_code}
        return await self._request("GET", self._get_model_endpoint(model_code), params=params)

    async def get_generations(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список всех поколений модели"""
        params = {'brandCode': brand_code}
        return await self._request("GET", self._get_generations_endpoint(model_code), params=params)

    async def get_generation(self, generation_code: str, brand_code: str, model_code: str) -> Dict[str, Any]:
        """Получить информацию о конкретном поколении"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return await self._request("GET", self._get_generation_endpoint(generation_code), params=params)

    async def get_drive_types(self, generation_code: str, brand_code: str, model_code: str) -> Dict[str, Any]:
        """Получить список всех видов приводов поколения"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return await self._request("GET", self._get_drive_types_endpoint(generation_code), params=params)

    async def get_drive_type(
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
        return await self._request("GET", self._get_drive_type_endpoint(drive_type_code), params=params)

    async def get_trims(
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
        return await self._request("GET", self._get_trims_endpoint(drive_type_code), params=params)

    async def get_trim(
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
        return await self._request("GET", self._get_trim_endpoint(trim_code), params=params)

    async def get_fuel_types(
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
        return await self._request("GET", self._get_fuel_types_endpoint(), params=params)

    async def get_fuel_type(
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

        return await self._request("GET", self._get_fuel_type_endpoint(fuel_type_code), params=params)

    async def get_cars(
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

        return await self._request("GET", self._get_cars_endpoint(), params=params)

    async def get_car(self, car_id: str | int) -> Dict[str, Any]:
        """Получить информацию об автомобиле по ID"""
        return await self._request("GET", self._get_car_endpoint(car_id))


class AsyncKBchachachaClient(AsyncBaseAPIClient, KBchachachaMixin):
    """Клиент для работы с API KBchachacha"""

    async def get_brands(self) -> Dict[str, Any]:
        """Получить список всех производителей"""
        return await self._request("GET", self._get_brands_endpoint())

    async def get_brand(self, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о производителе"""
        return await self._request("GET", self._get_brand_endpoint(brand_code))

    async def get_models(self, brand_code: str) -> Dict[str, Any]:
        """Получить список моделей производителя"""
        return await self._request("GET", self._get_models_endpoint(brand_code))

    async def get_model(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о модели"""
        params = {'brandCode': brand_code}
        return await self._request("GET", self._get_model_endpoint(model_code), params=params)

    async def get_generations(self, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список поколений модели"""
        params = {'brandCode': brand_code}
        return await self._request("GET", self._get_generations_endpoint(model_code), params=params)

    async def get_generation(self, generation_code: str, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о поколении"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return await self._request("GET", self._get_generation_endpoint(generation_code), params=params)

    async def get_trims(self, generation_code: str,  model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить список модификаций поколения"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code
        }
        return await self._request("GET", self._get_trims_endpoint(generation_code), params=params)

    async def get_trim(self, trim_code: str, generation_code: str, model_code: str, brand_code: str) -> Dict[str, Any]:
        """Получить информацию о модификации"""
        params = {
            'brandCode': brand_code,
            'modelCode': model_code,
            'generationCode': generation_code
        }
        return await self._request("GET", self._get_trim_endpoint(trim_code), params=params)

    async def get_cars(
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

        return await self._request("GET", self._get_cars_endpoint(), params=params)

    async def get_car(self, car_id: str | int) -> Dict[str, Any]:
        """Получить детальную информацию об автомобиле"""
        return await self._request("GET", self._get_car_endpoint(car_id))
