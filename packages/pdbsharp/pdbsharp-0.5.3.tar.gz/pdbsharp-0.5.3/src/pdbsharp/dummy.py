def dummy():
    import os
    import time

    x = 0
    while True:
        x += 1
        print(f"{os.getpid(): <8} {x: > 8}")
        time.sleep(1)


if __name__ == "__main__":
    dummy()
