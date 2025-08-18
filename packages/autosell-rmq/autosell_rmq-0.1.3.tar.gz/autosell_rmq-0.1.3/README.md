# 🐰 RabbitMQ AsyncIO Consumer/Producer

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Простая в использовании библиотека для работы с RabbitMQ в асинхронном режиме на 
Python. Поддерживает идемпотентность, Dead Letter Queue (DLQ), автоматические ответы и graceful shutdown.

## 🚀 Особенности

- **🔄 Асинхронная обработка сообщений** с использованием `aio_pika`
- **🔁 Автоматические ответы** по `reply_to` с `correlation_id`
- **☠️ Dead Letter Queue (DLQ)** для обработки ошибок
- **🔂 Идемпотентность** - защита от повторной обработки сообщений
- **🔄 Retry механизм** с настраиваемым количеством попыток
- **🛡️ Graceful shutdown** с обработкой сигналов
- **📊 Подробное логирование** всех операций
- **🎯 Простой API** для быстрого старта

## 📦 Установка

```bash
pip install autosell-rmq
```

## 🏃‍♂️ Быстрый старт

### Consumer

```python
import asyncio
from autosell_rmq import RabbitMQConsumer

async def message_handler(message_data: dict) -> dict:
    """Ваш обработчик сообщений"""
    print(f"Получено: {message_data}")
    
    # Ваша бизнес-логика здесь
    result = {"processed": True, "data": message_data}
    
    return result

async def main():
    # Создаем consumer
    consumer = RabbitMQConsumer(
        connection_url="amqp://guest:guest@localhost/",
        queue_name="my_queue",
        dlq_name="my_queue_dlq"
    )
    
    # Устанавливаем обработчик
    consumer.set_message_handler(message_handler)
    
    try:
        # Запускаем (работает до Ctrl+C)
        await consumer.run_forever()
    finally:
        await consumer.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Producer

```python
import asyncio
from autosell_rmq import RabbitMQProducer

async def main():
    producer = RabbitMQProducer("amqp://guest:guest@localhost/")
    
    try:
        # Отправляем сообщение и ждем ответ
        response = await producer.send_message(
            queue_name="my_queue",
            message_data={"text": "Привет, мир!", "user_id": 123}
        )
        
        print(f"Ответ: {response}")
        # Вывод: {"success": True, "data": {...}, "correlation_id": "..."}
        
        # Отправляем без ожидания ответа
        correlation_id = await producer.send_fire_and_forget(
            queue_name="my_queue",
            message_data={"type": "notification", "text": "Уведомление"}
        )
        print(f"Отправлено: {correlation_id}")
        
    finally:
        await producer.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 Подробная документация

### RabbitMQConsumer

#### Параметры конструктора

```python
consumer = RabbitMQConsumer(
    connection_url="amqp://guest:guest@localhost/",  # URL подключения к RabbitMQ
    queue_name="main_queue",                         # Имя основной очереди
    dlq_name="dlq_queue",                           # Имя Dead Letter Queue
    max_retries=3                                    # Максимальное количество повторов
)
```

#### Методы

- **`set_message_handler(handler)`** - Устанавливает обработчик сообщений
- **`start_consuming()`** - Запускает обработку сообщений
- **`run_forever()`** - Запускает consumer с graceful shutdown
- **`stop()`** - Останавливает consumer программно
- **`close()`** - Закрывает соединение

### RabbitMQProducer

#### Параметры конструктора

```python
producer = RabbitMQProducer(
    connection_url="amqp://guest:guest@localhost/"   # URL подключения к RabbitMQ
)
```

#### Методы

- **`send_message(queue_name, message_data, wait_for_response=True, timeout=30.0)`** - Отправляет сообщение
- **`send_fire_and_forget(queue_name, message_data)`** - Отправляет без ожидания ответа
- **`close()`** - Закрывает соединение

## 🔧 Расширенные примеры

### Настройка обработчика с ошибками

