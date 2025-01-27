import socket
import threading
from queue import Queue

# Lock for printing to prevent jumbled output in multithreading
print_lock = threading.Lock()

# Function to scan a specific port
def scan_port(host, port):
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Set a timeout for the connection
            # Attempt to connect to the port
            if s.connect_ex((host, port)) == 0:
                with print_lock:
                    print(f"[OPEN] Port {port} is open on {host}")
            else:
                with print_lock:
                    print(f"[CLOSED] Port {port} is closed on {host}")
    except socket.error as e:
        with print_lock:
            print(f"[ERROR] Unable to scan port {port}: {e}")

# Worker function for threading
def worker(host, port_queue):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(host, port)
        port_queue.task_done()

# Main function to handle input and start scanning
def port_scanner():
    print("Python Port Scanner")
    print("===================")
    
    # Get target host and ports to scan
    host = input("Enter the target host (e.g., 192.168.1.1 or example.com): ").strip()
    port_range = input("Enter the port range to scan (e.g., 1-1024): ").strip()
    
    try:
        # Resolve host to an IP address
        target_ip = socket.gethostbyname(host)
        print(f"\nScanning target {host} ({target_ip})...\n")
    except socket.gaierror:
        print("[ERROR] Unable to resolve host. Please check the hostname.")
        return

    try:
        # Parse the port range
        start_port, end_port = map(int, port_range.split('-'))
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid port range. Please use the format 'start-end' (e.g., 1-1024).")
        return
    
    # Create a queue for ports
    port_queue = Queue()
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    # Number of threads
    num_threads = 50

    # Create and start threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(target_ip, port_queue))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("\nScan complete!")

if __name__ == "__main__":
    port_scanner()