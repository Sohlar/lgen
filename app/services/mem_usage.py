import os
import psutil

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    total_memory = psutil.virtual_memory().total
    percentage_used = (mem_info.rss / total_memory) * 100
    print(f"Current memory usage: {percentage_used:.2f}% of total memory")