import subprocess
import socket
import psutil
import re

def get_ip_addresses():
    #Obtener todas las IP de la Red
    ip_addresses = {}
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_addresses[interface] = addr.address
    return ip_addresses

def ping_test(ip, interface_ip):
    #Prueba de PING a las interfaces para saber que interfaz tiene acceso a internet
    try:
        output = subprocess.run(["ping", "-S", interface_ip, "-n", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Error al hacer ping: {e}")
        return False

def arp_a():
    #Ejecuto un arp -a para saber las ip de mi red local
    try:
        output = subprocess.run(["arp", "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return output.stdout
    except Exception as e:
        print(f"Error al ejecutar arp -a: {e}")
        return ""

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

def send_message(ip, message):
    #Enviar un msg a las ips descubiertas
    try:
        output = subprocess.run(["msg", f"/SERVER:{ip}", "CAMBIA-ESTO-POR-TU-USUARIO-POR-DEFECTO-EN-TU-RED-LOCAL", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Error al enviar mensaje a {ip}: {e}")
        return False

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

if __name__ == "__main__":
    main()