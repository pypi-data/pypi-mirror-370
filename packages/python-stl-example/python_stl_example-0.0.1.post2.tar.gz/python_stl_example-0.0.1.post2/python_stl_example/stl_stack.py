# encoding:utf-8
from __future__ import annotations
from python_stl_example.except_error import decorate
from typing import Any, Type

__all__ = [
    "Stack"
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


class Node(object):
    """栈节点（仅用 prev 指针模拟栈的链式结构）"""

    def __init__(self, data):
        self.data = data
        self.prev = None  # 指向前一个入栈的节点（栈底方向）


class _Stack(object):
    """实现 stack 的 STL 结构（基于单向节点，LIFO 特性）"""

    def __init__(self, l: tuple, Tp: Type[Any]):
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self._top = None  # 栈顶指针（指向最后入栈的节点）
        self._Tp = Tp
        self._size = 0
        for item in l:
            self.push(item)  # 初始化时依次入栈

    @decorate()
    def push(self, value: Any) -> None:
        """push(): 入栈：在栈顶添加元素（LIFO 特性）"""
        ERROR([value], [self._Tp])
        new_node = Node(value)
        if self._size == 0:
            # 空栈时，栈顶直接指向新节点
            self._top = new_node
        else:
            # 非空栈时，新节点的 prev 指向原栈顶，再更新栈顶为新节点
            new_node.prev = self._top
            self._top = new_node
        self._size += 1

    @decorate()
    def pop(self) -> None:
        """pop(): 出栈：删除并返回栈顶元素（LIFO 特性）"""
        if self.empty():
            raise IndexError("Cannot pop from empty stack")
        # 更新栈顶为前一个节点（原栈顶的 prev）
        self._top = self._top.prev
        self._size -= 1

    @decorate()
    def top(self) -> Any:
        """top(): 获取栈顶元素（不删除）"""
        if self.empty():
            raise IndexError("Stack is empty")
        return self._top.data

    @decorate()
    def empty(self) -> bool:
        """empty(): 判断栈是否为空"""
        return self._size == 0

    @decorate()
    def size(self) -> int:
        """size(): 返回栈中元素个数"""
        return self._size

    @decorate()
    def clear(self) -> None:
        """clear(): 清空栈"""
        self._top = None
        self._size = 0


class Stack(_Stack):
    """实现 stack 的 STL 结构（基于单向节点，LIFO 特性）"""
    pass


# 测试代码
if __name__ == "__main__":
    s = Stack((1, 2, 3, 4, 5, 6), int)
    print(s.top())
