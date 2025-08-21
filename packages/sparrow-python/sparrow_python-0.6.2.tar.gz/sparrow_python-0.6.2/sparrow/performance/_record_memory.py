from recordclass import recordclass, RecordClass, make_dataclass, dataobject

# Point = recordclass('Point', 'x y')
# p = Point(1,2)
# print(p)
# Point(1, 2)

if __name__ == "__main__":
    from sys import getsizeof as sizeof
    from collections import namedtuple
    import sys

    sysversion = sys.version
    print(type(sysversion), sysversion.split('\n'))


    # print(sys.platform)

    class Point(RecordClass):
        x: int
        y: int


    p = Point(1, 2, )
    print(p.x, p.y)
    print(p)
    p.x = 3
    print(p)
    print(sys.getsizeof(p))
