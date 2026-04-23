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
    api_key = os.environ.get("DNSHE_API_KEY")
    api_secret = os.environ.get("DNSHE_API_SECRET")

    if not api_key or not api_secret:
        print("ERROR: 请配置 DNSHE_API_KEY 和 DNSHE_API_SECRET")
        sys.exit(1)

    os.environ["DNSHE_API_KEY"] = api_key
    os.environ["DNSHE_API_SECRET"] = api_secret

    # 安装 acme.sh
    run_cmd("curl https://get.acme.sh | sh")
    acme = "/home/runner/.acme.sh/acme.sh"

    # 关闭自动升级，避免网络问题
    run_cmd(f"{acme} --upgrade --auto-upgrade 0")

    # 处理域名
    domains = ["larrcy.us.ci", "wlk.us.ci"]

    for domain in domains:
        print(f"\n===== 开始处理域名: {domain} =====")
        run_cmd(f"""
        {acme} --issue \
        --dns dns_he \
        -d {domain} \
        -d *.{domain} \
        --server letsencrypt \
        --force
        """)

    print("\n✅ 所有证书申请/续期操作完成！")
