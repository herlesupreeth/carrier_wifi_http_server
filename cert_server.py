#!/usr/bin/env python

# BSD 2-Clause License

# Copyright (c) 2020, Supreeth Herle
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
To generate a certificate use:

$ ipsec pki --gen --type rsa --size 2048 --outform pem > ca-key.pem

$ ipsec pki --self --ca --lifetime 3650 --in ca-key.pem \
	--type rsa --dn "CN=WLAN_EPDG_CA" --outform pem > ca-cert.pem

Public key 

$ cat ca-cert.pem

Then, construct radius_cert variable using the above output of ca-cert.pem i.e. replace new lines with \r\n

Usage

$ python3 cert_server.py <PORT> <IP_ADRRESS>
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import argparse
import re
import cgi
import json
import threading
from urllib import parse
import json
import gzip
import base64

radius_cert = "-----BEGIN CERTIFICATE-----\r\nMIIE9zCCA9+gAwIBAgIUWdxGbh1KrRssJAxRs8yWjUW8P3gwDQYJKoZIhvcNAQEL\r\nBQAwgZIxCzAJBgNVBAYTAkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNv\r\nbWV3aGVyZTEUMBIGA1UECgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFk\r\nbWluQGV4YW1wbGUub3JnMSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1\r\ndGhvcml0eTAeFw0yMDAzMDkwOTAyMjFaFw0yMDA1MDgwOTAyMjFaMIGSMQswCQYD\r\nVQQGEwJGUjEPMA0GA1UECAwGUmFkaXVzMRIwEAYDVQQHDAlTb21ld2hlcmUxFDAS\r\nBgNVBAoMC0V4YW1wbGUgSW5jMSAwHgYJKoZIhvcNAQkBFhFhZG1pbkBleGFtcGxl\r\nLm9yZzEmMCQGA1UEAwwdRXhhbXBsZSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwggEi\r\nMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCqOSz0QEFUmuPuz1qMfE190MHu\r\n9fkG8vJl01gvoyBETUDUgdIVXhQENIyAzgGNtdS2c8i5B68wcKKSdJAtuc8vDg6V\r\nrgvQoC4RrMxu9DCyxDq6+prYO+BASaV24pN4Nb8HfOsxpXd1A+N7rFtl1/wl+lkq\r\n0QbGF0pW8tWc3Q5BThm/cJHlqORPP3Ev1AoO1ZAA9rjDxv58Tzm9pcXOzGc28y8n\r\nQuRE6vfDhMyhSKdzCTjpT/hLno4E085T6AEuUzdHAtLjfrLFBUW2pRBsShIzwB4X\r\nvvP1eRKuP+4yb1XeCrBwnRyEZzriJ0QqZAEqRHyl7GBc5tWmzVIlKFyBN8SnAgMB\r\nAAGjggFBMIIBPTAdBgNVHQ4EFgQUp1WZPzzIdJd6I/1j45nnjE2S8ogwgdIGA1Ud\r\nIwSByjCBx4AUp1WZPzzIdJd6I/1j45nnjE2S8oihgZikgZUwgZIxCzAJBgNVBAYT\r\nAkZSMQ8wDQYDVQQIDAZSYWRpdXMxEjAQBgNVBAcMCVNvbWV3aGVyZTEUMBIGA1UE\r\nCgwLRXhhbXBsZSBJbmMxIDAeBgkqhkiG9w0BCQEWEWFkbWluQGV4YW1wbGUub3Jn\r\nMSYwJAYDVQQDDB1FeGFtcGxlIENlcnRpZmljYXRlIEF1dGhvcml0eYIUWdxGbh1K\r\nrRssJAxRs8yWjUW8P3gwDwYDVR0TAQH/BAUwAwEB/zA2BgNVHR8ELzAtMCugKaAn\r\nhiVodHRwOi8vd3d3LmV4YW1wbGUuY29tL2V4YW1wbGVfY2EuY3JsMA0GCSqGSIb3\r\nDQEBCwUAA4IBAQAX3EDBPTg7GwyLBZqFmnmIVOWZpEAfPqND8ZfyvO5Ng9eByxuc\r\n7NYDBSDX1OFZjaWIQwOblwropZSRLeTu3xyaAZErDeCY+jAlSDQIvXA3QDroDpJf\r\nuZ+1QtaTJsV7nDbikZUkq3oBv5YN5KYQPIUt7IOlprlsSpxoULXAC1BzAGGl2XCp\r\nWpOjVa4oMKq78fiSNYs/VY2oQ9tHa1zOmDUA6gG8ZVYrL00C1kwmtsJOlrEu5YaF\r\nN5Eg/hgop1xrwGH/BZWLwixT1/AGKQuxLKGo9zgI2fpStQL6nJg8Y6orGkEwkHUc\r\nV/wXY2FAmuHV626RHkW7oTd6Ix4M7oUNHv0y\r\n-----END CERTIFICATE-----"

key_id = "CertificateSerialNumber=473"

