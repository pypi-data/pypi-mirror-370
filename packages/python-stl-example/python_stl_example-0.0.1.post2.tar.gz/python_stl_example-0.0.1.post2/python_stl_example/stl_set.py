# encoding:utf-8
from __future__ import annotations
from python_stl_example.except_error import decorate
from typing import Any, Type, Optional
import bisect

__all__ = [
    "Set"
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


# 迭代器类（模拟 STL 迭代器）
class SetIterator:
    """此类实现 STL 迭代器"""

    def __init__(self, data: list, index: int):
        self.data = data
        self.index = index

    def __iter__(self) -> SetIterator:
        return self

    def __next__(self) -> Any:
        if self.index >= len(self.data):
            raise StopIteration
        value = self.data[self.index]
        self.index += 1
        return value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SetIterator):
            return self.data == other.data and self.index == other.index
        return False


class _Set(object):
    """此类实现 set 的 STL 结构（基于有序列表 + bisect 模拟）"""

    def __init__(self, l: tuple, Tp: Type[Any]) -> None:
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self._Tp = Tp
        self._data = []  # 用有序列表模拟 STL set 的有序性
        for item in l:
            self.insert(item)  # 初始化时插入元素，保证有序

    @decorate()
    def begin(self) -> SetIterator:
        """begin(): 获取起始迭代器（类似 STL set::begin）"""
        return SetIterator(self._data, 0)

    @decorate()
    def end(self) -> SetIterator:
        """end(): 获取结束迭代器（类似 STL set::end，指向尾后位置）"""
        return SetIterator(self._data, len(self._data))

    @decorate()
    def insert(self, value: Any) -> None:
        """insert(): 插入元素（类似 STL set::insert），保证有序且不重复"""
        ERROR([value], [self._Tp])
        # 利用 bisect 找插入位置，保证有序；set 不允许重复，已存在则不插入
        idx = bisect.bisect_left(self._data, value)
        if idx < len(self._data) and self._data[idx] == value:
            return  # 已存在，不插入
        self._data.insert(idx, value)

    @decorate()
    def erase(self, *args) -> None:
        """erase():
        重载删除逻辑：
        - erase(it)：删除迭代器指向元素
        - erase(start, end)：删除区间 [start, end) 元素
        - erase(value)：删除值为 value 的元素（set 中最多一个）
        """
        # 处理单参数情况
        if len(args) == 1:
            arg = args[0]
            # 判断是否为迭代器
            if isinstance(arg, SetIterator):
                # 1. 删除迭代器指向元素
                if arg.index < 0 or arg.index >= len(self._data):
                    raise IndexError("Iterator out of range")
                self._data.pop(arg.index)
            else:
                # 2. 删除值为 arg 的元素
                value = arg
                ERROR([value], [self._Tp])
                idx = bisect.bisect_left(self._data, value)
                if idx < len(self._data) and self._data[idx] == value:
                    self._data.pop(idx)
                else:
                    raise ValueError(f"Value {value} not in set")
        # 处理双参数情况（区间删除）
        elif len(args) == 2:
            start, end = args
            if not (isinstance(start, SetIterator) and isinstance(end, SetIterator)):
                raise TypeError("erase with two arguments requires iterators")
            if start.index < 0 or end.index > len(self._data) or start.index > end.index:
                raise IndexError("Invalid range for erase")
            del self._data[start.index:end.index]
        else:
            raise TypeError(f"erase takes 1 or 2 arguments, got {len(args)}")

    @decorate()
    def find(self, value: Any) -> Optional[SetIterator]:
        """find(): 查找元素，返回迭代器；不存在返回 end()"""
        ERROR([value], [self._Tp])
        idx = bisect.bisect_left(self._data, value)
        if idx < len(self._data) and self._data[idx] == value:
            return SetIterator(self._data, idx)
        return self.end()

    @decorate()
    def clear(self) -> None:
        """clear(): 清空容器（类似 STL set::clear）"""
        self._data.clear()

    @decorate()
    def size(self) -> int:
        """size(): 返回元素个数（类似 STL set::size）"""
        return len(self._data)

    @decorate()
    def empty(self) -> bool:
        """empty(): 判断是否为空（类似 STL set::empty）"""
        return len(self._data) == 0

    @decorate()
    def lower_bound(self, value: Any) -> SetIterator:
        """lower_bound(): 找大于等于 value 的最小元素迭代器（类似 STL set::lower_bound）"""
        ERROR([value], [self._Tp])
        idx = bisect.bisect_left(self._data, value)
        return SetIterator(self._data, idx)

    @decorate()
    def upper_bound(self, value: Any) -> SetIterator:
        """upper_bound(): 找大于 value 的最小元素迭代器（类似 STL set::upper_bound）"""
        ERROR([value], [self._Tp])
        idx = bisect.bisect_right(self._data, value)
        return SetIterator(self._data, idx)

    @decorate()
    def count(self, value: Any) -> int:
        """count(): 统计等于 value 的元素个数（set 中只能是 0 或 1）"""
        ERROR([value], [self._Tp])
        idx = bisect.bisect_left(self._data, value)
        if idx < len(self._data) and self._data[idx] == value:
            return 1
        return 0

    def __iter__(self) -> SetIterator:
        """支持 for 循环遍历"""
        return self.begin()


class Set(_Set):
    """此类实现 set 的 STL 结构"""
    pass


# 测试代码
if __name__ == "__main__":
    # 初始化测试
    s = _Set((3, 1, 2), int)
    print("Initial set elements:", list(s))  # 应输出 [1, 2, 3]

    # insert 测试
    s.insert(4)
    print("After insert 4:", list(s))  # 输出 [1, 2, 3, 4]

    # erase 测试（迭代器方式）
    it = s.find(2)
    s.erase(it)
    print("After erase 2 (iterator):", list(s))  # 输出 [1, 3, 4]

    # erase 测试（值方式）
    s.erase(3)
    print("After erase 3 (value):", list(s))  # 输出 [1, 4]

    # lower_bound / upper_bound 测试
    lb = s.lower_bound(2)
    ub = s.upper_bound(2)
    print("Lower bound of 2:", next(lb) if lb != s.end() else "end")  # 输出 4
    print("Upper bound of 2:", next(ub) if ub != s.end() else "end")  # 输出 4

    # count 测试
    print("Count of 4:", s.count(4))  # 输出 1
    print("Count of 5:", s.count(5))  # 输出 0

    # clear 测试
    s.clear()
    print("After clear, empty?", s.empty())  # 输出 True
