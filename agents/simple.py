def multiply(a: int, b: int):
    return a * b


def run(a: int, b: int):
    final = multiply(a, b)
    print(final)
    router(final)
    return final

def router(final: int):
    if final > 2 and final < 1000:
        run(final, 2)
    elif final > 1000:
        return final

def main(a, b):
    final = run(a, b)
    router(final)

main(10, 2)
