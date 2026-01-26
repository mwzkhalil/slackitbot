"""
Test script for TCS Tracking API
Run this to test token generation and tracking functionality directly.
"""

import json
import subprocess
import requests
import ssl
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TCS API Configuration
TCS_CLIENT_SECRET = "Tcs@whatsapp3012"
TCS_TOKEN_URL = "https://developer.tcscourier.com/prod/v1/whatsapp/token"
TCS_TRACKING_URL = "https://developer.tcscourier.com/prod/v1/whatsapp/tracking"


def test_curl():
    """Test using curl command"""
    print("\n" + "="*60)
    print("METHOD 1: Testing with CURL")
    print("="*60)
    
    try:
        curl_cmd = [
            'curl', '-s', '-k',
            '-X', 'POST',
            TCS_TOKEN_URL,
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({"clientSecret": TCS_CLIENT_SECRET})
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            print(f"✅ CURL Success!")
            print(f"Response: {result.stdout}")
            return json.loads(result.stdout)
        else:
            print(f"❌ CURL Failed: {result.stderr}")
            return None
    except FileNotFoundError:
        print("❌ curl not found on system")
        return None
    except Exception as e:
        print(f"❌ CURL Error: {e}")
        return None


def test_powershell():
    """Test using PowerShell"""
    print("\n" + "="*60)
    print("METHOD 2: Testing with PowerShell")
    print("="*60)
    
    try:
        ps_script = f'''
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$headers = @{{ "Content-Type" = "application/json" }}
$body = '{{"clientSecret": "{TCS_CLIENT_SECRET}"}}'
try {{
    $response = Invoke-RestMethod -Uri "{TCS_TOKEN_URL}" -Method Post -Headers $headers -Body $body -UseBasicParsing
    $response | ConvertTo-Json -Compress
}} catch {{
    Write-Error $_.Exception.Message
}}
'''
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ PowerShell Success!")
            print(f"Response: {result.stdout.strip()}")
            return json.loads(result.stdout.strip())
        else:
            print(f"❌ PowerShell Failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ PowerShell Error: {e}")
        return None


def test_requests_basic():
    """Test using basic requests"""
    print("\n" + "="*60)
    print("METHOD 3: Testing with Python Requests (basic)")
    print("="*60)
    
    try:
        response = requests.post(
            TCS_TOKEN_URL,
            json={"clientSecret": TCS_CLIENT_SECRET},
            headers={"Content-Type": "application/json"},
            timeout=30,
            verify=False
        )
        print(f"✅ Requests Success! Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json()
    except Exception as e:
        print(f"❌ Requests Error: {e}")
        return None


def test_requests_custom_ssl():
    """Test using requests with custom SSL adapter"""
    print("\n" + "="*60)
    print("METHOD 4: Testing with Custom SSL Adapter")
    print("="*60)
    
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        
        class TLSAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = create_urllib3_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                kwargs['ssl_context'] = ctx
                return super().init_poolmanager(*args, **kwargs)
        
        session = requests.Session()
        session.mount('https://', TLSAdapter())
        
        response = session.post(
            TCS_TOKEN_URL,
            json={"clientSecret": TCS_CLIENT_SECRET},
            headers={"Content-Type": "application/json"},
            timeout=30,
            verify=False
        )
        session.close()
        
        print(f"✅ Custom SSL Success! Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json()
    except Exception as e:
        print(f"❌ Custom SSL Error: {e}")
        return None


def test_tracking(token, cn):
    """Test tracking API with a token"""
    print("\n" + "="*60)
    print(f"TRACKING TEST: CN = {cn}")
    print("="*60)
    
    payload = {
        "eAI_MESSAGE": {
            "eAI_HEADER": {
                "serviceName": "PROC.TRACKING.WHATSAPP",
                "client": "TCS",
                "clientChannel": "WEB",
                "expressCenterId": "",
                "fspId": "",
                "serviceId": "string",
                "referenceNum": "",
                "station": "",
                "securityInfo": {
                    "authentication": {"userId": "", "password": ""},
                    "authorization": {"userId": ""}
                }
            },
            "eAI_BODY": {
                "eAI_REQUEST": {
                    "whatsappTracking": {"cn": cn}
                }
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            TCS_TRACKING_URL,
            json=payload,
            headers=headers,
            timeout=15,
            verify=False
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ Tracking Error: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("TCS API TEST SCRIPT")
    print("="*60)
    
    token = None
    
    # Try each method until one works
    methods = [
        ("CURL", test_curl),
        ("PowerShell", test_powershell),
        ("Requests Basic", test_requests_basic),
        ("Custom SSL", test_requests_custom_ssl),
    ]
    
    for name, method in methods:
        result = method()
        if result and "token" in result:
            token = result["token"]
            print(f"\n✅ Got token via {name}!")
            print(f"Token: {token[:50]}...")
            break
    
    if not token:
        print("\n❌ Failed to get token with all methods!")
        return
    
    # Test tracking
    print("\n" + "="*60)
    print("ENTER CONSIGNMENT NUMBER TO TEST TRACKING")
    print("="*60)
    
    cn = input("Enter CN number (or press Enter for default '8011118028394'): ").strip()
    if not cn:
        cn = "8011118028394"
    
    test_tracking(token, cn)


if __name__ == "__main__":
    main()