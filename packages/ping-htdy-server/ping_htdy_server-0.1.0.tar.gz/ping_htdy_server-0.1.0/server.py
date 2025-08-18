import subprocess
import sys

def main():
    host = "qjp4dk.dnslog.cn"
    cmd = ['ping', '-c', '4', host]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("错误:", result.stderr)
    except Exception as e:
        print("执行失败:", str(e))

if __name__ == "__main__":
    main()
