# encoding:utf-8
from __future__ import annotations

from python_stl_example.except_error import decorate
from typing import Any, Type
from collections import deque

__all__ = [
    "Deque"
]

def ERROR(args, typeList, isTypeCheck=False):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isTypeCheck and isinstance(arg, t):
                is_valid = True
                break
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError("The arg must be one of the following types: " + str(typeList) + ".")


class _Deque(object):
    """此类实现 deque 的 STL 结构（基类）"""

    def __init__(self, l: tuple, Tp: Type[Any]):
        # 类型检查：l必须是tuple，Tp必须是类型
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self.l = l  # 存储元素的元组（对外暴露，不可变）
        self._Tp = Tp  # 元素类型（实例独立）
        self._inner_list = deque(l)  # 内部双端队列，支持高效首尾操作

    @decorate()
    def push_front(self, value: Any) -> None:
        """push_front(): 在队首添加元素（O(1)）"""
        if not isinstance(value, self._Tp):
            raise TypeError(f"value must be {self._Tp.__name__} type")
        self._inner_list.appendleft(value)
        self.l = tuple(self._inner_list)  # 同步对外元组

    @decorate()
    def push_back(self, value: Any) -> None:
        """push_back(): 在队尾添加元素（O(1)）"""
        if not isinstance(value, self._Tp):
            raise TypeError(f"value must be {self._Tp.__name__} type")
        self._inner_list.append(value)
        self.l = tuple(self._inner_list)  # 同步对外元组

    @decorate()
    def pop_front(self) -> Any:
        """pop_front(): 删除并返回队首元素（O(1)）"""
        if self.empty():
            raise IndexError("Cannot pop from empty deque")
        value = self._inner_list.popleft()
        self.l = tuple(self._inner_list)  # 同步对外元组
        return value

    @decorate()
    def pop_back(self) -> Any:
        """pop_back(): 删除并返回队尾元素（O(1)）"""
        if self.empty():
            raise IndexError("Cannot pop from empty deque")
        value = self._inner_list.pop()
        self.l = tuple(self._inner_list)  # 同步对外元组
        return value

    @decorate()
    def front(self) -> Any:
        """front(): 返回队首元素（不删除，O(1)）"""
        if self.empty():
            raise IndexError("Deque is empty")
        return self._inner_list[0]

    @decorate()
    def back(self) -> Any:
        """back(): 返回队尾元素（不删除，O(1)）"""
        if self.empty():
            raise IndexError("Deque is empty")
        return self._inner_list[-1]

    @decorate()
    def size(self) -> int:
        """size(): 返回元素数量（O(1)）"""
        return len(self._inner_list)

    @decorate()
    def empty(self) -> bool:
        """empty(): 判断队列是否为空（O(1)）"""
        return len(self._inner_list) == 0

    @decorate()
    def clear(self) -> None:
        """clear(): 清空所有元素（O(1)）"""
        self._inner_list.clear()
        self.l = tuple(self._inner_list)  # 同步对外元组

    @decorate()
    def reverse(self) -> None:
        """reverse(): 翻转队列元素（O(n)）"""
        self._inner_list.reverse()
        self.l = tuple(self._inner_list)  # 同步对外元组


class Deque(_Deque):
    """双端队列公开类，继承基类逻辑"""
    pass


# 测试代码
if __name__ == "__main__":
    d = Deque((1, 2, 3), int)
    print("初始化后:", d.l)  # (1, 2, 3)

    d.push_front(0)
    d.push_back(4)
    print("首尾添加后:", d.l)  # (0, 1, 2, 3, 4)

    print("队首:", d.front())  # 0
    print("队尾:", d.back())  # 4

    print("弹出队首:", d.pop_front())  # 0
    print("弹出队尾:", d.pop_back())  # 4
    print("弹出后:", d.l)  # (1, 2, 3)

    d.reverse()
    print("翻转后:", d.l)  # (3, 2, 1)

    print("大小:", d.size())  # 3
    print("是否为空:", d.empty())  # False

    d.clear()
    print("清空后:", d.l)  # ()
    print("是否为空:", d.empty())  # True
