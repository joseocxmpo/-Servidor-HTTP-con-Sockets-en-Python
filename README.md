# 🌐 Servidor HTTP con Sockets en Python

Implementación de un servidor HTTP usando sockets y `ThreadingMixIn` para manejar múltiples conexiones concurrentes.

**Universidad de Colima**  
Maestría en Tecnologías de Internet  
Programación Avanzada

---

## 📋 Descripción

Este proyecto implementa un servidor HTTP desde cero utilizando el módulo `socketserver` de Python. El servidor soporta el método GET siguiendo las especificaciones del [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html).

### Características

- ✅ Método **GET** completo (RFC 9110)
- ✅ Método **HEAD** 
- ✅ **ThreadingMixIn** para concurrencia (compatible con Windows)
- ✅ Detección automática de tipos MIME
- ✅ Manejo de errores HTTP (400, 403, 404, 405, 500)
- ✅ Protección contra ataques de directory traversal
- ✅ Headers HTTP estándar (Date, Server, Content-Type, Content-Length)

---

## 📁 Estructura del Proyecto

```
Sockets/
├── http_server_threading.py   # Servidor HTTP principal
├── http_client_test.py        # Cliente de pruebas
├── README.md                  # Este archivo
└── www/                       # Carpeta de archivos web (se crea automáticamente)
    ├── index.html
    ├── about.html
    ├── styles.css
    ├── api/
    │   └── data.json
    └── images/
        └── logo.txt
```

---

## 🚀 Requisitos

- Python 3.6 o superior
- Windows, Linux o macOS

No se requieren dependencias externas, solo la biblioteca estándar de Python.

---

## 💻 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

2. (Opcional) Verifica tu versión de Python:
```bash
python --version
```

---

## ▶️ Ejecución

### Iniciar el Servidor

```bash
python http_server_threading.py
```

Salida esperada:
```
============================================================
  Servidor HTTP con ThreadingMixIn
  Maestría en Tecnologías de Internet
  Universidad de Colima
============================================================
✓ Archivos de ejemplo creados en './www/'

✓ Servidor iniciado en http://localhost:8080
✓ Sirviendo archivos desde: C:\...\www
✓ Usando ThreadingMixIn (un hilo por conexión)

Presiona Ctrl+C para detener el servidor...
```

### Probar en el Navegador

Abre tu navegador y visita:
- http://localhost:8080 - Página principal
- http://localhost:8080/about.html - Página About
- http://localhost:8080/api/data.json - Datos JSON
- http://localhost:8080/styles.css - Archivo CSS

### Ejecutar Pruebas de Concurrencia

En una **nueva terminal** (mientras el servidor está corriendo):

```bash
python http_client_test.py
```

Esto ejecutará:
- Pruebas individuales de cada recurso
- Pruebas de concurrencia con 10 solicitudes simultáneas
- Pruebas de estrés con 20 solicitudes simultáneas

---

## 🔧 Configuración

Puedes modificar las siguientes variables en `http_server_threading.py`:

```python
HOST = 'localhost'    # Dirección del servidor
PORT = 8080           # Puerto (cambiar si está ocupado)
DOCUMENT_ROOT = './www'  # Carpeta raíz de archivos
```

---

## 📡 Ejemplo de Solicitud/Respuesta HTTP

### Solicitud GET
```http
GET /index.html HTTP/1.1
Host: localhost:8080
User-Agent: Mozilla/5.0
Accept: */*
```

### Respuesta
```http
HTTP/1.1 200 OK
Date: Mon, 25 Nov 2024 12:00:00 GMT
Server: PythonHTTP/1.0 (ThreadingMixIn)
Content-Type: text/html
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
...
</html>
```

---

## 🧪 Códigos de Estado Implementados

| Código | Descripción | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Recurso encontrado y enviado |
| 400 | Bad Request | Solicitud mal formada |
| 403 | Forbidden | Intento de acceso no autorizado |
| 404 | Not Found | Recurso no existe |
| 405 | Method Not Allowed | Método HTTP no soportado |
| 500 | Internal Server Error | Error del servidor |

---

## 🔒 Seguridad

El servidor incluye protección contra:
- **Directory Traversal**: Bloquea rutas con `..`
- **Acceso fuera de DOCUMENT_ROOT**: Verifica que los archivos estén dentro de la carpeta permitida

---

## 📚 Referencias

- [RFC 9110 - HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Python socketserver Documentation](https://docs.python.org/3/library/socketserver.html)
- [Python socket Documentation](https://docs.python.org/3/library/socket.html)

---

## 👨‍💻 Autor

Desarrollado para la materia de **Programación Avanzada**  
Maestría en Tecnologías de Internet  
Universidad de Colima

---

## 📄 Licencia

Este proyecto es para fines educativos.
