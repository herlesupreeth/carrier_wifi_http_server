# carrier_wifi_http_server
Implements a server that hosts the certificate of the carrier which is used to encrypt the IMSI sent to WLAN or EPDG


## About

Carrier Wi-Fi is an auto-connection feature (using encrypted IMSI) available in Android 9 and higher that allows devices to automatically connect to carrier-implemented Wi-Fi networks. More details in the following [link](https://source.android.com/devices/tech/connect/carrier-wifi)

The python script (cert_server.py) in this repo is a mere tool to distribute public key certificate to phones so that they can connect to Carrier WiFi wihout any user interaction


## Requirements to run the HTTP server
- python3


## Requirements to test the fetching of certificate by UE
- Android phone with UICC Carrier priviliges provided by the UICC. Refer this [link](https://github.com/herlesupreeth/CoIMS_Wiki)
- Carrier Config Android app with following configuration parameters set
	- "imsi_key_availability_int" set to 3 (assuming we need the key for both WLAN and EPDG)
	- "carrier_wifi_string_array" set to Base64-encoded Wi-Fi SSID and an EAP type separated by a comma, where the EAP type is an [integer](https://www.iana.org/assignments/eap-numbers/eap-numbers.xhtml)
	- "imsi_key_download_url_string" set to "http://<IP_ADDRESS>:<PORT>/cert/"
	- "allow_metered_network_for_cert_download_bool" set to 1
- Cellular network/non-carrier WiFi network to which phone can connect and download the certificate from the HTTP server. The HTTP server should be reachable from whichever network the phone connects to


## Requirements to test the auto-connection feature by UE
- The carrier must support encrypted IMSI
- Carrier WiFi (In simplest form, an AP created using hostapd with the correct configuration and freeradius settings/user info)
- Private key configured at AAA to decrypt the IMSI sent by UE


## Steps to personalize the HTTP server with desired public key certificate


#### Step 1: Generate private key and certificate containing the public key

```
$ ipsec pki --gen --type rsa --size 2048 --outform pem > ca-key.pem
$ ipsec pki --self --ca --lifetime 3650 --in ca-key.pem \
	--type rsa --dn "CN=WLAN_EPDG_CA" --outform pem > ca-cert.pem
```


#### Step 2: Print contents of certificate containing public key to console

The ca-cert.pem generated in the previous step is the carrier certificate containing the public key used to encrypt the IMSI by UE

```
$ cat ca-cert.pem
```

Example:

```
$ cat ca-cert.pem
-----BEGIN CERTIFICATE-----
MIIE9zCCA9+gAwIBAgIUWdxGbh1KrRssJAxRs8yWjUW8P3gwDQYJKoZIhvcNAQEL
BQAwgZIxCzAJBgNVBAYTAkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNv
bWV3aGVyZTEUMBIGA1UECgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFk
bWluQGV4YW1wbGUub3JnMSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1
dGhvcml0eTAeFw0yMDAzMDkwOTAyMjFaFw0yMDA1MDgwOTAyMjFaMIGSMQswCQYD
VQQGEwJGUjEPMA0GA1UECAwGUmFkaXVzMRIwEAYDVQQHDAlTb21ld2hlcmUxFDAS
BgNVBAoMC0V4YW1wbGUgSW5jMSAwHgYJKoZIhvcNAQkBFhFhZG1pbkBleGFtcGxl
Lm9yZzEmMCQGA1UEAwwdRXhhbXBsZSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwggEi
MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCqOSz0QEFUmuPuz1qMfE190MHu
9fkG8vJl01gvoyBETUDUgdIVXhQENIyAzgGNtdS2c8i5B68wcKKSdJAtuc8vDg6V
rgvQoC4RrMxu9DCyxDq6+prYO+BASaV24pN4Nb8HfOsxpXd1A+N7rFtl1/wl+lkq
0QbGF0pW8tWc3Q5BThm/cJHlqORPP3Ev1AoO1ZAA9rjDxv58Tzm9pcXOzGc28y8n
QuRE6vfDhMyhSKdzCTjpT/hLno4E085T6AEuUzdHAtLjfrLFBUW2pRBsShIzwB4X
vvP1eRKuP+4yb1XeCrBwnRyEZzriJ0QqZAEqRHyl7GBc5tWmzVIlKFyBN8SnAgMB
AAGjggFBMIIBPTAdBgNVHQ4EFgQUp1WZPzzIdJd6I/1j45nnjE2S8ogwgdIGA1Ud
IwSByjCBx4AUp1WZPzzIdJd6I/1j45nnjE2S8oihgZikgZUwgZIxCzAJBgNVBAYT
AkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNvbWV3aGVyZTEUMBIGA1UE
CgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFkbWluQGV4YW1wbGUub3Jn
MSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1dGhvcml0eYIUWdxGbh1K
rRssJAxRs8yWjUW8P3gwDwYDVR0TAQH/BAUwAwEB/zA2BgNVHR8ELzAtMCugKaAn
hiVodHRwOi8vd3d3LmV4YW1wbGUuY29tL2V4YW1wbGVfY2EuY3JsMA0GCSqGSIb3
DQEBCwUAA4IBAQAX3EDBPTg7GwyLBZqFmnmIVOWZpEAfPqND8ZfyvO5Ng9eByxuc
7NYDBSDX1OFZjaWIQwOblwropZSRLeTu3xyaAZErDeCY+jAlSDQIvXA3QDroDpJf
uZ+1QtaTJsV7nDbikZUkq3oBv5YN5KYQPIUt7IOlprlsSpxoULXAC1BzAGGl2XCp
WpOjVa4oMKq78fiSNYs/VY2oQ9tHa1zOmDUA6gG8ZVYrL00C1kwmtsJOlrEu5YaF
N5Eg/hgop1xrwGH/BZWLwixT1/AGKQuxLKGo9zgI2fpStQL6nJg8Y6orGkEwkHUc
V/wXY2FAmuHV626RHkW7oTd6Ix4M7oUNHv0y
-----END CERTIFICATE-----
```


#### Step 3: Convert the contents of certificate printed in Step 2 to a single line string and update the python script

Converting the contents of certificate to a single line string involves replacing newlines with \r\n and update the radius_cert variable in python script

Example: Assuming the contents of ca-cert.pem in example given in Step 2, the radius_cert variable in the script will be as follows

```
radius_cert = "-----BEGIN CERTIFICATE-----\r\nMIIE9zCCA9+gAwIBAgIUWdxGbh1KrRssJAxRs8yWjUW8P3gwDQYJKoZIhvcNAQEL\r\nBQAwgZIxCzAJBgNVBAYTAkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNv\r\nbWV3aGVyZTEUMBIGA1UECgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFk\r\nbWluQGV4YW1wbGUub3JnMSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1\r\ndGhvcml0eTAeFw0yMDAzMDkwOTAyMjFaFw0yMDA1MDgwOTAyMjFaMIGSMQswCQYD\r\nVQQGEwJGUjEPMA0GA1UECAwGUmFkaXVzMRIwEAYDVQQHDAlTb21ld2hlcmUxFDAS\r\nBgNVBAoMC0V4YW1wbGUgSW5jMSAwHgYJKoZIhvcNAQkBFhFhZG1pbkBleGFtcGxl\r\nLm9yZzEmMCQGA1UEAwwdRXhhbXBsZSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwggEi\r\nMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCqOSz0QEFUmuPuz1qMfE190MHu\r\n9fkG8vJl01gvoyBETUDUgdIVXhQENIyAzgGNtdS2c8i5B68wcKKSdJAtuc8vDg6V\r\nrgvQoC4RrMxu9DCyxDq6+prYO+BASaV24pN4Nb8HfOsxpXd1A+N7rFtl1/wl+lkq\r\n0QbGF0pW8tWc3Q5BThm/cJHlqORPP3Ev1AoO1ZAA9rjDxv58Tzm9pcXOzGc28y8n\r\nQuRE6vfDhMyhSKdzCTjpT/hLno4E085T6AEuUzdHAtLjfrLFBUW2pRBsShIzwB4X\r\nvvP1eRKuP+4yb1XeCrBwnRyEZzriJ0QqZAEqRHyl7GBc5tWmzVIlKFyBN8SnAgMB\r\nAAGjggFBMIIBPTAdBgNVHQ4EFgQUp1WZPzzIdJd6I/1j45nnjE2S8ogwgdIGA1Ud\r\nIwSByjCBx4AUp1WZPzzIdJd6I/1j45nnjE2S8oihgZikgZUwgZIxCzAJBgNVBAYT\r\nAkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNvbWV3aGVyZTEUMBIGA1UE\r\nCgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFkbWluQGV4YW1wbGUub3Jn\r\nMSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1dGhvcml0eYIUWdxGbh1K\r\nrRssJAxRs8yWjUW8P3gwDwYDVR0TAQH/BAUwAwEB/zA2BgNVHR8ELzAtMCugKaAn\r\nhiVodHRwOi8vd3d3LmV4YW1wbGUuY29tL2V4YW1wbGVfY2EuY3JsMA0GCSqGSIb3\r\nDQEBCwUAA4IBAQAX3EDBPTg7GwyLBZqFmnmIVOWZpEAfPqND8ZfyvO5Ng9eByxuc\r\n7NYDBSDX1OFZjaWIQwOblwropZSRLeTu3xyaAZErDeCY+jAlSDQIvXA3QDroDpJf\r\nuZ+1QtaTJsV7nDbikZUkq3oBv5YN5KYQPIUt7IOlprlsSpxoULXAC1BzAGGl2XCp\r\nWpOjVa4oMKq78fiSNYs/VY2oQ9tHa1zOmDUA6gG8ZVYrL00C1kwmtsJOlrEu5YaF\r\nN5Eg/hgop1xrwGH/BZWLwixT1/AGKQuxLKGo9zgI2fpStQL6nJg8Y6orGkEwkHUc\r\nV/wXY2FAmuHV626RHkW7oTd6Ix4M7oUNHv0y\r\n-----END CERTIFICATE-----"

```


#### Step 4: Run the script

```
$ python3 cert_server.py <PORT> <IP_ADRRESS>
```

where, <IP_ADRRESS>, <PORT> are IP address and Port configured in Carrier Config Android App at key value "imsi_key_download_url_string"


## Working
- UE successfully retrieves the certificate from the HTTP server - Verified using Logcat


## Not tested
- Auto-connecting feature by UE with Carrier WiFi


## Not working
- UE once it retrieves the certificate does not try to retrieve the certificate again - Weird, not sure why
- UE does not encrypt the IMSI but sends it out in the plan while attaching using EAP-AKA, EAP-AKA-PRIME and EAP-SIM mechanisms
