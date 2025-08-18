# Marketplace API Client

Python клиент для работы с API Marketplace (Encar и KBchachacha).

## Установка

```bash
pip install api-marketplace-client
```
## Использование

```python
from api_marketplace_client import EncarClient, KBchachachaClient

# Инициализация клиентов
encar = EncarClient(api_key="your_api_key")
kb_chachacha = KBchachachaClient(api_key="your_api_key")

# Получение списка брендов
brands = encar.get_brands()
print(brands)

# Получение автомобилей
cars = encar.get_cars(brand_code="001", page=1, per_page=20)
print(cars)
```

## API Reference

### Синхронная версия:
```python
from api_marketplace_client import EncarClient

# Обычное использование
client = EncarClient(api_key="your_key")
brands = client.get_brands()
client.close()

# Или с контекстным менеджером
with EncarClient(api_key="your_key") as client:
    brands = client.get_brands()
    cars = client.get_cars(brand_code="001", page=1)
```

### Асинхронная версия:
```python
from api_marketplace_client import AsyncEncarClient

async def main():
    # Обычное использование
    client = AsyncEncarClient(api_key="your_key")
    brands = await client.get_brands()
    await client.close()
    
    # Или с контекстным менеджером
    async with AsyncEncarClient(api_key="your_key") as client:
        brands = await client.get_brands()
        cars = await client.get_cars(brand_code="001", page=1)
```

### EncarClient
- `get_brands()` - Получить список всех брендов
- `get_brand(brand_code)` - Получить информацию о бренде
- `get_models(brand_code)` - Получить модели бренда
- `get_model(model_code, brand_code)` - Получить информацию о конкретной модели
- `get_generations(model_code, brand_code)` - Получить поколения модели
- `get_generation(generation_code, model_code, brand_code)` - Получить информацию о конкретном поколении
- `get_drive_types(generation_code, model_code, brand_code)` - Получить виды привода поколения
- `get_drive_type(drive_type_code, generation_code, model_code, brand_code)` - Получить информацию о конкретном виде привода
- `get_trims(drive_type_code, generation_code, model_code, brand_code)` - Получить список всех комплектаций
- `get_trim(trim_code, drive_type_code, generation_code, model_code, brand_code)` - Получить информацию о конкретной комплектации
- `get_fuel_types(brand_code, **filters)` - Получить список всех видов топлива
- `get_fuel_type(fuel_type_code, brand_code, **filters)` - Получить информацию о конкретном виде топлива
- `get_cars(brand_code, **filters)` - Получить список автомобилей
- `get_car(car_id)` - Получить информацию об автомобиле по ID

### KBchachachaClient
- `get_brands()` - Получить список всех брендов
- `get_brand(brand_code)` - Получить информацию о бренде
- `get_models(brand_code)` - Получить модели бренда
- `get_model(model_code, brand_code)` - Получить информацию о конкретной модели
- `get_generations(model_code, brand_code)` - Получить поколения модели
- `get_generation(generation_code, model_code, brand_code)` - Получить информацию о конкретном поколении
- `get_trims(generation_code, model_code, brand_code)` - Получить список всех комплектаций
- `get_trim(trim_code, generation_code, model_code, brand_code)` - Получить информацию о конкретной комплектации
- `get_fuel_types(brand_code, **filters)` - Получить список всех видов топлива
- `get_fuel_type(fuel_type_code, brand_code, **filters)` - Получить информацию о конкретном виде топлива
- `get_cars(brand_code, **filters)` - Получить список автомобилей
- `get_car(car_id)` - Получить информацию об автомобиле по ID


## Лицензия

MIT License