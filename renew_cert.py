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
        print(f"Command failed with code {returncode}")
        sys.exit(result.returncode)
    return result.stdout

if __name__ == "__main__":
    api_key = os.environ.get("DNSHE_API_KEY")
    api_secret = os.environ.get("DNSHE_API_SECRET")
    if not api_key or not api_secret:
        print("API密钥缺失")
        sys.exit(1)

    os.environ["DNSHE_API_KEY"] = api_key
    os.environ["DNSHE_API_SECRET"] = api_secret

    run_cmd("curl https://get.acme.sh | sh")
    acme_path = os.path.expanduser("~/.acme.sh/acme.sh")

    # 只保留 主域名 + 泛域名，去掉重复的 www
    domains = [
        "larrcy.us.ci",
        "wlk.us.ci"
    ]

    for domain in domains:
        print(f"=== 处理域名: {domain} ===")
        cmd = f"""{acme_path} --issue \
            --dns dns_dnshe \
            -d {domain} \
            -d *.{domain} \
            --server letsencrypt \
            --force"""
        run_cmd(cmd)

    print("✅ 证书续期全部成功！")
