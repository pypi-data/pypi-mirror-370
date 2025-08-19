# lunaversex-genai

![PyPI Version](https://img.shields.io/pypi/v/lunaversex-genai)
![License](https://img.shields.io/pypi/l/lunaversex-genai)
![Python Version](https://img.shields.io/pypi/pyversions/lunaversex-genai)

**LunaVerseX Generative AI SDK for Python**

SDK oficial de **LunaVerseX** para integrar capacidades de **IA generativa** en aplicaciones Python.
Provee interfaces simples para chat, streaming, manejo de modelos y utilidades relacionadas.

📚 Documentación completa: [docs.lunaversex.com/sdks/genai](https://docs.lunaversex.com/sdks/genai)

---

## 🚀 Instalación

```bash
pip install lunaversex-genai
```

---

## ✨ Características

* 🔹 **Chat conversacional** con soporte para múltiples modelos.
* 🔹 **Streaming de respuestas** para baja latencia.
* 🔹 **Gestión de modelos disponibles**.
* 🔹 **Generación de texto simple o con razonamiento**.
* 🔹 **Extracción de uso de tokens**.
* 🔹 **Tipado completo** con soporte `py.typed`.

---

## 🧪 Modelos disponibles

| Modelo       | ID           | Soporta Reasoning | Descripción                                          |
| ------------ | ------------ | ----------------- | ---------------------------------------------------- |
| Lumi o1 Mini | lumi-o1-mini | ✅ Sí              | Modelo compacto para tareas generales.               |
| Lumi o1      | lumi-o1      | ❌ No              | Modelo equilibrado para uso general.                 |
| Lumi o1 Pro  | lumi-o1-pro  | ❌ No              | El modelo más creativo y sentimental.                |
| Lumi o1 High | lumi-o1-high | ✅ Sí              | Razonamiento profundo y rápido, código, matemáticas. |
| Lumi o3      | lumi-o3      | ✅ Sí (Nativo)     | El modelo más avanzado de LunaVerseX.                |

---

## 🧩 Funciones y Clases Exportadas

### Funciones Principales

* `genai.init(api_key: str, base_url: str = "https://api.lunaversex.com")`
  Inicializa el SDK con la clave API.

* `genai.chat(messages: List[Message], options: ChatOptions) -> ChatResponse`
  Envía un mensaje al modelo y recibe la respuesta completa.

* `genai.chatStream(messages: List[Message], options: ChatOptions) -> AsyncGenerator[StreamDelta, None]`
  Envía un mensaje al modelo y recibe la respuesta en streaming.

* `genai.listModels() -> ModelsResponse`
  Lista los modelos disponibles y sus características.

* `genai.generate(prompt: str, model: str = "lumi-o1") -> str`
  Genera texto simple desde un prompt.

* `genai.generateWithReasoning(prompt: str, effort: str = "medium", model: str = "lumi-o1-mini") -> Tuple[str, Optional[Dict]]`
  Genera texto incluyendo el proceso de razonamiento.

* `genai.tokens(response: ChatResponse) -> Usage`
  Extrae información de tokens de una respuesta.

* `genai.close()`
  Cierra las conexiones HTTP y libera recursos.

---

### Clases y Tipos de Datos

* `Message` – Representa un mensaje en la conversación.
* `ChatOptions` – Configuraciones para una petición de chat.
* `ChatResponse` – Respuesta completa de un chat.
* `StreamDelta` – Fragmentos recibidos durante el streaming.
* `Model` – Información de un modelo.
* `ModelsResponse` – Contenedor con todos los modelos disponibles.
* `ReasoningConfig` – Configuración de razonamiento para modelos.
* `ToolFunction` – Definición de función/herramienta para el modelo.
* `FileAttachment` – Archivos adjuntos a un mensaje.
* `Usage` – Información de uso de tokens.
* `ChatChoice` – Elección individual dentro de la respuesta de chat.

### Excepciones

* `LunaVerseXError` – Clase base para errores del SDK.
* `APIError` – Errores relacionados con solicitudes HTTP o la API.
* `ValidationError` – Error de validación en parámetros.
* `ConfigurationError` – Error de configuración del SDK.
* `ModelNotFoundError` – Modelo no encontrado o inválido.

---

## 🔧 Uso básico

### Configuración global

```python
from lunaversex-genai import genai

genai.init(api_key="your-api-key")
```

### Chat básico

```python
import asyncio
from lunaversex-genai import genai, Message, ChatOptions
genai.init(api_key="your-api-key")

async def run_chat():
    messages = [Message(role="user", content="Hola")]
    options = ChatOptions(model="lumi-o1")

    response = await genai.chat(messages, options)
    print("Respuesta:", response.choices[0].message.content)

    await genai.close()

asyncio.run(run_chat())
```

### Streaming de chat

```python
import asyncio
from lunaversex-genai import genai, Message, ChatOptions
genai.init(api_key="your-api-key")
async def run_stream():
    messages = [Message(role="user", content="Cuéntame una historia corta")]
    options = ChatOptions(model="lumi-o1-mini")

    async for delta in genai.chatStream(messages, options):
        if delta.type == "delta" and delta.content:
            print(delta.content, end="")
        elif delta.type == "end":
            print("\n[Fin del stream]")

    await genai.close()

asyncio.run(run_stream())
```

---

## 🔐 Seguridad

* **Nunca incluyas tu API Key directamente en el código fuente.**
* Usá variables de entorno (`os.environ["LUNAVERSEX_API_KEY"]`).
* El SDK no guarda ni expone claves sensibles.

---

## 📜 Licencia

Este proyecto está bajo licencia [Apache-2.0](LICENSE).

---

## 🧑‍💻 Autor

Desarrollado por **[LunaVerseX](https://www.lunaversex.com)**.
Mantenido por **[Joaco Heredia](https://github.com/joaco-heredia)**.

---

## 📈 Changelog

### v1.0.0 (2025-08-18)

* 🎉 Lanzamiento inicial del SDK Python.
* ✅ Implementación completa de `genai` con chat, streaming, manejo de modelos, generación con razonamiento y tokenización.
* 📝 Documentación inicial con ejemplos de uso.
