#!/bin/bash

echo "=== Limpiando puertos en uso ==="

# Verificar si el puerto 8082 está en uso
PORT=8082
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Puerto $PORT en uso por el proceso $PID. Intentando terminar..."
    kill -9 $PID
    echo "Proceso terminado."
else
    echo "El puerto $PORT no está en uso."
fi

# Verificar si el puerto 8081 está en uso (para el panel de administración)
PORT=8081
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Puerto $PORT en uso por el proceso $PID. Intentando terminar..."
    kill -9 $PID
    echo "Proceso terminado."
else
    echo "El puerto $PORT no está en uso."
fi

echo "Limpieza completada. Ahora puedes iniciar la aplicación."
