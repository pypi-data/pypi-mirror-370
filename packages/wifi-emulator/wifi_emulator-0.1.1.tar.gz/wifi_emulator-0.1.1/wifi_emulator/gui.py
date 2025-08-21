import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext

class WiFi_Emulator:
    def __init__(self, root):
        check_sudo()

        log_dir = "/var/log/wifi-emulator"
        os.makedirs(log_dir, exist_ok=True)

        self.root = root
        self.root.title("WiFi Emulator")
        self.root.geometry("600x750")
        self.root.configure(bg="#1e1e1e")

        style = ttk.Style()
        style.configure("Custom.TButton",
            foreground="#ffffff",
            background="#005f73", 
            font=("Segoe UI", 10, "bold"),
            # padding=8,
            borderwidth=1,
            focusthickness=3,
            focuscolor="#ffffff",
            relief="groove"
        )

        style.map("Custom.TButton",
            background=[("active", "#0a9396")], 
            foreground=[("disabled", "#888888")]
        )

        self.main_label_section()
        self.config_section()
        self.interface_section()
        self.service_section()
        self.wifite_section()
        self.utilities_section()
        self.log_area()
    
    def log(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def main_label_section(self):
        l = tk.LabelFrame(self.root, text="♒ Instructions", bg="#1e1e1e", fg="white")
        l.pack(fill="x", padx=10, pady=5)
        tk.Label(l, text=" Run buttons in sequense, check help for details.", bg="#1e1e1e", fg="white").grid(row=0, column=0, pady=10)

    def config_section(self):
        f = tk.LabelFrame(self.root, text="⚙️ Config Files", bg="#1e1e1e", fg="white")
        f.pack(fill="x", padx=10, pady=5)

        ttk.Button(f, text="🛠 Generate AP Conf", style="Custom.TButton", command=self.generate_ap_conf).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(f, text="📝 Edit ap.conf", style="Custom.TButton", command=lambda: self.edit_conf("ap.conf")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(f, text="🛠 Generate Client Conf", style="Custom.TButton", command=self.generate_client_conf).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(f, text="📝 Edit client.conf", style="Custom.TButton", command=lambda: self.edit_conf("client.conf")).grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def interface_section(self):
        v = tk.LabelFrame(self.root, text="🌐 Virtual Wireless Interfaces", bg="#1e1e1e", fg="white")
        v.pack(fill="x", padx=10, pady=5)

        ttk.Button(v, text="➕ Create Interfaces", style="Custom.TButton", command=self.interfaces_create).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(v, text="🔍 Status", style="Custom.TButton", command=self.interfaces_status).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    def service_section(self):
        s = tk.LabelFrame(self.root, text="📡 Services", bg="#1e1e1e", fg="white")
        s.pack(fill="x", padx=10, pady=5)

        ttk.Button(s, text="▶ Start AP", style="Custom.TButton", command=self.accesspoint_start).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(s, text="🔍 AP Status", style="Custom.TButton", command=self.accesspoint_status).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(s, text="▶ Start Client", style="Custom.TButton", command=self.client_start).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(s, text="🔍 Client Status", style="Custom.TButton", command=self.client_status).grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def wifite_section(self):
        w = tk.LabelFrame(self.root, text="🎯 WPA Capturinge & Cracking", bg="#1e1e1e", fg="white")
        w.pack(fill="x", padx=10, pady=5)

        # ttk.Button(w, text="🚀 Run Wifite", style="Custom.TButton", command=self.run_wifite).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(w, text="🚀 Open Root Terminal", style="Custom.TButton", command=self.run_shell).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    def utilities_section(self):
        u = tk.LabelFrame(self.root, text="🧰 Utilities", bg="#1e1e1e", fg="white")
        u.pack(fill="x", padx=10, pady=5)

        ttk.Button(u, text="❓ Help", style="Custom.TButton", command=self.show_help).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(u, text="🔄 Reset", style="Custom.TButton", command=self.reset_app).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(u, text="❌ Close", style="Custom.TButton", command=self.close_app).grid(row=0, column=2, padx=5, pady=5)

    def log_area(self):
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=12, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff"
        )
        self.text_area.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10))

    def generate_ap_conf(self):
        conf = """interface=wlan0
driver=nl80211
ssid=CyberWifi
channel=6
hw_mode=g
auth_algs=1
wpa=2
wpa_passphrase=sunshine
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP"""
        with open("/var/log/wifi-emulator/ap.conf", "w") as f:
            f.write(conf)
        self.log("✅ AP config created.")

    def generate_client_conf(self):
        conf = """ctrl_interface=/var/run/wpa_supplicant
network={
    ssid="CyberWifi"
    psk="sunshine"
}
"""
        with open("/var/log/wifi-emulator/client.conf", "w") as f:
            f.write(conf)
        self.log("✅ Client config created.")

    def edit_conf(self, filename):
        win = tk.Toplevel(self.root)
        win.title(f"Edit: {filename}")
        win.geometry("700x500")

        with open(f"/var/log/wifi-emulator/{filename}", "r") as f:
            content = f.read()

        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, bg="black", fg="white", insertbackground="white")
        text.insert(tk.END, content)
        text.pack(expand=True, fill=tk.BOTH)

        ttk.Button(win, text="💾 Save", style="Custom.TButton", command=lambda: self.save_conf(filename, text, win)).pack(pady=5)

    def save_conf(self, filename, widget, window):
        with open(f"/var/log/wifi-emulator/{filename}", "w") as f:
            f.write(widget.get("1.0", tk.END))
        self.log(f"✅ {filename} saved.")
        window.destroy()

    def interfaces_create(self):
        self.run_cmd(["modprobe -r mac80211_hwsim && modprobe mac80211_hwsim radios=3"], "Creating interfaces", shell=True)

    def interfaces_status(self):
        output = subprocess.check_output(["ip", "a"], text=True)
        self.log(output)

    def accesspoint_start(self):
        subprocess.run("killall hostapd", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open("/var/log/wifi-emulator/AccessPoint.log", "w") as f:
            subprocess.Popen(["hostapd", "/var/log/wifi-emulator/ap.conf"], stdout=f, stderr=subprocess.STDOUT, text=True)
        self.log("▶ Access Point started on wlan0.")

    def accesspoint_status(self):
        try:
            with open("/var/log/wifi-emulator/AccessPoint.log", "r") as f:
                self.log(f.read())
        except FileNotFoundError:
            self.log("⚠ No Access Point log found.")

    def client_start(self):
        def run():
            log_file = "/var/log/wifi-emulator/AccessClient.log"
            cmd = "echo '\nWait few seconds to see the connection details below...' && rm -f /var/run/wpa_supplicant/* && wpa_supplicant -i wlan1 -c /var/log/wifi-emulator/client.conf"
            try:
                with open(log_file, "w") as log:
                    process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    self.log("\n▶ Starting Wireless Client on wlan1...\nOutput is being logged to /var/log/wifi-emulator/AccessClient.log")
                    for line in process.stdout:
                        self.log(line.strip())
                        log.write(line)
                        log.flush()
                    process.wait()
                    self.log("Access Client finished.")
            except Exception as e:
                self.log(f"Error running Access Client: {e}")
        threading.Thread(target=run, daemon=True).start()

    def client_status(self):
        try:
            with open("/var/log/wifi-emulator/AccessClient.log", "r") as f:
                output = f.read()
            self.log("AccessClient Output:\n" + output)
        except FileNotFoundError:
            self.log("⚠ No Client log found.")

    # def run_wifite(self):
    #     subprocess.run("mkdir -p /var/log/wifi-emulator/wifite && rm -rf /var/log/wifi-emulator/wifite/*", shell=True)
    #     cmd = 'x-terminal-emulator -e bash -c "cd /var/log/wifi-emulator/wifite; wifite; echo \'\n\nPress any key to close...\'; read"'
    #     self.run_cmd(cmd, "Running wifite", shell=True)
    
    def run_shell(self):
        subprocess.run("mkdir -p /var/log/wifi-emulator/capture && rm -rf /var/log/wifi-emulator/capture/*", shell=True)
        cmd = 'x-terminal-emulator -e bash -c "cd /var/log/wifi-emulator/capture; echo \\"\nPlease check the app\'s help for instructions\\"; exec bash"'
        self.run_cmd(cmd, "Opening root terminal", shell=True)

    def run_cmd(self, cmd, msg="", shell=False):
        try:
            subprocess.Popen(cmd, shell=shell)
            self.log(f"✅ {msg} started.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def reset_app(self):
        cmd = (
            "killall hostapd; killall wpa_supplicant; modprobe -r mac80211_hwsim; "
            "rm -rf /var/log/wifi-emulator/* /var/run/wpa_supplicant/*"
        )
        self.run_cmd(cmd, "Resetting", shell=True)

    def show_help(self):
        help_text = r"""
    Welcome to WiFi Emulator!
    If you have any questions or suggestions, feel free to email me.
    Kaled Aljebur,
    https://github.com/kaledaljebur/wifi-emulator
    kaledaljebur@gmail.com

    Note: use Ctrl+C to copy any command from this window
    
    Run the steps in the following order:
    1. Generate Access Point Conf file
    2. Edit ap.conf if needed
    3. Generate Access Client Conf file
    4. Edit client.conf if needed
    5. Create Virtual Interfaces
    6. Start Access Point on wlan0
    7. Start Access Client on wlan1
    8. (Optional) Run Wifite for capture/cracking

    Other Buttons:
    - Reset: Remove all virtual interfaces and temp files
    - Close: Exit the application
    - Status: Check the status of network interfaces, wlan0, and wlan1
    - Help: Show this window

    Clikc on `Open Root Terminal button`, then follow:
    1.  Enable monitor mode on wlan2
        airmon-ng start wlan2
        - This will change wlan2 into wlan2mon, use `ip a` to check
    2.  Scan the avillable wireless networks
        airodump-ng wlan2mon
    3.  Start capturing the WPA hansshape from the targeted AP
        airodump-ng wlan2mon --bssid ce:7f:82:23:49:53 --channel 6 -w capture
        - Change ce:7f:82:23:49:53 with wlan0 MAC address
        - If handshake captured, you will see `WPA handshake...` in the top right
    4.  If no hsndshake captured, open new terminal tab, then try to de-auth
        aireplay-ng --deauth 3 -a ce:7f:82:23:49:53 wlan2mon
        - Change ce:7f:82:23:49:53 with wlan0 or wlan1 MAC address
    5.  Stop all commands when see WPA handshake captured,
        all capturing files located in /var/log/wifi-emulator/capture
    6.  Try dictionary attack to get the wifi key from the captured handshake
        aircrack-ng capture-01.cap -w /usr/share/dict/wordlist-probable.txt

    Or, clikc on `Open Root Terminal button`, type `wifite` then do:
    - Select wlan2 as monitoring interface
    - Select the Access Point CyberWifi
    - Wifite will try to de-authentiate to ceapture the WPA handshake
    - Little wait and you will see the cracked default key
    - Wifite files are will be located in /var/log/wifi-emulator/capture
    - Each time you run Wifite, /var/log/wifi-emulator/capture will be cleared

    Note:
    - Do not clock on "Generate..." after editing because your edit will be gone
    - Ensure you run this tool with root (sudo)
    - Use the status buttons to see the outputs
    - All logs and Wifite cracking results will be saved in /var/log/wifi-emulator/

    This application was created for educational and research purposes in 
    cybersecurity teaching labs. The traffic generated between wlan0 and wlan1 is 
    realistic and suitable for hands-on research.
        """
        win = tk.Toplevel(self.root)
        win.title("Help")
        win.geometry("700x700")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white")
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        text.pack(expand=True, fill=tk.BOTH)

    def close_app(self):
        self.root.destroy()

def check_sudo():
    if os.geteuid() != 0:
        tk.Tk().withdraw()
        messagebox.showerror("Permission Required", "❌ Please run this app with sudo/root.")
        sys.exit()

def main():
    root = tk.Tk()
    app = WiFi_Emulator(root)
    root.mainloop()
