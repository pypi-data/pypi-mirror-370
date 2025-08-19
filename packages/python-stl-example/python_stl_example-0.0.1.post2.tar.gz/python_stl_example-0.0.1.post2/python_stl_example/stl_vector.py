# encoding:utf-8
from __future__ import annotations

import warnings
from typing import Any, Type
from python_stl_example.except_error import decorate

__all__ = [
    "Vector"
]


# 定义自定义警告类
class VectorWarnings(UserWarning):
    """Vector相关的警告类"""
    pass


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


class _Vector(object):
    """此类实现 vector 的 STL 结构（基类）"""

    def __init__(self, l: tuple, Tp: Type[Any]):
        # 类型检查：l必须是tuple，Tp必须是类型
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self.l = l  # 存储元素的元组（不可变，通过转换list修改）
        self._Tp = Tp  # 实例变量，每个实例独立保存类型，避免冲突
        self._inner_list = list(l)

    @decorate()
    def front(self) -> Any:
        """返回数组的第一个元素，空数组则报错"""
        if self.empty():
            raise IndexError("The vector is empty")
        return self._inner_list[0]

    @decorate()
    def back(self) -> Any:
        """返回数组的最后一个元素，空数组则报错"""
        if self.empty():
            raise IndexError("The vector is empty")
        return self._inner_list[-1]

    @decorate()
    def push_back(self, value: Any) -> None:
        """在数组末尾添加元素（校验类型）"""
        if not isinstance(value, self._Tp):
            raise TypeError(f"value must be {self._Tp.__name__} type")
        self._inner_list.append(value)
        self.l = tuple(self._inner_list)

    @decorate()
    def clear(self) -> None:
        """清空数组"""
        self._inner_list.clear()
        self.l = tuple(self._inner_list)

    @decorate()
    def erase(self, first: int, last: int = None) -> None:
        """删除[first, last)区间的元素（按索引，左闭右开）"""
        length = len(self._inner_list)
        if first < 0 or first >= length:
            raise IndexError("first index out of range")
        if last is None:
            del self._inner_list[first]
        else:
            if last <= first or last > length:
                raise IndexError("last index out of range")
            del self._inner_list[first:last]
        self.l = tuple(self._inner_list)

    @decorate()
    def insert(self, pos: int, value: Any, count: int = 1) -> None:
        """在 pos 位置插入 count 个 value（默认插入1个）"""
        if not isinstance(value, self._Tp):
            raise TypeError(f"value must be {self._Tp.__name__} type")
        length = len(self._inner_list)
        if pos < 0 or pos > length:
            raise IndexError("insert position out of range")
        self._inner_list[pos:pos] = [value] * count
        self.l = tuple(self._inner_list)

    @decorate()
    def pop_back(self) -> None:
        """删除最后一个元素"""
        if self.empty():
            raise IndexError("Cannot pop from empty vector")
        self._inner_list.pop()
        self.l = tuple(self._inner_list)

    @decorate()
    def size(self) -> int:
        """返回数组长度"""
        return len(self._inner_list)

    @decorate()
    def empty(self) -> bool:
        """返回数组是否为空（简化实现）"""
        return len(self._inner_list) == 0

    @decorate()
    def resize(self, length: int, args: Any = None) -> None:
        """调整数组长度：短则截断，长则补 args（需匹配类型）"""
        current_len = len(self._inner_list)
        if length < 0:
            raise ValueError("length cannot be negative")
        if length > current_len:
            warnings.warn("The length > current length", VectorWarnings)
            if args is None:
                try:
                    args = self._Tp()
                except TypeError:
                    raise ValueError("args must be provided for extension")
            if not isinstance(args, self._Tp):
                raise TypeError(f"args must be {self._Tp.__name__} type")
            add_count = length - current_len
            self._inner_list.extend([args] * add_count)
        elif length < current_len:
            self._inner_list = self._inner_list[:length]
        self.l = tuple(self._inner_list)

    @decorate()
    def reverse(self) -> None:
        """翻转数组"""
        self._inner_list.reverse()
        self.l = tuple(self._inner_list)


class Vector(_Vector):
    """动态数组类，继承基类逻辑（无需重写，保持简洁）"""
    pass


# 测试代码
if __name__ == "__main__":
    # 测试int类型的Vector
    v = Vector((1, 2, 3), int)
    print("初始化后:", v.l)  # (1, 2, 3)

    v.push_back(4)
    print("push_back(4):", v.l)  # (1, 2, 3, 4)

    print("front:", v.front())  # 1
    print("back:", v.back())  # 4

    v.erase(1, 3)  # 删除索引1-2（元素2,3）
    print("erase(1,3):", v.l)  # (1, 4)

    v.insert(1, 2, 2)  # 在索引1插入2个2
    print("insert(1,2,2):", v.l)  # (1, 2, 2, 4)

    v.pop_back()
    print("pop_back():", v.l)  # (1, 2, 2)

    v.resize(5, 0)  # 扩展到5个元素，补0
    print("resize(5,0):", v.l)  # (1, 2, 2, 0, 0)

    v.reverse()
    print("reverse():", v.l)  # (0, 0, 2, 2, 1)

    v.clear()
    print("clear():", v.l)  # ()
    print("empty:", v.empty())  # True
