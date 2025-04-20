import psutil
import time
from typing import Dict, List, Tuple
import threading
import numpy as np
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

def check_resource_usage():
    """
    检查系统资源占用，如果达到99%则触发蓝屏
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    if cpu_usage >= 99 or memory_usage >= 99:
        blue_screen()

class ResourceAnalyzer:
    def __init__(self):
        self.baseline_cpu = 0
        self.baseline_memory = 0
        self.current_cpu = 0
        self.current_memory = 0
        self.history: List[Tuple[float, float, float]] = []  # [(timestamp, cpu, memory)]
        self._collect_baseline()
        self._running = False  # 控制CPU占用线程的运行状态

    def _collect_baseline(self) -> None:
        """收集系统基准资源使用率"""
        cpu_samples = []
        memory_samples = []
        for _ in range(3):  # 采样3次取平均值
            cpu_samples.append(psutil.cpu_percent(interval=0.1))
            memory_samples.append(psutil.virtual_memory().percent)
        
        self.baseline_cpu = sum(cpu_samples) / len(cpu_samples)
        self.baseline_memory = sum(memory_samples) / len(memory_samples)
        self.current_cpu = self.baseline_cpu
        self.current_memory = self.baseline_memory

    def _precise_sleep(self, duration):
        """更精确的sleep实现"""
        start = time.perf_counter()
        while time.perf_counter() - start < duration:
            pass

    def start_resource_consumption(self, tariff_rate: float) -> None:
        """根据关税率增加资源消耗"""
        # 计算目标资源使用率（基于关税率）
        target_increase = 1 + (tariff_rate / 100)
        target_cpu = min(self.baseline_cpu * target_increase, 100)
        target_memory = min(self.baseline_memory * target_increase, 100)

        import os

        # 立即分配内存到目标占用
        def memory_jump_task():
            memory_list = []
            vm = psutil.virtual_memory()
            total_mem = vm.total
            # 计算目标占用的绝对值
            target_mem_bytes = int(total_mem * target_memory / 100)
            # 当前已用
            used_mem_bytes = int(total_mem * vm.percent / 100)
            # 需要额外分配的字节数
            need_bytes = max(target_mem_bytes - used_mem_bytes, 0)
            # 分配整数个MB
            chunk_size = 1024 * 1024
            chunks = need_bytes // chunk_size
            for _ in range(chunks):
                memory_list.append(bytearray(chunk_size))
            # 保持引用，防止被GC
            self._memory_list = memory_list

        # 精确控制CPU占用率
        def cpu_jump_task():
            self._running = True
            interval = 0.1  # 100ms一个周期
            smoothing = 0.9  # 平滑因子
            
            # 初始化控制变量
            error = 0.0
            prev_error = 0.0
            avg = self.baseline_cpu
            
            while self._running:
                start_time = time.perf_counter()
                
                # 目标工作时间
                target_work = interval * (target_cpu / 100)
                
                # 计算PID控制参数
                error = target_cpu - avg
                delta = error - prev_error
                adjustment = 0.1 * error + 0.001 * delta
                prev_error = error
                
                # 调整工作时间
                work_time = max(min(target_work + adjustment, interval), 0)
                
                # 执行忙等待
                self._precise_sleep(work_time)
                
                # 计算实际CPU占用
                actual_work = time.perf_counter() - start_time
                actual_cpu = (actual_work / interval) * 100
                
                # 使用指数平滑平均
                avg = smoothing * avg + (1 - smoothing) * actual_cpu
                
                # 睡眠剩余时间
                sleep_time = interval - (time.perf_counter() - start_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # 检查资源占用
                check_resource_usage()

        self.cpu_thread = threading.Thread(target=cpu_jump_task)
        self.memory_thread = threading.Thread(target=memory_jump_task)
        self.cpu_thread.daemon = True
        self.memory_thread.daemon = True
        self.memory_thread.start()
        self.cpu_thread.start()

    def get_current_usage(self) -> Tuple[float, float]:
        """获取当前资源使用率"""
        self.current_cpu = psutil.cpu_percent(interval=0.1)
        self.current_memory = psutil.virtual_memory().percent
        current_time = time.time()
        self.history.append((current_time, self.current_cpu, self.current_memory))
        return self.current_cpu, self.current_memory

    def get_resource_report(self) -> Dict[str, float]:
        """生成资源使用报告"""
        return {
            'baseline_cpu': self.baseline_cpu,
            'baseline_memory': self.baseline_memory,
            'current_cpu': self.current_cpu,
            'current_memory': self.current_memory,
            'cpu_increase': (self.current_cpu - self.baseline_cpu) / self.baseline_cpu if self.baseline_cpu > 0 else 0,
            'memory_increase': (self.current_memory - self.baseline_memory) / self.baseline_memory if self.baseline_memory > 0 else 0
        }
    
    def stop(self):
        """停止资源消耗"""
        self._running = False
        if hasattr(self, '_memory_list'):
            del self._memory_list