```python
async def robust_handler(message_data: dict) -> dict:
    try:
        # Ваша бизнес-логика
        if message_data.get("simulate_error"):
            raise ValueError("Имитация ошибки")
        
        # Обработка данных
        result = process_business_logic(message_data)
        
        return {
            "success": True,
            "result": result,
            "processed_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        # Логируем ошибку - сообщение попадет в DLQ
        logging.error(f"Ошибка обработки: {e}")
        raise  # Перебрасываем для отправки в DLQ
    
    except Exception as e:
        # Неожиданная ошибка
        logging.error(f"Неожиданная ошибка: {e}")
        raise
```

### Использование с пулом соединений

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def consumer_context(queue_name: str):
    consumer = RabbitMQConsumer(queue_name=queue_name)
    consumer.set_message_handler(my_handler)
    
    try:
        await consumer.start_consuming()
        yield consumer
    finally:
        await consumer.close()

async def main():
    async with consumer_context("orders_queue") as consumer:
        # Consumer работает в контексте
        await consumer.run_forever()
```

### Batch обработка

```python
async def send_batch_messages():
    producer = RabbitMQProducer()
    
    try:
        # Отправляем несколько сообщений параллельно
        tasks = []
        for i in range(10):
            task = producer.send_message(
                "batch_queue",
                {"batch_id": "batch_001", "item": i, "data": f"item_{i}"}
            )
            tasks.append(task)
        
        # Ждем все ответы
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Ошибка в сообщении {i}: {response}")
            else:
                print(f"Ответ {i}: {response}")
                
    finally:
        await producer.close()
```

## 🔄 Идемпотентность

Библиотека автоматически обеспечивает идемпотентность обработки сообщений на основе `correlation_id`:

```python
# Первая отправка
response1 = await producer.send_message(
    "test_queue", 
    {"data": "test"}, 
    correlation_id="unique-id-123"
)

# Повторная отправка с тем же correlation_id
# Вернет тот же результат без повторной обработки
response2 = await producer.send_message(
    "test_queue", 
    {"data": "different data"}, 
    correlation_id="unique-id-123"
)

# response1 == response2
```

## ☠️ Dead Letter Queue (DLQ)

Сообщения автоматически попадают в DLQ в следующих случаях:

- Превышено максимальное количество попыток обработки
- Ошибка парсинга JSON
- Необработанное исключение в обработчике
- Отсутствие обработчика сообщений

Структура сообщения в DLQ:

```json
{
  "original_body": "...",
  "reason": "Превышено максимальное количество попыток: ...",
  "failed_at": "2024-01-15T10:30:00",
  "correlation_id": "...",
  "original_queue": "main_queue"
}
```
## ⚙️ Конфигурация

### Переменные окружения

```bash
export RABBITMQ_URL="amqp://user:pass@localhost:5672/vhost"
export QUEUE_NAME="my_app_queue"
export DLQ_NAME="my_app_dlq"
export MAX_RETRIES="5"
```

### Конфигурация через код

```python
import os

consumer = RabbitMQConsumer(
    connection_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/"),
    queue_name=os.getenv("QUEUE_NAME", "default_queue"),
    dlq_name=os.getenv("DLQ_NAME", "default_dlq"),
    max_retries=int(os.getenv("MAX_RETRIES", "3"))
)
```

## 📊 Мониторинг и логирование

Библиотека предоставляет подробное логирование:

```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Логи будут содержать:
# - Подключение к RabbitMQ
# - Обработка сообщений
# - Отправка ответов
# - Ошибки и перемещение в DLQ
# - Статистика идемпотентности
```
## 📝 Требования

- Python >=3.13,<4
- aio-pika
- RabbitMQ Server

## 📈 Changelog

### v1.0.0
- ✨ Первый релиз
- 🔄 Базовая функциональность Consumer/Producer
- 🔂 Поддержка идемпотентности
- ☠️ Dead Letter Queue
- 🛡️ Graceful shutdown

---

**Создано с ❤️ для разработчиков autosell.kz**
