import os
import subprocess

def main():
    deb_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "wifi-emulator_0.1.3_all.deb"
    ))

    try:
        # print("The .deb path is: ",deb_file)
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", deb_file], check=True)
        print("wifi-emulator .deb package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install .deb package: {e}")
