#!/bin/bash

# Script para crear la estructura de directorios del proyecto
# Autor: [Tu Nombre]
# Fecha: 6 de mayo de 2025

# Definir colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "Creando estructura de directorios para Tutti Frutti..."

# Crear directorios principales
mkdir -p game
mkdir -p routes
mkdir -p models
mkdir -p utils
mkdir -p static/{css,js,img}
mkdir -p templates
mkdir -p logs

# Crear archivos __init__.py para los paquetes
touch game/__init__.py
touch routes/__init__.py
touch models/__init__.py
touch utils/__init__.py

# Crear directorios static
mkdir -p static/css
mkdir -p static/js
mkdir -p static/img

echo -e "Estructura de directorios creada correctamente"
echo
echo -e "Directorios creados:"
echo -e "├── game/ - Componentes del juego"
echo -e "├── routes/ - Rutas API"
echo -e "├── models/ - Modelos de datos"
echo -e "├── utils/ - Utilidades"
echo -e "├── static/ - Archivos estáticos"
echo -e "│   ├── css/ - Estilos CSS"
echo -e "│   ├── js/ - Scripts JavaScript" 
echo -e "│   └── img/ - Imágenes"
echo -e "├── templates/ - Plantillas HTML"
echo -e "└── logs/ - Archivos de registro"
echo
echo -e "¡Listo para empezar a trabajar en el proyecto!"
