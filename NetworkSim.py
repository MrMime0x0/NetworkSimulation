import random
import time
import sqlite3
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading

# Database functions
def init_db():
    conn = sqlite3.connect('network_events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, event_type TEXT, lan_ip TEXT, wan_ip TEXT, details TEXT)''')
    conn.commit()
    conn.close()

def insert_event(event_type, lan_ip, wan_ip, event_details):
    conn = sqlite3.connect('network_events.db')
    c = conn.cursor()
    c.execute("INSERT INTO events (event_type, lan_ip, wan_ip, details) VALUES (?, ?, ?, ?)", 
              (event_type, lan_ip, wan_ip, event_details))
    conn.commit()
    conn.close()

def fetch_events():
    conn = sqlite3.connect('network_events.db')
    c = conn.cursor()
    c.execute("SELECT event_type, lan_ip, wan_ip, details FROM events")
    events = c.fetchall()
    conn.close()
    return events

# Event classes
class Event:
    def __init__(self, lan_ip, wan_ip, details):
        self.lan_ip = lan_ip
        self.wan_ip = wan_ip
        self.details = details

class AttackEvent(Event):
    def __init__(self, lan_ip, wan_ip, details):
        super().__init__(lan_ip, wan_ip, details)
        self.event_type = 'Attack'

class ServerEvent(Event):
    def __init__(self, lan_ip, wan_ip, details):
        super().__init__(lan_ip, wan_ip, details)
        self.event_type = 'Server'

class PacketEvent(Event):
    def __init__(self, lan_ip, wan_ip, details):
        super().__init__(lan_ip, wan_ip, details)
        self.event_type = 'Packet'

class ServiceEvent(Event):
    def __init__(self, lan_ip, wan_ip, details):
        super().__init__(lan_ip, wan_ip, details)
        self.event_type = 'Service'

# Network functions
def generate_random_ip(subnet):
    return f"{subnet}.{random.randint(1, 254)}"

def generate_random_wan_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def segregate_network():
    # Example subnets
    return ['192.168.1', '192.168.2', '192.168.3']

# GUI class
class NetworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Simulation")
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.update_graph()

    def update_graph(self):
        events = fetch_events()
        self.ax.clear()
        
        attack_x, attack_y = [], []
        server_x, server_y = [], []
        packet_x, packet_y = [], []
        service_x, service_y = [], []

        for i, (event_type, lan_ip, wan_ip, details) in enumerate(events):
            if event_type == 'Attack':
                attack_x.append(i)
                attack_y.append(1)
            elif event_type == 'Server':
                server_x.append(i)
                server_y.append(1)
            elif event_type == 'Packet':
                packet_x.append(i)
                packet_y.append(1)
            elif event_type == 'Service':
                service_x.append(i)
                service_y.append(1)
        
        self.ax.plot(attack_x, attack_y, 'ro', label='Attack Event')
        self.ax.plot(server_x, server_y, 'bo', label='Server Event')
        self.ax.plot(packet_x, packet_y, 'go', label='Packet Event')
        self.ax.plot(service_x, service_y, 'yo', label='Service Event')

        self.ax.legend()
        self.canvas.draw()

def log_event(event, gui):
    insert_event(event.event_type, event.lan_ip, event.wan_ip, event.details)
    gui.update_graph()

def generate_traffic(gui):
    subnets = segregate_network()
    services = ['RDP', 'SSH', 'FTP', 'SFTP', 'HTTP', 'HTTPS', 'POP3', 'SMTP']
    while True:
        event_type = random.choice(['Attack', 'Server', 'Packet', 'Service'])
        subnet = random.choice(subnets)
        lan_ip = generate_random_ip(subnet)
        wan_ip = generate_random_wan_ip()

        if event_type == 'Attack':
            event = AttackEvent(lan_ip, wan_ip, "Simulated attack event.")
        elif event_type == 'Server':
            event = ServerEvent(lan_ip, wan_ip, "Server event occurred.")
        elif event_type == 'Packet':
            event = PacketEvent(lan_ip, wan_ip, "Packet event logged.")
        else:
            service = random.choice(services)
            event = ServiceEvent(lan_ip, wan_ip, f"Accessed {service} service.")
        
        log_event(event, gui)
        time.sleep(random.uniform(0.1, 1.0))  # Simulate varying traffic rates

def run_simulation(gui):
    init_db()
    threading.Thread(target=generate_traffic, args=(gui,), daemon=True).start()

# Main execution
if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    gui = NetworkGUI(root)
    run_simulation(gui)
    root.mainloop()
