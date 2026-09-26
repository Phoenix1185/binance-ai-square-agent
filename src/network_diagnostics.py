import requests

def print_network_diagnostics():
    print("\n=== NETWORK DIAGNOSTICS ===")

    # Public outbound IP used by the runtime.
    try:
        ip = requests.get("https://api.ipify.org?format=json", timeout=10).json()
        print(f"Outbound public IP: {ip.get('ip')}")
    except Exception as exc:
        print(f"Outbound public IP: unavailable ({exc})")

    # Test Binance public REST API independently of Square publishing.
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ping",
            timeout=15,
        )
        print(f"api.binance.com: HTTP {response.status_code}")
    except Exception as exc:
        print(f"api.binance.com: request failed ({exc})")

    # We deliberately do not send the Square API key during this probe.
    # This only verifies that the Binance host is reachable from the runner.
    try:
        response = requests.get(
            "https://www.binance.com/en",
            timeout=15,
        )
        print(f"www.binance.com: HTTP {response.status_code}")
    except Exception as exc:
        print(f"www.binance.com: request failed ({exc})")

    print("=== END NETWORK DIAGNOSTICS ===\n")
