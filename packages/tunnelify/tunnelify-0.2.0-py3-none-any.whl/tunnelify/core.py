import subprocess
import re
import threading
import requests
import json
from urllib.parse import urlsplit
import queue
import socket
import os
import sys

def cloudflare_tunnel(port):
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url = None
    def reader():
        nonlocal url
        for line in proc.stdout:
            m = re.search(r"https://[0-9a-zA-Z\-]+\.trycloudflare\.com", 
line)
            if m:
                url = m.group(0)
                break
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    while url is None:
        pass
    return url, proc

def localtunnel(port, subdomain=""):
    LOCAL_TUNNEL_SERVER = "http://localtunnel.me/"
    
    def get_tunnel_url():
        assigned_domain = subdomain if subdomain else "?new"
        url = LOCAL_TUNNEL_SERVER + assigned_domain
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to get assigned URL: 
{response.text}")
        data = json.loads(response.text)
        if "error" in data:
            raise Exception(f"Failed to get assigned URL: 
{data['error']}")
        return data["url"], data["port"], data["max_conn_count"]

    url, remote_port, max_conn_count = get_tunnel_url()
    
    def create_tunnel():
        remote_host = urlsplit(LOCAL_TUNNEL_SERVER).netloc
        while True:
            try:
                remote_conn = socket.create_connection((remote_host, 
remote_port))
                local_conn = socket.create_connection(('localhost', port))
                
                def copy_data(source, dest):
                    try:
                        while True:
                            data = source.recv(4096)
                            if not data:
                                break
                            dest.sendall(data)
                    except:
                        pass
                    finally:
                        source.close()
                        dest.close()

                t1 = threading.Thread(target=copy_data, args=(remote_conn, 
local_conn))
                t2 = threading.Thread(target=copy_data, args=(local_conn, 
remote_conn))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            except:
                pass

    for _ in range(max_conn_count):
        t = threading.Thread(target=create_tunnel, daemon=True)
        t.start()

    return url, None

def tunnel(port, tunnel_type="cloudflare", subdomain=""):
    if tunnel_type.lower() == "cloudflare":
        return cloudflare_tunnel(port)
    elif tunnel_type.lower() == "localtunnel":
        return localtunnel(port, subdomain)
    else:
        raise ValueError("Invalid tunnel type. Please use 'cloudflare' or 'localtunnel'")