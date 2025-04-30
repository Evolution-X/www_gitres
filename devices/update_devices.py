#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import requests
import json

def print_error(message):
    print(f"\033[91m{message}\033[0m")

def main():
    if len(sys.argv) != 2:
        print_error("Usage: python update_devices.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    base_headers = {"Authorization": f"token {github_token}"}

    # Fetch & print OTA branches
    print("Fetching OTA branches...")
    response = requests.get(
        "https://api.github.com/repos/Evolution-X/OTA/branches", headers=base_headers
    )
    if response.status_code != 200:
        print_error("Error: Failed to fetch OTA branch data.")
        sys.exit(1)

    branches = [branch["name"] for branch in response.json()]
    if not branches:
        print_error("No OTA branches found.")
        sys.exit(1)

    print("\nOTA branches found:")
    for branch in branches:
        print(f"- {branch}")

    devices_json = {}

    # Fetch devices for each branch on OTA
    for branch in branches:
        print(f"Fetching devices on {branch}...")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        devices_response = requests.get(url, headers=base_headers)

        if devices_response.status_code != 200:
            print_error(f"Error: Failed to fetch devices on {branch}.")
            continue

        devices = [
            os.path.splitext(item["name"])[0]
            for item in devices_response.json()
            if item["name"].endswith(".json")
        ]

        if not devices:
            print(f"No devices found on {branch}.")
        else:
            for device in devices:
                if device not in devices_json:
                    devices_json[device] = []
                devices_json[device].append(branch)

    devices_json_array = [{"device": device, "branches": branches} for device, branches in devices_json.items()]
    devices_json_array = sorted(devices_json_array, key=lambda x: x["device"])

    with open("devices.json", "w") as file:
        json.dump(devices_json_array, file, indent=2)

    # Check if device images exist
    print("Checking if device images exist...")
    os.makedirs("images", exist_ok=True)

    for device in devices_json:
        device_name = device
        output_path = f"images/{device_name}.webp"

        if not os.path.exists(output_path):
            image_url = f"https://raw.githubusercontent.com/LineageOS/lineage_wiki/refs/heads/main/images/devices/{device_name}.png"
            image_response = requests.head(image_url)

            if image_response.status_code == 200:
                print(f"\033[93m[WARNING]\033[0m {device_name}.webp does not exist locally.")
                print(f"Please download the image manually from:\n{image_url}")
                print(f"Then convert it to webp at 90% quality with a compression level of 6.")
            else:
                print(f"\033[93m[WARNING]\033[0m {device_name}.png is not available on the LineageOS GitHub.")
                print("Please retrieve the image from another source (e.g., manufacturer site, or XDA forums).")
                print(f"Then convert it to webp at 90% quality with a compression level of 6.")

    # Generate installation instructions
    os.makedirs("instructions", exist_ok=True)
    for device in devices_json_array:
        device_name = device["device"]
        for branch in device["branches"]:
            print(f"Generating instructions for {device_name} on {branch}...")
            branch_dir = f"instructions/{branch}"
            os.makedirs(branch_dir, exist_ok=True)
            md_file = f"{branch_dir}/{device_name}.md"

            json_url = f"https://raw.githubusercontent.com/Evolution-X/OTA/refs/heads/{branch}/builds/{device_name}.json"
            response = requests.get(json_url)

            if response.status_code != 200:
                print_error(f"Failed to fetch JSON for {device_name} on branch {branch}. Status code: {response.status_code}")
                print_error(f"Response content: {response.text}")
                continue

            try:
                json_content = response.json()
            except requests.exceptions.JSONDecodeError as e:
                print_error(f"Error decoding JSON for {device_name} on {branch}: {e}")
                print_error(f"Response content: {response.text}")
                continue

            if not json_content or "response" not in json_content or not json_content["response"]:
                print_error(f"JSON for {device_name} not found on branch {branch}.")
                continue

            initial_images = json_content["response"][0].get("initial_installation_images", [])
            oem = json_content["response"][0].get("oem", "")
            if oem == "Samsung":
                flash_command_prefix = "heimdall flash"
            else:
                flash_command_prefix = "fastboot flash"

            flash_commands = "\n\n".join(
                f"```{flash_command_prefix} --{img.upper()} {img}.img```" if oem == "Samsung" else
                (f"```{flash_command_prefix} {img} {img}.img```" if img != "super_empty" else "```fastboot wipe-super super_empty.img```")
                for img in initial_images
            )

            images_to_download = ", ".join(initial_images + ["rom"])
            download_url = json_content["response"][0]["download"]
            version = download_url.split("/")[-3]
            download_url = f"https://sourceforge.net/projects/evolution-x/files/{device_name}/{version}/"

            with open(md_file, "w") as md:
                md.write(
                    f"""## THESE INSTRUCTIONS ASSUME YOUR DEVICE'S BOOTLOADER IS ALREADY UNLOCKED

1. Download {images_to_download} for {device_name} from [here]({download_url}).
2. Reboot to bootloader.
3.
{flash_commands}

4. Reboot to recovery.
5. While in recovery, navigate to **Factory Reset** → **Format Data/Factory Reset** and confirm to format the device.
6. When done formatting, go back to the main menu and then navigate to **Apply Update** → **Apply from ADB**.
7. `adb sideload rom.zip` (replace "rom.zip" with the actual build filename).
8. (Optional) Reboot to recovery (fully) to sideload any add-ons.
9. Reboot to system and **#KeepEvolving**.
"""
                )

    print("Done.")

if __name__ == "__main__":
    main()
