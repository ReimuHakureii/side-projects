import socket
import threading
from queue import Queue
import time

# Lock for thread-safe output
print_lock = threading.Lock()

# Common ports for quick scanning
COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP Proxy",
}

# Function to scan a specific port
def scan_port(host, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                service = COMMON_PORTS.get(port, "Unknown Service")
                with print_lock:
                    print(f"[OPEN] {host}:{port} - {service}")
                return True, service
    except socket.error:
        pass
    return False, None

# Worker function for threading
def worker(host, port_queue, timeout, results):
    while not port_queue.empty():
        port = port_queue.get()
        is_open, service = scan_port(host, port, timeout)
        if is_open:
            results.append((port, service))
        port_queue.task_done()

# Main function to handle input and scanning
def port_scanner():
    print("Python Advanced Port Scanner")
    print("============================\n")
    
    # Get host(s) from the user
    hosts = input("Enter target host(s) (comma-separated, e.g., example.com, 192.168.1.1): ").strip().split(",")
    hosts = [host.strip() for host in hosts]
    
    # Ask for scan mode
    print("\nScan Mode:")
    print("1. Scan specific port")
    print("2. Scan range of ports")
    print("3. Scan common ports")
    scan_mode = input("Choose a scan mode (1/2/3): ").strip()
    
    # Handle port inputs based on mode
    ports = []
    if scan_mode == "1":
        port = int(input("Enter the specific port to scan: ").strip())
        ports = [port]
    elif scan_mode == "2":
        port_range = input("Enter the port range (e.g., 20-80): ").strip()
        start_port, end_port = map(int, port_range.split('-'))
        ports = list(range(start_port, end_port + 1))
    elif scan_mode == "3":
        ports = list(COMMON_PORTS.keys())
    else:
        print("[ERROR] Invalid scan mode.")
        return

    # Get thread count
    num_threads = int(input("Enter the number of threads (default: 50): ").strip() or 50)
    
    # Get timeout
    timeout = float(input("Enter the connection timeout in seconds (default: 1.0): ").strip() or 1.0)

    # Prepare for logging
    log_file = input("Enter the log file name (default: scan_results.txt): ").strip() or "scan_results.txt"
    
    # Perform the scan
    for host in hosts:
        print(f"\nStarting scan for {host}...\n")
        try:
            target_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print(f"[ERROR] Unable to resolve host: {host}")
            continue

        print(f"Resolved {host} to {target_ip}\n")
        port_queue = Queue()
        for port in ports:
            port_queue.put(port)

        # List to store results
        results = []

        # Create threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=worker, args=(target_ip, port_queue, timeout, results))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Display and log results
        with open(log_file, "a") as log:
            log.write(f"Results for {host} ({target_ip}):\n")
            if results:
                for port, service in sorted(results):
                    log.write(f"Port {port}: {service}\n")
                print(f"\nScan for {host} completed. {len(results)} open ports found. Results saved to {log_file}\n")
            else:
                log.write("No open ports found.\n")
                print(f"\nScan for {host} completed. No open ports found.\n")

if __name__ == "__main__":
    port_scanner()
