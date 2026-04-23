import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("输出:", result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    if result.returncode != 0:
        print(f"命令失败，代码: {result.returncode}")
        sys.exit(result.returncode)
    return result.stdout

if __name__ == "__main__":
    run_cmd("curl https://get.acme.sh | sh")
    acme = "/home/runner/.acme.sh/acme.sh"

    # 注册邮箱（必须！ZeroSSL要求）
    run_cmd(f"{acme} --register-account -m test@example.com")

    # 申请证书
    domains = ["larrcy.us.ci", "wlk.us.ci"]

    for domain in domains:
        print(f"\n==================================")
        print(f"      申请证书: {domain}")
        print(f"==================================")
        
        run_cmd(f"""
        {acme} --issue \
        -d {domain} \
        -d *.{domain} \
        --standalone \
        --force
        """)

    print("\n🎉🎉🎉 全部成功！自动续期已开启！")
