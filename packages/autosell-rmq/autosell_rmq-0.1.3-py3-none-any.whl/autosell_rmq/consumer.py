import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable, Awaitable

import aio_pika
from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage
from enum import Enum
from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingResult:
    status: MessageStatus
    result: Any = None
    error: Optional[str] = None
    processed_at: Optional[datetime] = None


class IdempotencyManager:
    """Менеджер для обеспечения идемпотентности обработки сообщений"""

    def __init__(self, ttl_seconds: int = 3600):
        self._processed_messages: Dict[str, ProcessingResult] = {}
        self._ttl_seconds = ttl_seconds

    def is_processed(self, correlation_id: str) -> bool:
        """Проверяет, было ли сообщение уже обработано"""
        if correlation_id in self._processed_messages:
            result = self._processed_messages[correlation_id]
            # Проверяем TTL
            if result.processed_at and datetime.now() - result.processed_at > timedelta(
                    seconds=self._ttl_seconds):
                del self._processed_messages[correlation_id]
                return False
            return True
        return False

    def get_result(self, correlation_id: str) -> Optional[ProcessingResult]:
        """Получает результат обработки сообщения"""
        return self._processed_messages.get(correlation_id)

    def mark_processing(self, correlation_id: str):
        """Отмечает сообщение как обрабатываемое"""
        self._processed_messages[correlation_id] = ProcessingResult(
            status=MessageStatus.PROCESSING,
            processed_at=datetime.now()
        )

    def mark_completed(self, correlation_id: str, result: Any):
        """Отмечает сообщение как успешно обработанное"""
        self._processed_messages[correlation_id] = ProcessingResult(
            status=MessageStatus.COMPLETED,
            result=result,
            processed_at=datetime.now()
        )

    def mark_failed(self, correlation_id: str, error: str):
        """Отмечает сообщение как неуспешно обработанное"""
        self._processed_messages[correlation_id] = ProcessingResult(
            status=MessageStatus.FAILED,
            error=error,
            processed_at=datetime.now()
        )


