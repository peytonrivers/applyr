from playwright.sync_api import sync_playwright
import json

def math_process(a: int, b: int):
    c = a + b
    d = a * b
    return c,d

print(math_process(2, 4))