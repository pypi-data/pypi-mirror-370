# Zafiro API Provider 🐍

Cliente API moderno y asíncrono para interactuar de forma sencilla e intuitiva con la API de Zafiro, permitiendo construir peticiones de forma fluida y pitónica.

## ✨ Características

- **Interfaz Fluida**: Construye endpoints encadenando atributos (`api.recurso.subrecurso`).
- **Asíncrono**: Basado en [httpx](https://www.python-httpx.org/) para un alto rendimiento.
- **Gestión Automática de Conexiones**: Usa `async with` para manejar el ciclo de vida del cliente.
- **Integrado**: Manejo de errores y autenticación básica listos para usar.

## 📦 Instalación

```bash
pip install zafiro-api-provider
```

## 🚀 Uso Rápido

La forma recomendada de usar el cliente es dentro de un bloque `async with` para gestionar la conexión automáticamente.

```python
import asyncio
from zafiro_api import ZafiroApiProvider  # Cambia esto por el nombre de tu paquete

async def main():
    # Inicializa el cliente con tus credenciales y la URL base de la API
    async with ZafiroApiProvider(
        base_url="https://tu-instancia.zafiro.com/api/v1",
        user="TU_USUARIO",
        password="TU_CONTRASEÑA"
    ) as api:
        try:
            # Listar recursos (GET /transactions/wellParameters.json)
            print("Listando parámetros...")
            params = {"well_id": "pozo-ejemplo-01"}
            all_params = await api.transactions.wellParameters.index(params=params)
            print("Parámetros encontrados:", all_params)

            # Crear un recurso (POST /transactions/wellParameters.json)
            print("\nCreando un nuevo parámetro...")
            new_param_data = {"name": "Presión", "value": 1500}
            created_param = await api.transactions.wellParameters.post(data=new_param_data)
            print("Parámetro creado:", created_param)

        except Exception as e:
            print(f"Ha ocurrido un error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 API en Resumen

### Inicialización

```python
api = ZafiroApiProvider("URL_BASE", "USUARIO", "CONTRASEÑA")
```

### Peticiones

Las peticiones se forman encadenando los recursos y finalizando con una acción:

```python
await api.recurso.subrecurso.accion(*args)
```

### Acciones Disponibles

- `.index(params: dict = None)`: **GET** a una lista de recursos.
- `.get(resource_id: str)`: **GET** a un recurso específico.
- `.post(data: dict = None)`: **POST** para crear un recurso.
- `.put(resource_id: str, data: dict = None)`: **PUT** para actualizar un recurso.
- `.delete(resource_id: str)`: **DELETE** para eliminar un recurso.
