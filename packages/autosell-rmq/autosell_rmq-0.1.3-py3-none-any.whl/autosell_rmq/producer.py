import asyncio
import json
import logging
import uuid
from typing import Dict, Optional, Any

import aio_pika
from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Producer для тестирования consumer'а"""

    def __init__(self, connection_url: str = "amqp://guest:guest@localhost/"):
        self.connection_url = connection_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.response_queue: Optional[aio_pika.Queue] = None
        self.responses: Dict[str, Any] = {}

    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()

            # Создаем временную очередь для ответов
            self.response_queue = await self.channel.declare_queue(
                exclusive=True,
                auto_delete=True
            )

            # Слушаем ответы
            await self.response_queue.consume(self._handle_response, no_ack=True)

            logger.info("Producer подключен к RabbitMQ")

        except Exception as e:
            logger.error(f"Ошибка подключения producer к RabbitMQ: {e}")
            raise

    async def _handle_response(self, message: AbstractIncomingMessage):
        """Обрабатывает ответы от consumer'а"""
        try:
            response_data = json.loads(message.body.decode())
            correlation_id = response_data.get("correlation_id")

            if correlation_id:
                self.responses[correlation_id] = response_data
                logger.info(f"Получен ответ для {correlation_id}: {response_data}")

        except Exception as e:
            logger.error(f"Ошибка обработки ответа: {e}")

    async def send_message(
            self,
            queue_name: str,
            message_data: dict,
            wait_for_response: bool = True,
            timeout: float = 30.0,
            correlation_id: Optional[str] = None
    ) -> Optional[dict]:
        """Отправляет сообщение и ожидает ответ"""
        if not self.connection:
            await self.connect()

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        try:
            message_body = json.dumps(message_data)

            message = Message(
                message_body.encode(),
                correlation_id=correlation_id,
                reply_to=self.response_queue.name if wait_for_response else None,
                delivery_mode=DeliveryMode.PERSISTENT
            )

            await self.channel.default_exchange.publish(
                message,
                routing_key=queue_name
            )

            logger.info(
                f"Сообщение отправлено в {queue_name} с correlation_id: {correlation_id}")

            if wait_for_response:
                # Ожидаем ответ
                start_time = asyncio.get_event_loop().time()
                while correlation_id not in self.responses:
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        logger.warning(f"Timeout ожидания ответа для {correlation_id}")
                        return None

                    await asyncio.sleep(0.1)

                response = self.responses.pop(correlation_id)
                return response

            return {"correlation_id": correlation_id, "sent": True}

        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            raise

    async def send_fire_and_forget(self, queue_name: str, message_data: dict) -> str:
        """Отправляет сообщение без ожидания ответа"""
        response = await self.send_message(
            queue_name=queue_name,
            message_data=message_data,
            wait_for_response=False
        )
        return response["correlation_id"]

    async def close(self):
        """Закрывает соединение"""
        if self.connection:
            await self.connection.close()
            logger.info("Producer соединение закрыто")
