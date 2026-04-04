"""
Wrapper de compatibilidad para exponer la app principal del juego.

La implementación completa del backend vive en ``simple_app.py``. Este
archivo mantiene el import path ``app.main:app`` para herramientas o
despliegues que ya lo estuvieran usando.
"""

from simple_app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8082, reload=False)