# data = "-----BEGIN CERTIFICATE-----\r\nMIIC8DCCAdigAwIBAgIIfshW+jZ0WLIwDQYJKoZIhvcNAQELBQAwFjEUMBIGA1UE\r\nAxMLVlBOIHJvb3QgQ0EwHhcNMjAwMzExMDc0OTA5WhcNMzAwMzA5MDc0OTA5WjAW\r\nMRQwEgYDVQQDEwtWUE4gcm9vdCBDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC\r\nAQoCggEBAMCO7eU3Jbhk7ngxsFrM+5apMG235V6BI+JwRpHqWSLPt+0djBJWNvFL\r\nHoI0KjIU6v049hfMINARhKHtKLOmWhJy7anwrhgxKObyxRs2EO/v9dcq9Jryc1NC\r\nrl+RLwa+JgLE4rOuVabLGrV3FNqvUZyZZAZnCSS8qs+92VmBMZ4qLNnlzonEoVls\r\nwCH5eWA9i+AkPNb/aX0BgKFKq+/j8sYShZUxS4FQ9GYwfLCnUFtnYpg5vqrlGwOv\r\n+hDSa7qgNq/C5hC0FuAyXgX6DQhrTUwCViX2QT7TJrrzpoc5KJlC1ItsRqmmHyCz\r\nxMXuZXDasgpOa/1EXGtafEbuSKE+vbsCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB\r\n/zAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFCsIP2v4GMWxv6fxbhyMMLBGOH9g\r\nMA0GCSqGSIb3DQEBCwUAA4IBAQB9gevq5DRyonm38BGNl69S6z8CQticLG4zrDpo\r\nuhfmVsEmRQTLy3iMsm3OBfNYdP8NdH7lu2FohSaAdbp/fCQdV3vM+QWHITkj/H1a\r\n2Lvh2KrvfowouYTMHjMI0H8xkyMVlrdhhNMxaMzbN4OjQ30hRbuZBYh12nvqjHsP\r\nG7fMA4IwkGRYYJ8WM6UJTUymAnnn/VSdrnRaiw49rUIohbnieRVTxvI3jHPuhDWW\r\nXqDKFWZ/RClMKYXWkkWfEX7e6JIq97BwesgIGjTn7ibb1Xzl9EvyxU63Ot1NpTCC\r\nK3FOP53o9UIlgS8aZ5cYILTwHmAoCT1i7scW5y0P9GxBJVMl\r\n-----END CERTIFICATE-----"
# cert_encoded = base64.b64encode(data.encode("utf-8"))

cert = {
	"carrier-keys": [
		{
			"key-identifier" : key_id,
			"key-type" : "WLAN",
			# "public-key" : data,
			"certificate" : radius_cert
		},
		{
			"key-identifier" : key_id,
			"key-type" : "EPDG",
			# "public-key" : data,
			"certificate" : radius_cert
		}
	]
}

carrier_keys = [
	{
		"key-identifier" : key_id,
		"key-type" : "WLAN",
		# "public-key" : data,
		"certificate" : radius_cert
	},
	{
		"key-identifier" : key_id,
		"key-type" : "EPDG",
		# "public-key" : data,
		"certificate" : radius_cert
	}
]


class HTTPRequestHandler(SimpleHTTPRequestHandler):
	def do_POST(self):
		if re.search('/cert', self.path):
			ctype, pdict = cgi.parse_header(
				self.headers.get('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.get('content-length'))
				rfile_str = self.rfile.read(length).decode('utf8')
				req = parse.parse_qs(rfile_str, keep_blank_values=1)
				# Here match the key-identifier and send certificate for that
				print("request json %s" % (req))
				# HTTP 200: ok
				self.send_response(200)
				payload = json.dumps(cert)
				s_out = gzip.compress(payload.encode('utf8'))
				self.send_header('Content-Type', 'application/json')
				self.send_header('Content-Encoding', 'gzip')
				self.send_header('Content-Length', len(s_out))
				self.end_headers()
				self.wfile.write(s_out)
		else:
			# HTTP 403: forbidden
			self.send_response(403)
			self.end_headers()

	def do_GET(self):
		if re.search('/cert', self.path):
			self.send_response(200)
			payload = json.dumps(cert)
			s_out = gzip.compress(payload.encode('utf8'))
			self.send_header('Content-Type', 'application/json')
			self.send_header('Content-Encoding', 'gzip')
			self.send_header('Content-Length', len(s_out))
			self.end_headers()
			self.wfile.write(s_out)
		else:
			self.send_response(403)
			self.end_headers()


def main():
	parser = argparse.ArgumentParser(description='HTTP Server')
	parser.add_argument('port', type=int, help='Listening port for HTTP Server')
	parser.add_argument('ip', help='HTTP Server IP')
	args = parser.parse_args()

	server = HTTPServer((args.ip, args.port), HTTPRequestHandler)
	#server.socket = ssl.wrap_socket(server.socket, certfile="../server.pem", server_side=True)
	print('HTTP Server Running...........')
	server.serve_forever()

if __name__ == '__main__':
	main()
