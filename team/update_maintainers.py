#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2025 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import requests
import json

def print_error(message):
    print(f"\033[91m{message}\033[0m")

def fetch_branches(github_token):
    base_headers = {"Authorization": f"token {github_token}"}
    print("Fetching branches...")
    response = requests.get(
        "https://api.github.com/repos/Evolution-X/OTA/branches", headers=base_headers
    )
    if response.status_code != 200:
        print_error("Error: Failed to fetch branch data.")
        sys.exit(1)

    branches = [branch["name"] for branch in response.json()]
    if not branches:
        print_error("No branches found.")
        sys.exit(1)

    print("\nBranches found:")
    for branch in branches:
        print(f"- {branch}")

    return branches

def fetch_maintainers_for_device(device, branch, github_token):
    url = f"https://raw.githubusercontent.com/Evolution-X/OTA/refs/heads/{branch}/builds/{device}.json"
    response = requests.get(url, headers={"Authorization": f"token {github_token}"})

    if response.status_code != 200:
        print_error(f"Failed to fetch JSON for {device} on branch {branch}. "
                    f"Status code: {response.status_code}")
        return []

    try:
        content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print_error(f"Error decoding JSON for {device} on branch {branch}: {e}")
        return []

    if not content or "response" not in content or not content["response"]:
        print_error(f"No maintainer entries for {device} on branch {branch}.")
        return []

    entries = []
    for m in content["response"]:
        github_username = m.get("github")
        maintainer_name = m.get("maintainer")
        oem = m.get("oem")
        device_name = m.get("device")
        maintained = m.get("currently_maintained", False)
        if github_username and maintainer_name and oem and device_name:
            entries.append((maintainer_name, github_username, oem, device_name, maintained))
    return entries

def main():
    if len(sys.argv) != 2:
        print_error("Usage: ./update_maintainers.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    branches = fetch_branches(github_token)
    maintainers = {}

    for branch in branches:
        print(f"\nProcessing branch: {branch}")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        resp = requests.get(url, headers={"Authorization": f"token {github_token}"})
        if resp.status_code != 200:
            print_error(f"Error fetching device list for branch {branch}.")
            continue

        devices = [
            os.path.splitext(item["name"])[0]
            for item in resp.json()
            if item["name"].endswith(".json")
        ]
        if not devices:
            print(f"No devices found on branch {branch}.")
            continue

        for device in devices:
            print(f"  Fetching {device}.json …")
            entries = fetch_maintainers_for_device(device, branch, github_token)
            for name, github_user, oem, dev, is_active in entries:
                if name not in maintainers:
                    maintainers[name] = {
                        "name": name,
                        "github": github_user,
                        "active_devices": set(),
                        "inactive_devices": set()
                    }
                key = f"{oem} {dev}"
                if is_active:
                    maintainers[name]["active_devices"].add(key)
                else:
                    maintainers[name]["inactive_devices"].add(key)

    active_list = []
    inactive_list = []
    for m in maintainers.values():
        if m["active_devices"]:
            active_list.append({
                "name": m["name"],
                "github": m["github"],
                "devices": sorted(m["active_devices"])
            })
        elif m["inactive_devices"]:
            inactive_list.append({
                "name": m["name"],
                "github": m["github"],
                "devices": sorted(m["inactive_devices"])
            })

    active_list.sort(key=lambda x: x["name"])
    inactive_list.sort(key=lambda x: x["name"])

    with open("maintainers.json", "w") as f:
        json.dump({"maintainers": active_list}, f, indent=2)
        f.write("\n") 
    with open("inactive_maintainers.json", "w") as f:
        json.dump({"maintainers": inactive_list}, f, indent=2)
        f.write("\n") 

    print(f"\n✅ Wrote {len(active_list)} active maintainers to maintainers.json")

    print("\nActive Maintainers:")
    for m in active_list:
        print(f"- {m['name']}")

    print(f"\n✅ Wrote {len(inactive_list)} inactive maintainers to inactive_maintainers.json")

    print("\nInactive Maintainers:")
    for m in inactive_list:
        print(f"- {m['name']}")

if __name__ == "__main__":
    main()
