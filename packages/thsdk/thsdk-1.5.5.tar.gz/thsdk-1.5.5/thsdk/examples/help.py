from thsdk import THS
import time

with THS() as ths:
    print("\n=== help about ===")
    print(ths.help("about"))
    time.sleep(0.5)

    print("\n=== help doc ===")
    print(ths.help("doc"))
    time.sleep(0.5)

    print("\n=== help version ===")
    print(ths.help("version"))
    time.sleep(0.5)

    print("\n=== help donation ===")
    print(ths.help("donation"))
    time.sleep(0.5)

    print("\n=== help about ===")
    print(ths.help("about"))
    time.sleep(0.5)

    time.sleep(1)
