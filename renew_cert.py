import os
import subprocess
import sys
import requests
import time

DNSHE_API_KEY = os.environ.get("DNSHE_API_KEY")
DNSHE_API_ENDPOINT = "https://api005.dnshe.com/index.php?m=domain_hub"

def dnshe_api(action, **params):
    """调用 DNSHE API 的通用方法"""
    data = {
        "key": DNSHE_API_KEY,
        "action": action,
        **params
    }
    response = requests.post(DNSHE_API_ENDPOINT, data=data)
    response.raise_for_status()
    return response.json()

def get_domain_id(domain):
    """获取域名在 DNSHE 中的ID"""
    resp = dnshe_api("domain_list")
    for item in resp.get("data", []):
        if item["domain"] == domain:
            return item["id"]
    raise Exception(f"域名 {domain} 不在你的 DNSHE 列表中")

def add_txt_record(domain, name, value):
    """添加 TXT 记录"""
    domain_id = get_domain_id(domain)
    dnshe_api("record_add", domain_id=domain_id, type="TXT", name=name, value=value)

def delete_txt_record(domain, name, value):
    """删除 TXT 记录"""
    domain_id = get_domain_id(domain)
    resp = dnshe_api("record_list", domain_id=domain_id)
    for record in resp.get("data", []):
        if record["type"] == "TXT" and record["name"] == name and record["value"] == value:
            dnshe_api("record_del", domain_id=domain_id, record_id=record["id"])
            return

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

def main():
    if not DNSHE_API_KEY:
        print("ERROR: 请配置 DNSHE_API_KEY")
        sys.exit(1)

    # 安装 acme.sh
    run_cmd("curl https://get.acme.sh | sh")
    acme = "/home/runner/.acme.sh/acme.sh"

    domains = ["larrcy.us.ci", "wlk.us.ci"]

    for domain in domains:
        print(f"\n===== 处理域名: {domain} =====")
        # 第一步：生成挑战值
        challenge_dir = f"/tmp/acme_challenge_{domain}"
        os.makedirs(challenge_dir, exist_ok=True)
        
        # 第二步：获取挑战记录
        cmd = f"{acme} --issue -d {domain} -d *.{domain} --server letsencrypt --yes-I-know-dns-manual-mode-enough-go-ahead-please --force"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        challenge_found = False
        txt_records = []
        
        for line in iter(proc.stdout.readline, ""):
            print(line, end="")
            if "Add the following TXT record:" in line:
                challenge_found = True
            if challenge_found and "Domain:" in line:
                name = line.split("Domain:")[1].strip()
            if challenge_found and "TXT value:" in line:
                value = line.split("TXT value:")[1].strip()
                txt_records.append((name, value))
                if len(txt_records) == 2:
                    proc.terminate()
                    break
        
        # 第三步：添加 TXT 记录
        for name, value in txt_records:
            add_txt_record(domain, name.replace(f".{domain}", ""), value)
        print("✅ 已添加 TXT 记录，等待生效...")
        time.sleep(30)
        
        # 第四步：完成证书申请
        run_cmd(f"{acme} --renew -d {domain} -d *.{domain} --server letsencrypt --force")
        
        # 第五步：删除 TXT 记录
        for name, value in txt_records:
            delete_txt_record(domain, name.replace(f".{domain}", ""), value)
        print("✅ 已删除临时 TXT 记录")

    print("\n🎉 所有证书申请/续期完成！")

if __name__ == "__main__":
    main()
