from playwright.sync_api import sync_playwright
import json
import psutil
import tracemalloc

memory = psutil.virtual_memory()
cpu_usage = psutil.cpu_percent(interval=1)

tracemalloc.start()
snapshot = tracemalloc.take_snapshot()
statisticts = snapshot.statistics('lineno')

for stat in statisticts[:10]:
    print(f"stat: {stat}")

print(f"ram memory: {memory.percent}%")
print(f"cpu usage: {cpu_usage}%")

def math_process(a: int, b: int):
    c = a + b
    d = a * b
    return c,d

print(math_process(2, 4))