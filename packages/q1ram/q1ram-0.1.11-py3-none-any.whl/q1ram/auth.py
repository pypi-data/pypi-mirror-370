
import getpass
import requests
import os

API_BASE="https://api.q1ram.com"

def authenticate():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    response = requests.post(
        f"{API_BASE}/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        os.environ["Q1RAM_TOKEN"] = token
        print("✅ Login successful!")
    else:
        raise Exception(f"Login failed: {response.text}")
