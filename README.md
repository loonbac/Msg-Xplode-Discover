# MSG-XPLODE-DISCOVER
Este Script usa msg para enviar un mensaje a todos los equipos con windows con un usuario definido de tu red local.

## Instalación

Para ejecutar este script, necesitas tener Python instalado en tu máquina. Además, necesitamos la librería `psutil` para obtener información sobre las interfaces de red, que se puede instalar con `pip`.

```bash
pip install psutil
```

## Uso

```python
import subprocess
import socket
import psutil
import re
```

Primero, importamos los módulos necesarios para interactuar con la red, hacer pruebas de conectividad y manejar las direcciones IP.

### Función: `get_ip_addresses`

```python
def get_ip_addresses():
    #Obtener todas las IP de la Red
    ip_addresses = {}
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_addresses[interface] = addr.address
    return ip_addresses
```

Aquí creamos una función llamada `get_ip_addresses`. Lo que hace es obtener las direcciones IP de todas las interfaces de red de tu computadora. Para eso usamos `psutil.net_if_addrs()`, que nos devuelve las interfaces y sus direcciones. Filtramos por las que son de tipo IPv4 (direcciones como `192.168.x.x`) y las guardamos en un diccionario.

### Función: `ping_test`

```python
def ping_test(ip, interface_ip):
    #Prueba de PING a las interfaces para saber que interfaz tiene acceso a internet
    try:
        output = subprocess.run(["ping", "-S", interface_ip, "-n", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Error al hacer ping: {e}")
        return False
```

En esta función, hacemos una prueba de ping para saber si podemos acceder a Internet desde una interfaz específica. Usamos el comando `ping` con la opción `-S` para especificar la interfaz que vamos a usar. Si el ping es exitoso (si el código de retorno es `0`), devolvemos `True`, de lo contrario, devolvemos `False`.

### Función: `arp_a`

```python
def arp_a():
    #Ejecuto un arp -a para saber las ip de mi red local
    try:
        output = subprocess.run(["arp", "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return output.stdout
    except Exception as e:
        print(f"Error al ejecutar arp -a: {e}")
        return ""
```

Esta función ejecuta el comando `arp -a` en la terminal. Este comando nos devuelve una lista de las direcciones IP y sus correspondientes direcciones MAC en la red local. Usamos `subprocess.run` para ejecutar el comando y capturamos la salida.

### Función: `filter_arp_by_interface`

```python
def filter_arp_by_interface(arp_output, interface_ip):
    #Obtener ips que estan en mi misma subred
    subnet = '.'.join(interface_ip.split('.')[:-1]) + '.'
    filtered_ips = []
    for line in arp_output.splitlines():
        if subnet in line:
            match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
            if match:
                filtered_ips.append(match.group(0))
    
    return filtered_ips
```

Aquí filtramos las direcciones IP obtenidas por `arp -a` para quedarnos solo con las que están en la misma subred que la interfaz que estamos utilizando. Primero, extraemos la subred de la IP de la interfaz y luego buscamos direcciones IP que pertenezcan a esa subred usando una expresión regular.

### Función: `send_message`

```python
def send_message(ip, message):
    #Enviar un msg a las ips descubiertas
    try:
        output = subprocess.run(["msg", f"/SERVER:{ip}", "CAMBIA-ESTO-POR-TU-USUARIO-POR-DEFECTO-EN-TU-RED-LOCAL", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Error al enviar mensaje a {ip}: {e}")
        return False
```

En esta función, enviamos un mensaje a una IP específica usando el comando `msg` de Windows. El comando `msg` solo funciona en sistemas Windows y permite enviar mensajes a otras máquinas en la red. Si el mensaje se envía correctamente, la función devuelve `True`.

### Función Principal: `main`

```python
def main():
    #Iniciador
    ip_addresses = get_ip_addresses()
    ping_success = False
    successful_interface = None
    for interface, ip in ip_addresses.items():
        if ping_test("8.8.8.8", ip):
            print(f"Ping exitoso a 8.8.8.8 usando la interfaz {interface} con IP {ip}")
            ping_success = True
            successful_interface = ip
            break

    if not ping_success:
        print("No se pudo hacer ping a 8.8.8.8 usando ninguna interfaz.")
        return

    arp_output = arp_a()
    filtered_ips = filter_arp_by_interface(arp_output, successful_interface)
    
    print("\nRedes en la red local:")
    for ip in filtered_ips:
        print(ip)

    message = "print(Hola Mundo)"
    successful_ips = []

    for ip in filtered_ips:
        if send_message(ip, message):
            print(f"Mensaje enviado correctamente a {ip}")
            successful_ips.append(ip)
        else:
            print(f"No se pudo enviar el mensaje a {ip}")

    if successful_ips:
        print("\nMensajes enviados correctamente a las siguientes IPs:")
        for ip in successful_ips:
            print(ip)
    else:
        print("No se enviaron mensajes correctamente a ninguna IP.")
```

La función principal `main()` coordina todo el proceso. Primero, obtiene las IPs locales usando `get_ip_addresses`. Luego, realiza un ping a `8.8.8.8` (un servidor de Google) usando las diferentes interfaces para saber cuál tiene acceso a Internet. Si encuentra una interfaz con acceso, ejecuta el comando `arp -a` para obtener las IPs de la red local y las filtra usando la función `filter_arp_by_interface`.

Luego, intenta enviar un mensaje a cada una de las IPs descubiertas en la red local. Si el mensaje se envía correctamente, guarda esas IPs en una lista llamada `successful_ips` y las muestra al final.

### Ejecución del Script

Para ejecutar este script, simplemente corre la función `main()`.

```python
if __name__ == "__main__":
    main()
```

Este bloque asegura que el script se ejecute solo si lo estamos ejecutando directamente (no si lo estamos importando en otro archivo).

## Licencia

Este proyecto tiene una licencia [MIT](https://choosealicense.com/licenses/mit/).
