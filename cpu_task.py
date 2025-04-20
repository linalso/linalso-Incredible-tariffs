import multiprocessing
import os

def compute_intensive_task(data):
    # 模拟一个计算密集型任务
    result = 0
    for i in range(1000000):
        result += i * data
    return result

def main():
    # 获取 CPU 核心数
    cpu_count = multiprocessing.cpu_count()
    
    # 创建数据集
    data = [i for i in range(1000)]
    
    # 使用 multiprocessing.Pool 提高 CPU 利用率
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.map(compute_intensive_task, data)
    
    print(f"任务完成，结果总数: {len(results)}")

if __name__ == "__main__":
    main()