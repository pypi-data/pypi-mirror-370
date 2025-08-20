from dataclasses import dataclass

from strats.internal.lru_set import LRUSet


@dataclass(frozen=True)
class A:
    a: int
    b: list[int]


def test_lru_set():
    lruset = LRUSet(capacity=2)

    lruset.add(A(a=0, b=[]))
    assert lruset.contains(A(a=0, b=[]))
    assert not lruset.contains(A(a=1, b=[]))
    assert not lruset.contains(A(a=2, b=[]))

    lruset.add(A(a=0, b=[]))
    assert lruset.contains(A(a=0, b=[]))
    assert not lruset.contains(A(a=1, b=[]))
    assert not lruset.contains(A(a=2, b=[]))

    lruset.add(A(a=1, b=[]))
    assert lruset.contains(A(a=0, b=[]))
    assert lruset.contains(A(a=1, b=[]))
    assert not lruset.contains(A(a=2, b=[]))

    lruset.add(A(a=2, b=[]))
    assert not lruset.contains(A(a=0, b=[]))
    assert lruset.contains(A(a=1, b=[]))
    assert lruset.contains(A(a=2, b=[]))


def test_lru_set_with_array():
    lruset = LRUSet(capacity=2)

    lruset.add([A(a=0, b=[])])
    assert lruset.contains([A(a=0, b=[])])
    assert not lruset.contains([A(a=1, b=[])])
    assert not lruset.contains([A(a=2, b=[])])
