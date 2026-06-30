import socket
import threading
import csv
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

print("=" * 60)
print("      OPTIMUS AUTOMATE - NETWORK PORT SCANNER")
print("=" * 60)
print("Use only on systems you own or have permission to scan.\n")

target = input("Enter Target IP / Hostname: ")

try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print(Fore.RED + "[-] Invalid Hostname/IP")
    exit()

start_port = int(input("Start Port: "))
end_port = int(input("End Port: "))

timeout = 0.5

queue = Queue()
lock = threading.Lock()

results = []

common_services = {
    20: "FTP Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPC",
    119: "NNTP",
    123: "NTP",
    135: "MS RPC",
    137: "NetBIOS",
    138: "NetBIOS",
    139: "NetBIOS",
    143: "IMAP",
    161: "SNMP",
    179: "BGP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    587: "SMTP TLS",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt"
}


def banner(sock):
    try:
        sock.settimeout(1)
        return sock.recv(1024).decode(errors="ignore").strip()
    except:
        return ""


def scan(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((target_ip, port))

        if result == 0:

            service = common_services.get(port, "Unknown")

            try:
                service = socket.getservbyport(port)
            except:
                pass

            b = banner(sock)

            with lock:
                print(
                    Fore.GREEN +
                    f"[OPEN] Port {port:<5} Service: {service:<12} Banner: {b}"
                )

                results.append([port, service, b])

    finally:
        sock.close()


def worker():
    while True:
        port = queue.get()

        scan(port)

        queue.task_done()


thread_count = 100

for i in range(thread_count):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

print("\nScanning...\n")

for port in range(start_port, end_port + 1):
    queue.put(port)

queue.join()

print("\nScan Completed")

print(f"\nOpen Ports Found: {len(results)}")

save = input("\nSave results to CSV? (y/n): ")

if save.lower() == "y":

    filename = "scan_results.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["Port", "Service", "Banner"])

        writer.writerows(results)

    print(Fore.CYAN + f"\nResults saved to {filename}")

print("\nFinished.")