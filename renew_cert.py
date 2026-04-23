import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"Command failed with code {result.returncode}")
        sys.exit(result.returncode)
    return result.stdout

if __name__ == "__main__":
    # 从 GitHub Secrets 读取 API 密钥
    api_key = os.environ.get("DNSHE_API_KEY")
    api_secret = os.environ.get("DNSHE_API_SECRET")
    if not api_key or not api_secret:
        print("DNSHE API Key/Secret not found in environment variables")
        sys.exit(1)

    # 设置环境变量给 acme.sh 使用
    os.environ["DNSHE_API_KEY"] = api_key
    os.environ["DNSHE_API_SECRET"] = api_secret

    # 安装 acme.sh
    run_cmd("curl https://get.acme.sh | sh")
    acme_path = os.path.expanduser("~/.acme.sh/acme.sh")

    # 给两个域名申请/续期证书
    domains = [
        "larrcy.us.ci",
        "wlk.us.ci"
    ]

    for domain in domains:
        print(f"=== Processing domain: {domain} ===")
        cmd = f"""{acme_path} --issue \
            --dns dns_dnshe \
            -d {domain} \
            -d www.{domain} \
            -d *.{domain} \
            --server letsencrypt \
            --force"""
        run_cmd(cmd)

    print("✅ All certificates renewed successfully!")
