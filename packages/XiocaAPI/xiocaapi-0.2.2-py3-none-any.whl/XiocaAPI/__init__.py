import os
import json
import asyncio
from typing import List, Dict, Optional, Any, Literal

import requests
import aiohttp
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["assistant", "user", "system"]
    content: Optional[str] = None
    image_url: Optional[str] = None

class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = Field(None, alias="finish_reason")

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class APIResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None

class APIError(Exception): pass
class AuthenticationError(APIError): pass
class PermissionError(APIError): pass
class NotFoundError(APIError): pass

class _BaseHandler:
    def __init__(self, client):
        self._client = client

class ChatHandler(_BaseHandler):
    def create(self, *, model: str, messages: List[Dict[str, str]], **kwargs) -> APIResponse:
        payload = {"model": model, "messages": messages, **kwargs}
        response_data = self._client._request("post", "ai", json=payload)
        return APIResponse.model_validate(response_data)

class ImageHandler(_BaseHandler):
    def generate(self, *, model: str, prompt: str, **kwargs) -> APIResponse:
        messages = [{"role": "user", "content": prompt}]
        payload = {"model": model, "messages": messages, **kwargs}
        response_data = self._client._request("post", "ai", json=payload)
        return APIResponse.model_validate(response_data)

class AsyncChatHandler(_BaseHandler):
    async def create(self, *, model: str, messages: List[Dict[str, str]], **kwargs) -> APIResponse:
        payload = {"model": model, "messages": messages, **kwargs}
        response_data = await self._client._request("post", "ai", json=payload)
        return APIResponse.model_validate(response_data)

class AsyncImageHandler(_BaseHandler):
    async def generate(self, *, model: str, prompt: str, **kwargs) -> APIResponse:
        messages = [{"role": "user", "content": prompt}]
        payload = {"model": model, "messages": messages, **kwargs}
        response_data = await self._client._request("post", "ai", json=payload)
        return APIResponse.model_validate(response_data)

class XiocaAPI:
    chat: ChatHandler
    images: ImageHandler
    
    def __init__(self, *, api_key: Optional[str] = None, base_url: str = "https://xioca.live/api/"):
        if api_key is None: api_key = os.environ.get("XIOCA_API_KEY")
        if not api_key: raise AuthenticationError("Не предоставлен API ключ. Передайте его в конструктор или установите переменную окружения XIOCA_API_KEY.")
        self.api_key = api_key
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        self.chat = ChatHandler(self)
        self.images = ImageHandler(self)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        try:
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            detail = err.response.text
            if status_code == 401: raise AuthenticationError("Ошибка аутентификации. Проверьте ваш API ключ.") from err
            if status_code == 403: raise PermissionError("Доступ запрещен. Возможно, ваш аккаунт заблокирован.") from err
            if status_code == 404: raise NotFoundError(f"Ресурс или модель не найдены: {detail}") from err
            raise APIError(f"HTTP ошибка: {status_code} - {detail}") from err
        except requests.exceptions.RequestException as err:
            raise APIError(f"Ошибка подключения: {err}") from err

class AsyncXiocaAPI:
    chat: AsyncChatHandler
    images: AsyncImageHandler

    def __init__(self, *, api_key: Optional[str] = None, base_url: str = "https://xioca.live/api/"):
        if api_key is None: api_key = os.environ.get("XIOCA_API_KEY")
        if not api_key: raise AuthenticationError("Не предоставлен API ключ. Передайте его в конструктор или установите переменную окружения XIOCA_API_KEY.")
        self.api_key = api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None
        self.chat = AsyncChatHandler(self)
        self.images = AsyncImageHandler(self)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        session = await self._get_session()
        url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as err:
            if err.status == 401: raise AuthenticationError("Ошибка аутентификации. Проверьте ваш API ключ.") from err
            if err.status == 403: raise PermissionError("Доступ запрещен. Возможно, ваш аккаунт заблокирован.") from err
            if err.status == 404: raise NotFoundError(f"Ресурс или модель не найдены: {err.message}") from err
            raise APIError(f"HTTP ошибка: {err.status} - {err.message}") from err
        except aiohttp.ClientError as err:
            raise APIError(f"Ошибка подключения клиента: {err}") from err

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()