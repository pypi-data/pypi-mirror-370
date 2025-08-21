from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess, sys, platform, os, shutil

class PostInstallCommand(install):
    def run(self):
        install.run(self)

        if shutil.which("cloudflared"):
            print("cloudflared already exists, skipping installation.")
            return

        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        filename = "cloudflared"

        if platform.system() == "Darwin":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
        elif platform.system() == "Windows":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            filename = "cloudflared.exe"

        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)

        if platform.system() != "Windows":
            os.chmod(filename, 0o755)

setup(
    name="tunnelify",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    author="Yusuf YILDIRIM",
    author_email="yusuf@tachion.tech",
    description="A simple package for easily creating Cloudflare or Localtunnel tunnels.",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/MYusufY/tunnelify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.6",
    cmdclass={"install": PostInstallCommand},
)
