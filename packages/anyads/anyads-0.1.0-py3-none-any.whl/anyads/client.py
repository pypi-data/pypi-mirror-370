# src/anyads/client.py
import asyncio
import hashlib
import logging
import platform
import uuid
from pathlib import Path
from typing import Callable, Coroutine, Any, Dict, Optional

import httpx
from getmac import get_mac_address

from .exceptions import InitializationError, APIError

logger = logging.getLogger("anyads.sdk")

BroadcastHandler = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]

_sdk_instance: Optional['PollingSDK'] = None

class PollingSDK:
    def __init__(self, api_key: str, interval_seconds: int = 300, sdk_version: str = "py-0.1.0"):
        if hasattr(self, '_initialized'):
            return

        if not api_key or not api_key.startswith("anyads_"):
            raise InitializationError("Неверный формат API ключа. Он должен начинаться с 'anyads_'.")
        
        self.api_key = api_key
        self.interval = interval_seconds
        self.sdk_version = sdk_version
        self.api_base_url = "https://api.anyads.online/v1"
        self._instance_id_path = Path("./.anyads_instance_id")

        self._fingerprint = self._get_environment_fingerprint()
        
        self._http_client: Optional[httpx.AsyncClient] = None
        
        self._polling_task: Optional[asyncio.Task] = None
        self._broadcast_handler: Optional[BroadcastHandler] = None
        self._initialized = True
        
        self._instance_id: Optional[str] = None

    async def _initialize_session(self):
        """Асинхронная инициализация, включая создание InstanceID и HTTP клиента."""
        if self._instance_id is None:
            self._instance_id = await self._get_or_create_instance_id()
        
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.api_base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-Instance-ID": self._instance_id,
                    "X-Environment-Fingerprint": self._fingerprint,
                    "User-Agent": f"AnyAdsPythonSDK/{self.sdk_version}",
                },
                timeout=20.0,
                follow_redirects=True,
            )
        logger.info(f"SDK AnyAds инициализирован. Instance ID: {self._instance_id}")

    async def _get_or_create_instance_id(self) -> str:
        """Читает Instance ID из файла или создает новый и регистрирует его."""
        try:
            if self._instance_id_path.exists():
                instance_id = self._instance_id_path.read_text().strip()
                if instance_id:
                    logger.debug(f"Найден существующий Instance ID: {instance_id}")
                    return instance_id
            
            new_id = f"inst_{uuid.uuid4()}"
            self._instance_id_path.write_text(new_id)
            logger.info(f"Создан новый Instance ID: {new_id}. Регистрируем на сервере...")
            
            await self._register_instance(new_id)
            return new_id
        except Exception as e:
            raise InitializationError(f"Не удалось прочитать, записать или зарегистрировать Instance ID: {e}")

    async def _register_instance(self, instance_id: str):
        """Отправляет запрос на регистрацию нового инстанса на сервер."""
        try:
            async with httpx.AsyncClient(base_url=self.api_base_url, timeout=20.0) as temp_client:
                response = await temp_client.post(
                    "/sdk/register-instance",
                    json={
                        "api_key": self.api_key,
                        "instance_id": instance_id,
                        "fingerprint": self._fingerprint,
                        "sdk_version": self.sdk_version
                    }
                )
                response.raise_for_status()
                logger.info(f"Новый Instance ID {instance_id} успешно зарегистрирован.")
        except httpx.HTTPStatusError as e:
            logger.critical(f"Не удалось зарегистрировать Instance ID! Сервер ответил с ошибкой {e.response.status_code}: {e.response.text}")
            raise APIError(f"Ошибка регистрации инстанса: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.critical(f"Сетевая ошибка при регистрации Instance ID: {e}")
            raise APIError(f"Сетевая ошибка регистрации инстанса") from e


    def _get_environment_fingerprint(self) -> str:
        try:
            mac = get_mac_address()
            hostname = platform.node()
            system_info = f"{platform.system()}-{platform.release()}"
            raw_fingerprint = f"{mac}-{hostname}-{system_info}"
            return hashlib.sha256(raw_fingerprint.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Не удалось сгенерировать полный отпечаток системы: {e}")
            return "fingerprint_generation_failed"

    async def _poll(self):
        """Основной цикл опроса Ad Engine."""
        await asyncio.sleep(5)
        while True:
            try:
                logger.debug("Проверка наличия рекламных задач...")
                if not self._http_client:
                    raise InitializationError("HTTP клиент не инициализирован.")

                response = await self._http_client.get(
                    "/tasks/bots/newsletters",
                    params={"sdk_version": self.sdk_version}
                )

                if update_header := response.headers.get("X-AnyAds-Update-Recommended"):
                    logger.warning(f"Доступна новая версия SDK: {update_header}. Пожалуйста, обновитесь: pip install --upgrade anyads")

                if response.status_code == 200:
                    ad_task = response.json()
                    if self._broadcast_handler:
                        logger.info(f"Получена новая рекламная задача: {ad_task.get('task_id')}")
                        asyncio.create_task(self._broadcast_handler(ad_task))
                    else:
                        logger.warning("Получена рекламная задача, но не зарегистрирован обработчик (on_broadcast_received). Задача будет проигнорирована.")
                elif response.status_code == 204:
                    logger.debug("Нет активных задач.")
                else:
                    response.raise_for_status()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 426:
                    logger.critical("Ваша версия SDK критически устарела и больше не поддерживается! Пожалуйста, обновитесь: pip install --upgrade anyads. Опрос остановлен.")
                    break
                logger.error(f"Ошибка API при опросе: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Сетевая ошибка при опросе Ad Engine: {e}")
            except Exception as e:
                logger.error(f"Непредвиденная ошибка в цикле опроса: {e}", exc_info=True)
            
            await asyncio.sleep(self.interval)

    def on_broadcast_received(self, handler: BroadcastHandler):
        """Декоратор для регистрации коллбэка."""
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("Обработчик должен быть асинхронной функцией (async def).")
        self._broadcast_handler = handler
        return handler

    async def process_verification_code(self, code: str) -> bool:
        """Отправляет верификационный код на сервер."""
        if not self._http_client:
            await self._initialize_session()
        
        if not code or not code.startswith('/verify_anyads_'):
            return False
        
        verification_code = code.lstrip('/')
        logger.info(f"Получена верификационная команда: {verification_code}")
        
        try:
            response = await self._http_client.post(
                "/sdk/verify", 
                json={"verification_code": verification_code}
            )
            response.raise_for_status()
            logger.info("Код верификации успешно отправлен на сервер.")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке кода верификации: {e}")
            return False

    async def start(self):
        """Инициализирует сессию и запускает фоновый опрос."""
        await self._initialize_session()
        if self._polling_task and not self._polling_task.done():
            logger.warning("Фоновый опрос уже запущен.")
            return
        self._polling_task = asyncio.create_task(self._poll())

    async def stop(self):
        """Останавливает фоновый опрос и закрывает соединения."""
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None
        if self._http_client:
            await self._http_client.aclose()
        logger.info("SDK AnyAds остановлен.")

def init(api_key: str, interval_seconds: int = 300, sdk_version: str = "py-0.1.0") -> PollingSDK:
    """Инициализирует и возвращает глобальный экземпляр SDK."""
    global _sdk_instance
    if _sdk_instance is None:
        _sdk_instance = PollingSDK(api_key, interval_seconds, sdk_version)
    return _sdk_instance

def get_sdk_instance() -> PollingSDK:
    """Возвращает инициализированный экземпляр SDK."""
    if _sdk_instance is None:
        raise InitializationError("SDK не был инициализирован. Вызовите anyads.init() при старте вашего приложения.")
    return _sdk_instance