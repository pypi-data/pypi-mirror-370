# encoding:utf-8
from python_stl_example.stl_vector import Vector
from python_stl_example.stl_deque import Deque
from python_stl_example.stl_list import SinglyLinkedList, DoublyLinkedList
from python_stl_example.stl_set import Set
from python_stl_example.stl_stack import Stack

__all__ = [
    "vector",
    "deque",
    "forward_list",
    "list",
    "set",
    "stack",
    "sort",
    "swap"
]

vector = Vector
deque = Deque
forward_list = SinglyLinkedList
list = DoublyLinkedList
set = Set
stack = Stack


def ERROR(args, typeList, isTypeCheck=False):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isTypeCheck:
                if arg == t:
                    is_valid = True
                    break
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError(f"The arg must be one of the following types: {typeList}.")


def sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr  # 递归终止
    pivot = arr[0]  # 选第一个元素为基准值
    left = [x for x in arr[1:] if x <= pivot]  # 小于等于基准值的元素
    right = [x for x in arr[1:] if x > pivot]  # 大于基准值的元素
    return sort(left) + [pivot] + sort(right)  # 递归拼接


def swap(value1, value2):
    """交换两个值，返回交换后的元组。支持兼容类型，对不可变类型返回新值。"""
    # 优化类型检查：允许子类实例（如bool是int的子类）
    if not isinstance(value1, type(value2)) and not isinstance(value2, type(value1)):
        raise TypeError("value1 and value2 must be of compatible types")

    # 直接返回交换后的元组（对所有类型通用）
    return value2, value1


if __name__ == '__main__':
    v1 = Vector((1, 2, 3), int)
    v2 = Vector((4, 5, 6), int)
    v1, v2 = swap(v1, v2)
    for i in v1.l:
        print(i)
    for i in v2.l:
        print(i)