class RabbitMQConsumer:
    """Consumer с поддержкой DLQ, идемпотентности и автоответов"""

    def __init__(
            self,
            connection_url: str = "amqp://guest:guest@localhost/",
            queue_name: str = "main_queue",
            dlq_name: str = "dlq_queue",
            max_retries: int = 3
    ):
        self.connection_url = connection_url
        self.queue_name = queue_name
        self.dlq_name = dlq_name
        self.max_retries = max_retries

        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.dlq: Optional[aio_pika.Queue] = None

        self.idempotency_manager = IdempotencyManager()
        self.message_handler: Optional[Callable[[dict], Awaitable[Any]]] = None
        self._stop_event = asyncio.Event()
        self._consumer_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()

            # Настройка основной очереди
            self.queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": self.dlq_name,
                    "x-message-ttl": 300000,  # 5 минут TTL
                }
            )

            # Настройка DLQ
            self.dlq = await self.channel.declare_queue(
                self.dlq_name,
                durable=True
            )
            self.retry_exchange = await self.channel.declare_exchange(
                f"{self.queue_name}.retry",
                type=aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            # Привязываем к основной очереди с задержкой
            await self.channel.declare_queue(
                f"{self.queue_name}.retry.temp",
                durable=True,
                arguments={
                    "x-message-ttl": 5000,  # 5 секунд задержки
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": self.queue_name
                }
            )

            logger.info(
                f"Подключен к RabbitMQ. Очередь: {self.queue_name}, DLQ: {self.dlq_name}")

        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            raise

    def set_message_handler(self, handler: Callable[[dict], Awaitable[Any]]):
        """Устанавливает обработчик сообщений"""
        self.message_handler = handler

    async def _send_response(self, message: AbstractIncomingMessage,
                             response_data: Any):
        """Отправляет ответ на сообщение"""
        if not message.reply_to:
            logger.warning("reply_to не установлен, ответ не будет отправлен")
            return

        try:
            response_body = json.dumps({
                "success": True,
                "data": response_data,
                "correlation_id": message.correlation_id
            })

            response_message = Message(
                response_body.encode(),
                correlation_id=message.correlation_id,
                delivery_mode=DeliveryMode.PERSISTENT
            )

            await self.channel.default_exchange.publish(
                response_message,
                routing_key=message.reply_to
            )

            logger.info(
                f"Ответ отправлен в {message.reply_to} с correlation_id: {message.correlation_id}")

        except Exception as e:
            logger.error(f"Ошибка отправки ответа: {e}")

    async def _send_error_response(self, message: AbstractIncomingMessage, error: str):
        """Отправляет ответ с ошибкой"""
        if not message.reply_to:
            return

        try:
            response_body = json.dumps({
                "success": False,
                "error": error,
                "correlation_id": message.correlation_id
            })

            response_message = Message(
                response_body.encode(),
                correlation_id=message.correlation_id,
                delivery_mode=DeliveryMode.PERSISTENT
            )

            await self.channel.default_exchange.publish(
                response_message,
                routing_key=message.reply_to
            )

            logger.info(f"Ответ с ошибкой отправлен в {message.reply_to}")

        except Exception as e:
            logger.error(f"Ошибка отправки ответа с ошибкой: {e}")

    async def _move_to_dlq(self, message: AbstractIncomingMessage, reason: str):
        """Перемещает сообщение в DLQ"""
        try:
            dlq_body = json.dumps({
                "original_body": message.body.decode(),
                "reason": reason,
                "failed_at": datetime.now().isoformat(),
                "correlation_id": message.correlation_id,
                "original_queue": self.queue_name
            })

            dlq_message = Message(
                dlq_body.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                headers={"x-death-reason": reason}
            )

            await self.channel.default_exchange.publish(
                dlq_message,
                routing_key=self.dlq_name
            )

            logger.warning(f"Сообщение перемещено в DLQ. Причина: {reason}")

        except Exception as e:
            logger.error(f"Ошибка перемещения в DLQ: {e}")

    async def _process_message(self, message: AbstractIncomingMessage):
        """Обрабатывает входящее сообщение"""
        correlation_id = message.correlation_id

        try:
            # Проверка идемпотентности
            if correlation_id and self.idempotency_manager.is_processed(correlation_id):
                result = self.idempotency_manager.get_result(correlation_id)
                logger.info(f"Сообщение {correlation_id} уже обработано")

                if result.status == MessageStatus.COMPLETED:
                    await self._send_response(message, result.result)
                elif result.status == MessageStatus.FAILED:
                    await self._send_error_response(message, result.error)

                await message.ack()
                return

            # Отмечаем как обрабатываемое
            if correlation_id:
                self.idempotency_manager.mark_processing(correlation_id)

            # Парсим сообщение
            try:
                message_data = json.loads(message.body.decode())
            except json.JSONDecodeError as e:
                error_msg = f"Ошибка парсинга JSON: {e}"
                logger.error(error_msg)

                if correlation_id:
                    self.idempotency_manager.mark_failed(correlation_id, error_msg)

                await self._send_error_response(message, error_msg)
                await self._move_to_dlq(message, error_msg)
                await message.ack()
                return

            # Обрабатываем сообщение
            if not self.message_handler:
                error_msg = "Обработчик сообщений не установлен"
                logger.error(error_msg)

                if correlation_id:
                    self.idempotency_manager.mark_failed(correlation_id, error_msg)

                await self._send_error_response(message, error_msg)
                await message.reject()
                return

            # Вызываем обработчик
            result = await self.message_handler(message_data)

            # Отмечаем как успешно обработанное
            if correlation_id:
                self.idempotency_manager.mark_completed(correlation_id, result)

            # Отправляем ответ
            await self._send_response(message, result)
            await message.ack()

            logger.info(f"Сообщение {correlation_id} успешно обработано")

        except Exception as e:
            error_msg = f"Ошибка обработки сообщения: {e}"
            logger.error(error_msg)

            if correlation_id:
                self.idempotency_manager.mark_failed(correlation_id, error_msg)

            # Проверяем количество попыток
            retry_count = 0
            if message.headers and "x-retry-count" in message.headers:
                retry_count = int(message.headers["x-retry-count"])

            if retry_count < self.max_retries:
                logger.info(f"Повторная попытка {retry_count + 1}/{self.max_retries}")

                new_headers = dict(message.headers) if message.headers else {}
                new_headers["x-retry-count"] = retry_count + 1

                retry_message = Message(
                    message.body,
                    correlation_id=message.correlation_id,
                    reply_to=message.reply_to,
                    headers=new_headers,
                    delivery_mode=DeliveryMode.PERSISTENT
                )

                # Отправляем в retry очередь с задержкой
                await self.channel.default_exchange.publish(
                    retry_message,
                    routing_key=f"{self.queue_name}.retry.temp"
                )

                await message.ack()
            else:
                # Максимальное количество попыток достигнуто
                await self._send_error_response(message, error_msg)
                await self._move_to_dlq(message,
                                        f"Превышено максимальное количество попыток: {error_msg}")
                await message.ack()

    async def start_consuming(self):
        """Запускает обработку сообщений"""
        if not self.connection:
            await self.connect()

        await self.queue.consume(self._process_message, no_ack=False)
        logger.info("Consumer запущен и ожидает сообщения...")

    async def run_forever(self):
        """Запускает consumer и работает до получения сигнала остановки"""
        await self.start_consuming()

        # Настраиваем обработку сигналов
        import signal

        def signal_handler(signum, _):
            logger.info(f"Получен сигнал {signum}, начинаем graceful shutdown...")
            self.stop()

        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("Consumer работает. Нажмите Ctrl+C для остановки...")

        # Ожидаем сигнал остановки
        await self._stop_event.wait()
        logger.info("Consumer остановлен")

    def stop(self):
        """Останавливает consumer"""
        logger.info("Инициирована остановка consumer'а...")
        self._stop_event.set()

    async def close(self):
        """Закрывает соединение"""
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

        if self.connection:
            await self.connection.close()
            logger.info("Соединение с RabbitMQ закрыто")
