import httpx
from typing import List, Optional, Dict, Any

# Clase auxiliar que construye dinámicamente la ruta del endpoint y ejecuta la acción.
class Endpoint:
    def __init__(self, api_provider: 'ZafiroApiProvider', path_parts: List[str]):
        self._api = api_provider
        self._path_parts = path_parts

    def __getattr__(self, name: str) -> 'Endpoint':
        """Permite encadenar atributos para construir la ruta (ej: api.transactions.wellParameters)."""
        new_path_parts = self._path_parts + [name]
        return Endpoint(self._api, new_path_parts)

    def _get_full_path(self, resource_id: Optional[str] = None) -> str:
        path = "/".join(self._path_parts)
        if resource_id:
            return f"{path}/{resource_id}"
        return path

    # Métodos de acción (GET, POST, etc.) que ejecutan la petición final.
    async def index(self, params: Optional[Dict[str, Any]] = None) -> Any:
        full_path = self._get_full_path()
        return await self._api._request("GET", full_path, params=params)

    async def get(self, resource_id: str) -> Any:
        full_path = self._get_full_path(resource_id)
        return await self._api._request("GET", full_path)

    async def post(self, data: Optional[Dict[str, Any]] = None) -> Any:
        full_path = self._get_full_path()
        return await self._api._request("POST", full_path, json=data)

    async def put(self, resource_id: str, data: Optional[Dict[str, Any]] = None) -> Any:
        full_path = self._get_full_path(resource_id)
        return await self._api._request("PUT", full_path, json=data)

    async def delete(self, resource_id: str) -> None:
        full_path = self._get_full_path(resource_id)
        return await self._api._request("DELETE", full_path)


class ZafiroApiProvider:
    """
    Un proveedor API para interactuar con Zafiro.
    Maneja la comunicación HTTP, autenticación y la construcción ergonómica de endpoints.
    """
    def __init__(self, base_url: str, user: str, password: str):
        self.base_url = base_url.rstrip('/')
        auth = httpx.BasicAuth(username=user, password=password)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            auth=auth
        )

    async def _request(self, method: str, path: str, **kwargs):
        """Método central que realiza todas las peticiones HTTP a la API."""
        url = f"/{path.lstrip('/')}.json"
        try:
            response = await self.client.request(method=method, url=url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Sin detalles adicionales."
            try:
                error_body = e.response.json()
                error_detail = str(error_body)
            except ValueError:
                error_detail = e.response.text
            raise Exception(f"Error de API: {e.response.status_code}. Detalles: {error_detail}") from e
        except httpx.RequestError as e:
            raise Exception(f"Error de solicitud: {str(e)}") from e
        except ValueError as e:
            raise Exception("Error: Respuesta JSON inválida de la API") from e

    def __getattr__(self, name: str) -> Endpoint:
        """Punto de entrada para la construcción dinámica de rutas."""
        return Endpoint(self, [name])

    async def aclose(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    # --- Métodos originales para retrocompatibilidad ---
    async def index(self, endpoint: str, params: dict = None):
        return await self._request("GET", endpoint, params=params)

    async def get(self, endpoint: str, resource_id: str):
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("GET", full_path)

    async def post(self, endpoint: str, data: dict = None):
        return await self._request("POST", endpoint, json=data)

    async def put(self, endpoint: str, resource_id: str, data: dict = None):
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("PUT", full_path, json=data)

    async def delete(self, endpoint: str, resource_id: str):
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("DELETE", full_path)