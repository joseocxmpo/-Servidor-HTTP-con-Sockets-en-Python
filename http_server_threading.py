"""
Servidor HTTP con ThreadingMixIn
Implementación del método GET siguiendo RFC 9110
Para Windows - usando hilos para concurrencia

Autor: Ejemplo para Maestría en Tecnologías de Internet
Universidad de Colima
"""

import socketserver
import os
import mimetypes
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

# Configuración del servidor
HOST = 'localhost'
PORT = 8080
DOCUMENT_ROOT = './www'  # Carpeta raíz para servir archivos

# Códigos de estado HTTP
HTTP_STATUS = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
}


class HTTPRequestHandler(socketserver.BaseRequestHandler):
    """
    Manejador de solicitudes HTTP.
    Procesa solicitudes GET y devuelve recursos estáticos.
    """
    
    def handle(self):
        """
        Método principal que se llama cuando llega una solicitud.
        """
        try:
            # Recibir datos del cliente (máximo 4KB para la solicitud)
            data = self.request.recv(4096).decode('utf-8', errors='ignore')
            
            if not data:
                return
            
            # Parsear la solicitud HTTP
            request_info = self.parse_request(data)
            
            if request_info is None:
                self.send_error(400, "Solicitud mal formada")
                return
            
            method, path, version = request_info
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"{self.client_address[0]}:{self.client_address[1]} - "
                  f"{method} {path}")
            
            # Solo aceptamos GET (y HEAD como bonus)
            if method == 'GET':
                self.handle_get(path)
            elif method == 'HEAD':
                self.handle_get(path, include_body=False)
            else:
                self.send_error(405, f"Método {method} no permitido")
                
        except Exception as e:
            print(f"Error procesando solicitud: {e}")
            self.send_error(500, "Error interno del servidor")
    
    def parse_request(self, data):
        """
        Parsea la línea de solicitud HTTP.
        Formato: METHOD /path HTTP/1.x
        
        Returns:
            tuple: (method, path, version) o None si hay error
        """
        lines = data.split('\r\n')
        if not lines:
            return None
        
        request_line = lines[0]
        parts = request_line.split(' ')
        
        if len(parts) != 3:
            return None
        
        method, path, version = parts
        
        # Decodificar caracteres URL-encoded
        path = unquote(path)
        
        # Extraer solo el path (sin query string)
        parsed = urlparse(path)
        path = parsed.path
        
        return method, path, version
    
    def handle_get(self, path, include_body=True):
        """
        Maneja solicitudes GET.
        
        Args:
            path: Ruta del recurso solicitado
            include_body: Si es False, solo envía headers (para HEAD)
        """
        # Prevenir directory traversal attacks
        if '..' in path:
            self.send_error(403, "Acceso prohibido")
            return
        
        # Si es la raíz, buscar index.html
        if path == '/':
            path = '/index.html'
        
        # Construir la ruta completa del archivo
        file_path = os.path.join(DOCUMENT_ROOT, path.lstrip('/'))
        file_path = os.path.normpath(file_path)
        
        # Verificar que el archivo esté dentro de DOCUMENT_ROOT
        if not file_path.startswith(os.path.normpath(DOCUMENT_ROOT)):
            self.send_error(403, "Acceso prohibido")
            return
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            self.send_error(404, f"Recurso no encontrado: {path}")
            return
        
        # Si es un directorio, buscar index.html
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, 'index.html')
            if not os.path.exists(file_path):
                self.send_error(404, "index.html no encontrado en el directorio")
                return
        
        # Leer y enviar el archivo
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determinar el tipo MIME
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Enviar respuesta exitosa
            self.send_response(200, content, content_type, include_body)
            
        except PermissionError:
            self.send_error(403, "Permiso denegado")
        except Exception as e:
            self.send_error(500, f"Error leyendo archivo: {e}")
    
    def send_response(self, status_code, body, content_type, include_body=True):
        """
        Envía una respuesta HTTP completa.
        
        Args:
            status_code: Código de estado HTTP
            body: Contenido del cuerpo (bytes)
            content_type: Tipo MIME del contenido
            include_body: Si incluir el cuerpo en la respuesta
        """
        status_text = HTTP_STATUS.get(status_code, 'Unknown')
        
        # Construir headers
        headers = [
            f"HTTP/1.1 {status_code} {status_text}",
            f"Date: {self.get_http_date()}",
            f"Server: PythonHTTP/1.0 (ThreadingMixIn)",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(body)}",
            "Connection: close",
            "",
            ""
        ]
        
        response = '\r\n'.join(headers).encode('utf-8')
        
        if include_body:
            response += body
        
        self.request.sendall(response)
    
    def send_error(self, status_code, message):
        """
        Envía una respuesta de error HTTP.
        
        Args:
            status_code: Código de estado HTTP
            message: Mensaje de error
        """
        status_text = HTTP_STATUS.get(status_code, 'Unknown')
        
        # Crear página HTML de error
        body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Error {status_code}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background-color: #f5f5f5;
        }}
        h1 {{ color: #d32f2f; }}
        .error-code {{ font-size: 72px; color: #333; }}
        .message {{ color: #666; }}
    </style>
</head>
<body>
    <div class="error-code">{status_code}</div>
    <h1>{status_text}</h1>
    <p class="message">{message}</p>
    <hr>
    <small>PythonHTTP/1.0 (ThreadingMixIn)</small>
</body>
</html>"""
        
        self.send_response(status_code, body.encode('utf-8'), 'text/html; charset=utf-8')
    
    def get_http_date(self):
        """
        Retorna la fecha actual en formato HTTP (RFC 7231).
        Ejemplo: Sun, 06 Nov 1994 08:49:37 GMT
        """
        now = datetime.now(timezone.utc)
        return now.strftime('%a, %d %b %Y %H:%M:%S GMT')


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor HTTP con soporte para múltiples hilos.
    Cada conexión se maneja en un hilo separado.
    """
    # Permitir reutilizar la dirección inmediatamente
    allow_reuse_address = True
    
    # Los hilos se cerrarán cuando el servidor principal termine
    daemon_threads = True


def create_sample_files():
    """
    Crea archivos de ejemplo para probar el servidor.
    """
    # Crear directorio www si no existe
    if not os.path.exists(DOCUMENT_ROOT):
        os.makedirs(DOCUMENT_ROOT)
    
    # Crear index.html
    index_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servidor HTTP - Universidad de Colima</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Servidor HTTP con Sockets</h1>
            <p>Maestría en Tecnologías de Internet - Programación Avanzada</p>
        </header>
        
        <main>
            <section class="info">
                <h2>Información del Servidor</h2>
                <ul>
                    <li><strong>Protocolo:</strong> HTTP/1.1</li>
                    <li><strong>Método implementado:</strong> GET</li>
                    <li><strong>Concurrencia:</strong> ThreadingMixIn (hilos)</li>
                    <li><strong>Plataforma:</strong> Windows</li>
                </ul>
            </section>
            
            <section class="links">
                <h2>Recursos de Prueba</h2>
                <ul>
                    <li><a href="/about.html">Página About</a></li>
                    <li><a href="/api/data.json">Datos JSON</a></li>
                    <li><a href="/images/logo.txt">Archivo de texto</a></li>
                    <li><a href="/noexiste.html">Página que no existe (404)</a></li>
                </ul>
            </section>
        </main>
        
        <footer>
            <p>Universidad de Colima - 2024</p>
        </footer>
    </div>
</body>
</html>"""
    
    with open(os.path.join(DOCUMENT_ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Crear styles.css
    styles_css = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    overflow: hidden;
}

header {
    background: #1a1a2e;
    color: white;
    padding: 30px;
    text-align: center;
}

header h1 {
    font-size: 2em;
    margin-bottom: 10px;
}

header p {
    color: #a0a0a0;
}

main {
    padding: 30px;
}

section {
    margin-bottom: 30px;
}

h2 {
    color: #333;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

ul {
    list-style: none;
}

li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}

a:hover {
    text-decoration: underline;
}

footer {
    background: #f5f5f5;
    padding: 20px;
    text-align: center;
    color: #666;
}"""
    
    with open(os.path.join(DOCUMENT_ROOT, 'styles.css'), 'w', encoding='utf-8') as f:
        f.write(styles_css)
    
    # Crear about.html
    about_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>About - Servidor HTTP</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Acerca del Servidor</h1>
        </header>
        <main>
            <section>
                <h2>Implementación</h2>
                <p>Este servidor HTTP está implementado usando el módulo <code>socketserver</code> 
                de Python con <code>ThreadingMixIn</code> para manejar múltiples conexiones 
                concurrentes usando hilos.</p>
                
                <h2 style="margin-top: 20px;">Características</h2>
                <ul>
                    <li>Soporte para método GET</li>
                    <li>Detección automática de tipos MIME</li>
                    <li>Manejo de errores HTTP (400, 403, 404, 405, 500)</li>
                    <li>Headers HTTP conformes a RFC 9110</li>
                    <li>Protección contra directory traversal</li>
                </ul>
            </section>
            <p style="margin-top: 20px;"><a href="/">← Volver al inicio</a></p>
        </main>
    </div>
</body>
</html>"""
    
    with open(os.path.join(DOCUMENT_ROOT, 'about.html'), 'w', encoding='utf-8') as f:
        f.write(about_html)
    
    # Crear directorio api y archivo JSON
    api_dir = os.path.join(DOCUMENT_ROOT, 'api')
    if not os.path.exists(api_dir):
        os.makedirs(api_dir)
    
    data_json = """{
    "servidor": "PythonHTTP",
    "version": "1.0",
    "metodos_soportados": ["GET", "HEAD"],
    "concurrencia": "ThreadingMixIn",
    "universidad": "Universidad de Colima",
    "materia": "Programación Avanzada"
}"""
    
    with open(os.path.join(api_dir, 'data.json'), 'w', encoding='utf-8') as f:
        f.write(data_json)
    
    # Crear directorio images y archivo de texto
    images_dir = os.path.join(DOCUMENT_ROOT, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    with open(os.path.join(images_dir, 'logo.txt'), 'w', encoding='utf-8') as f:
        f.write("Este es un archivo de texto de ejemplo.\nServidor HTTP - Universidad de Colima")
    
    print(f"✓ Archivos de ejemplo creados en '{DOCUMENT_ROOT}/'")


def main():
    """
    Función principal que inicia el servidor.
    """
    print("=" * 60)
    print("  Servidor HTTP con ThreadingMixIn")
    print("  Maestría en Tecnologías de Internet")
    print("  Universidad de Colima")
    print("=" * 60)
    
    # Crear archivos de ejemplo
    create_sample_files()
    
    # Crear e iniciar el servidor
    try:
        with ThreadedHTTPServer((HOST, PORT), HTTPRequestHandler) as server:
            print(f"\n✓ Servidor iniciado en http://{HOST}:{PORT}")
            print(f"✓ Sirviendo archivos desde: {os.path.abspath(DOCUMENT_ROOT)}")
            print(f"✓ Usando ThreadingMixIn (un hilo por conexión)")
            print("\nPresiona Ctrl+C para detener el servidor...\n")
            print("-" * 60)
            
            # Mantener el servidor corriendo
            server.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido por el usuario.")
    except OSError as e:
        if e.errno == 10048:  # Windows: puerto en uso
            print(f"\n✗ Error: El puerto {PORT} ya está en uso.")
            print(f"  Intenta con otro puerto o cierra la aplicación que lo usa.")
        else:
            raise


if __name__ == '__main__':
    main()
