#!/bin/bash

echo "=== Inicializando Tutti Frutti ==="

# Crear estructura de directorios
mkdir -p static/css
mkdir -p static/js
mkdir -p static/img
mkdir -p templates

echo "✅ Estructura de directorios creada"

# Verificar si existe el archivo de configuración del juego
if [ ! -f "game_config.json" ]; then
    echo "Creando archivo de configuración predeterminado..."
    cat << 'EOCFG' > game_config.json
{
    "default_categories": [
        "Nombre",
        "Animal",
        "Fruta/Verdura",
        "País/Ciudad",
        "Objeto",
        "Comidas",
        "Apellidos",
        "Color"
    ],
    "default_timer": 60,
    "default_max_rounds": 5,
    "default_stop_mode": "individual",
    "default_auto_validate": true,
    "last_winner": {
        "name": "Sistema",
        "score": 100,
        "timestamp": 1744511212
    }
}
EOCFG
    echo "✅ Archivo de configuración creado"
fi

# Verificar si los archivos existen
if [ -f "static/css/styles-inference.css" ] && [ -f "static/css/styles-dark.css" ] && [ -f "static/css/toast.css" ]; then
    echo "✅ Archivos CSS ya existen"
else
    echo "❌ Faltan archivos CSS. Por favor, crea los archivos necesarios con los comandos proporcionados."
fi

if [ -f "static/js/auth.js" ] && [ -f "static/js/connect.js" ] && [ -f "static/js/i18n.js" ] && [ -f "static/js/script.js" ]; then
    echo "✅ Archivos JavaScript ya existen"
else
    echo "❌ Faltan archivos JavaScript. Por favor, crea los archivos necesarios con los comandos proporcionados."
fi

if [ -f "templates/index.html" ] && [ -f "templates/admin_stats.html" ]; then
    echo "✅ Archivos HTML ya existen"
else
    echo "❌ Faltan archivos HTML. Por favor, crea los archivos necesarios con los comandos proporcionados."
fi

echo "===================================="
echo "Inicialización completada. Para iniciar el sistema, ejecuta:"
echo "python app.py"
echo "===================================="
