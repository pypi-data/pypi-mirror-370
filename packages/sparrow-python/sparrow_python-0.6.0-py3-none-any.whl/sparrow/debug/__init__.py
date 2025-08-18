import pysnooper
import random


if __name__ == "__main__":
    def foo():
        lst = []
        for i in range(10):
            lst.append(random.randrange(1, 1000))

        with pysnooper.snoop():
            lower = min(lst)
            upper = max(lst)
            mid = (lower + upper) / 2
            print(lower, mid, upper)

    foo()
