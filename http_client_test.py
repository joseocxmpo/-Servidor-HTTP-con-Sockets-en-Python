"""
Cliente de prueba para el Servidor HTTP
Realiza múltiples solicitudes concurrentes para probar ThreadingMixIn

Universidad de Colima - Maestría en Tecnologías de Internet
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


HOST = 'localhost'
PORT = 8080


def make_http_request(path, method='GET'):
    """
    Realiza una solicitud HTTP y retorna la respuesta.
    
    Args:
        path: Ruta del recurso
        method: Método HTTP (GET o HEAD)
    
    Returns:
        dict: Diccionario con status_code, headers, y body
    """
    try:
        # Crear socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # Timeout de 10 segundos
            s.connect((HOST, PORT))
            
            # Construir solicitud HTTP
            request = f"{method} {path} HTTP/1.1\r\n"
            request += f"Host: {HOST}:{PORT}\r\n"
            request += "User-Agent: PythonClient/1.0\r\n"
            request += "Accept: */*\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            
            # Enviar solicitud
            s.sendall(request.encode('utf-8'))
            
            # Recibir respuesta
            response = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            # Parsear respuesta
            return parse_response(response)
            
    except socket.timeout:
        return {'error': 'Timeout', 'status_code': None}
    except ConnectionRefusedError:
        return {'error': 'Conexión rechazada - ¿El servidor está corriendo?', 'status_code': None}
    except Exception as e:
        return {'error': str(e), 'status_code': None}


def parse_response(response):
    """
    Parsea una respuesta HTTP.
    
    Args:
        response: Respuesta HTTP en bytes
    
    Returns:
        dict: Diccionario con componentes de la respuesta
    """
    try:
        # Separar headers del body
        header_end = response.find(b'\r\n\r\n')
        if header_end == -1:
            return {'error': 'Respuesta mal formada', 'status_code': None}
        
        header_section = response[:header_end].decode('utf-8', errors='ignore')
        body = response[header_end + 4:]
        
        # Parsear línea de estado
        lines = header_section.split('\r\n')
        status_line = lines[0]
        parts = status_line.split(' ', 2)
        
        if len(parts) >= 2:
            version = parts[0]
            status_code = int(parts[1])
            status_text = parts[2] if len(parts) > 2 else ''
        else:
            return {'error': 'Línea de estado inválida', 'status_code': None}
        
        # Parsear headers
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return {
            'status_code': status_code,
            'status_text': status_text,
            'version': version,
            'headers': headers,
            'body': body,
            'body_length': len(body)
        }
        
    except Exception as e:
        return {'error': str(e), 'status_code': None}


def test_single_request(path, method='GET'):
    """
    Prueba una solicitud individual y muestra el resultado.
    """
    print(f"\n{'='*60}")
    print(f"Probando: {method} {path}")
    print('='*60)
    
    start_time = time.time()
    result = make_http_request(path, method)
    elapsed = (time.time() - start_time) * 1000
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✓ Status: {result['status_code']} {result['status_text']}")
        print(f"✓ Versión: {result['version']}")
        print(f"✓ Content-Type: {result['headers'].get('Content-Type', 'N/A')}")
        print(f"✓ Content-Length: {result['headers'].get('Content-Length', 'N/A')}")
        print(f"✓ Tiempo de respuesta: {elapsed:.2f} ms")
        
        # Mostrar preview del body si es texto
        content_type = result['headers'].get('Content-Type', '')
        if 'text' in content_type or 'json' in content_type:
            body_preview = result['body'][:200].decode('utf-8', errors='ignore')
            if len(result['body']) > 200:
                body_preview += '...'
            print(f"\n--- Preview del contenido ---")
            print(body_preview)
    
    return result


def test_concurrent_requests(num_requests=10):
    """
    Prueba múltiples solicitudes concurrentes para verificar ThreadingMixIn.
    """
    print(f"\n{'='*60}")
    print(f"Probando {num_requests} solicitudes concurrentes")
    print('='*60)
    
    paths = ['/', '/about.html', '/api/data.json', '/styles.css', '/noexiste.html']
    
    start_time = time.time()
    successful = 0
    failed = 0
    
    def make_request(i):
        path = paths[i % len(paths)]
        result = make_http_request(path)
        return i, path, result
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        
        for future in as_completed(futures):
            i, path, result = future.result()
            if 'error' in result:
                failed += 1
                print(f"  [{i+1}] ❌ {path} - Error: {result['error']}")
            else:
                successful += 1
                print(f"  [{i+1}] ✓ {path} - Status: {result['status_code']}")
    
    elapsed = time.time() - start_time
    
    print(f"\n--- Resumen ---")
    print(f"Total de solicitudes: {num_requests}")
    print(f"Exitosas: {successful}")
    print(f"Fallidas: {failed}")
    print(f"Tiempo total: {elapsed:.2f} segundos")
    print(f"Solicitudes por segundo: {num_requests/elapsed:.2f}")


def main():
    print("=" * 60)
    print("  Cliente de Prueba para Servidor HTTP")
    print("  Universidad de Colima")
    print("=" * 60)
    
    print("\nAsegúrate de que el servidor esté corriendo en")
    print(f"http://{HOST}:{PORT}")
    
    input("\nPresiona Enter para iniciar las pruebas...")
    
    # Pruebas individuales
    print("\n" + "=" * 60)
    print("PRUEBAS INDIVIDUALES")
    print("=" * 60)
    
    # Probar página principal
    test_single_request('/')
    
    # Probar página about
    test_single_request('/about.html')
    
    # Probar archivo JSON
    test_single_request('/api/data.json')
    
    # Probar archivo CSS
    test_single_request('/styles.css')
    
    # Probar método HEAD
    test_single_request('/', method='HEAD')
    
    # Probar recurso no existente (404)
    test_single_request('/noexiste.html')
    
    # Probar método no permitido
    # (Nota: Nuestro servidor solo acepta GET y HEAD)
    
    # Pruebas de concurrencia
    print("\n" + "=" * 60)
    print("PRUEBAS DE CONCURRENCIA (ThreadingMixIn)")
    print("=" * 60)
    
    test_concurrent_requests(10)
    
    print("\n" + "=" * 60)
    print("PRUEBAS DE ESTRÉS (20 solicitudes)")
    print("=" * 60)
    
    test_concurrent_requests(20)
    
    print("\n✓ Pruebas completadas")


if __name__ == '__main__':
    main()
