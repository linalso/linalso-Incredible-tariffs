import psutil
import time
import os

def blue_screen():
    """
    模拟蓝屏效果
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("系统错误: 资源占用过高")
    print("请立即释放资源以避免系统崩溃")
    print("按下任意键继续...")
    input()

def monitor_resources():
    """
    监控系统资源占用
    """
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        print(f"CPU使用率: {cpu_usage}%")
        print(f"内存使用率: {memory_usage}%")
        print(f"磁盘使用率: {disk_usage}%")

        # 检查资源占用是否达到99%
        if cpu_usage >= 99 or memory_usage >= 99 or disk_usage >= 99:
            blue_screen()

        time.sleep(5)

if __name__ == "__main__":
    monitor_resources()