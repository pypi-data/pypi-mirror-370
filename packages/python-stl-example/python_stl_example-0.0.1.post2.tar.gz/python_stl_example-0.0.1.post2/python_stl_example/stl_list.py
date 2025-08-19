# encoding:utf-8
from __future__ import annotations
from python_stl_example.except_error import decorate
from typing import Any, Type

__all__ = [
    "SinglyLinkedList",
    "DoublyLinkedList"
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
    """链表节点（单向）"""

    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList(object):
    """实现 list 单向链表的 STL 结构"""

    def __init__(self, l: tuple, Tp: Type[Any]):
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self.head = None  # 头节点
        self._Tp = Tp
        self._size = 0
        for item in l:
            self.push_back(item)

    @decorate()
    def push_front(self, value: Any) -> None:
        """push_front(): 在链表顶部添加元素"""
        ERROR([value], [self._Tp])
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    @decorate()
    def push_back(self, value: Any) -> None:  # 补充类型注解
        """push_back(): 在链表尾部添加元素"""
        ERROR([value], [self._Tp])
        new_node = Node(value)
        if self.empty():
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    @decorate()
    def pop_front(self) -> None:
        """pop_front(): 在链表顶部删除元素"""
        if self.empty():
            raise IndexError("Cannot pop from empty linked list")
        if self._size == 1:
            self.head = None
        else:
            self.head = self.head.next
        self._size -= 1

    @decorate()
    def pop_back(self) -> None:
        """pop_back(): 在链表尾部删除元素"""
        if self.empty():
            raise IndexError("Cannot pop from empty linked list")
        if self._size == 1:
            self.head = None
        else:
            current = self.head
            while current.next.next:
                current = current.next
            current.next = None
        self._size -= 1

    @decorate()
    def insert(self, index: int, value: Any) -> None:
        """insert(): 在指定索引插入元素（0-based）"""
        ERROR([index], [int])
        ERROR([value], [self._Tp])
        if index < 0 or index > self._size:
            raise IndexError("Insert index out of range")
        if index == 0:
            self.push_front(value)
            return
        current = self.head
        for _ in range(index - 1):
            current = current.next
        new_node = Node(value)
        new_node.next = current.next
        current.next = new_node
        self._size += 1

    @decorate()
    def begin(self) -> Any:
        """begin(): 返回第一个元素"""
        if self.empty():
            raise IndexError("Cannot get begin from empty linked list")
        return self.head.data

    @decorate()
    def end(self) -> Any:
        """end(): 返回最后一个元素"""
        if self.empty():
            raise IndexError("Cannot get end from empty linked list")  # 修正错误信息
        current = self.head
        while current.next:
            current = current.next
        return current.data

    @decorate()
    def size(self) -> int:
        """size(): 返回链表长度"""
        return self._size

    @decorate()
    def erase(self, first: int, last: int = None) -> None:
        """erase(): 删除[first, last)区间元素"""
        ERROR([first], [int])
        if last is not None:
            ERROR([last], [int])
            if last <= first:
                raise ValueError("last must be greater than first")
        if first < 0 or (last is not None and last > self._size) or first >= self._size:
            raise IndexError("erase index out of range")
        delete_count = 1 if last is None else last - first

        if last is None:
            if first == 0:
                self.head = self.head.next
            else:
                current = self.head
                for _ in range(first - 1):
                    current = current.next
                current.next = current.next.next
        else:
            if first == 0:
                current = self.head
                for _ in range(last):
                    current = current.next
                self.head = current
            else:
                prev = self.head
                for _ in range(first - 1):
                    prev = prev.next
                last_node = prev
                for _ in range(delete_count + 1):
                    last_node = last_node.next
                prev.next = last_node
        self._size -= delete_count

    @decorate()
    def remove(self, value: Any) -> None:
        """remove(): 删除所有值为value的元素"""
        ERROR([value], [self._Tp])
        del_nums = 0
        while not self.empty() and self.head.data == value:
            self.head = self.head.next
            self._size -= 1
            del_nums += 1
        if not self.empty():
            current = self.head
            while current.next:
                if current.next.data == value:
                    current.next = current.next.next
                    self._size -= 1
                    del_nums += 1
                else:
                    current = current.next
        if del_nums == 0:
            raise ValueError(f"The value {value} is not in linked list")

    def clear(self) -> None:  # 补充返回值注解
        """clear(): 清空链表"""
        self.head = None
        self._size = 0

    @decorate()
    def empty(self) -> bool:
        """empty(): 检查是否为空"""
        return self.head is None

    @decorate()
    def reverse(self) -> None:
        """reverse(): 反转链表"""
        if self._size <= 1:
            return
        prev, current = None, self.head
        while current:
            next_node = current.next
            current.next = prev
            prev, current = current, next_node
        self.head = prev

    @decorate()
    def sort(self) -> None:
        """sort(): 归并排序（升序）"""
        if self._size <= 1:
            return

        def merge_sort(head: Node) -> Node:
            """merge_sort(): 归并排序"""
            if not head or not head.next:
                return head
            slow, fast = head, head.next
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
            mid = slow.next
            slow.next = None
            left = merge_sort(head)
            right = merge_sort(mid)
            dummy = Node(None)
            current = dummy
            while left and right:
                if left.data <= right.data:
                    current.next = left
                    left = left.next
                else:
                    current.next = right
                    right = right.next
                current = current.next
            current.next = left if left else right
            return dummy.next

        self.head = merge_sort(self.head)

    @decorate()
    def unique(self) -> None:
        """unique(): 移除连续重复元素"""
        if self._size <= 1:
            return
        current = self.head
        while current.next:
            if current.data == current.next.data:
                current.next = current.next.next
                self._size -= 1
            else:
                current = current.next

    @decorate()
    def merge(self, other: SinglyLinkedList) -> None:  # 修正参数类型为单向链表
        """merge(): 合并两个有序单向链表"""
        if not isinstance(other, SinglyLinkedList):
            raise TypeError("other must be a SinglyLinkedList instance")
        if self._Tp != other._Tp:
            raise TypeError("Cannot merge lists with different element types")
        if self.empty():
            self.head = other.head
            self._size = other._size
            other.clear()
            return
        if other.empty():
            return

        dummy = Node(None)
        current = dummy
        p1, p2 = self.head, other.head
        while p1 and p2:
            if p1.data <= p2.data:
                current.next = p1
                p1 = p1.next
            else:
                current.next = p2
                p2 = p2.next
            current = current.next
        current.next = p1 if p1 else p2
        self.head = dummy.next
        self._size += other._size
        other.clear()

    @decorate()
    def print(self) -> None:  # 补充返回值注解，优化输出格式
        """print(): 打印链表元素（空格分隔）"""
        if self.empty():
            return
        current = self.head
        result = []
        while current:
            result.append(str(current.data))
            current = current.next
        print(" ".join(result))  # 一行输出，空格分隔


class DoublyNode:
    """双向链表节点"""
    def __init__(self, data):
        self.data = data
        self.prev = None  # 前向指针
        self.next = None  # 后向指针


class DoublyLinkedList(object):
    """实现 list 双向链表的 STL 结构"""

    def __init__(self, l: tuple, Tp: Type[Any]):
        ERROR([l], [tuple])
        ERROR([Tp], [type], True)
        self.head = None
        self.tail = None
        self._Tp = Tp
        self._size = 0
        for item in l:
            self.push_back(item)

    @decorate()
    def push_front(self, value: Any) -> None:
        """push_front(): 头部添加元素"""
        ERROR([value], [self._Tp])
        new_node = DoublyNode(value)
        if self.empty():
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    @decorate()
    def push_back(self, value: Any) -> None:
        """push_back(): 尾部添加元素"""
        ERROR([value], [self._Tp])
        new_node = DoublyNode(value)
        if self.empty():
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    @decorate()
    def pop_front(self) -> None:
        """pop_front(): 头部删除元素"""
        if self.empty():
            raise IndexError("Cannot pop from empty linked list")
        if self._size == 1:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        self._size -= 1

    @decorate()
    def pop_back(self) -> None:
        """pop_back(): 尾部删除元素"""
        if self.empty():
            raise IndexError("Cannot pop from empty linked list")
        if self._size == 1:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self._size -= 1

    @decorate()
    def insert(self, index: int, value: Any) -> None:
        """insert(): 指定索引插入元素"""
        ERROR([index], [int])
        ERROR([value], [self._Tp])
        if index < 0 or index > self._size:
            raise IndexError("Insert index out of range")
        if index == 0:
            self.push_front(value)
            return

        current = self.head
        for _ in range(index - 1):
            current = current.next
        new_node = DoublyNode(value)
        new_node.next = current.next
        new_node.prev = current
        if current.next:  # 若插入位置不是尾部，更新后节点的prev
            current.next.prev = new_node
        current.next = new_node
        if index == self._size:  # 插入尾部时更新tail
            self.tail = new_node
        self._size += 1

    @decorate()
    def begin(self) -> Any:
        """begin(): 返回第一个元素"""
        if self.empty():
            raise IndexError("Cannot get begin from empty linked list")
        return self.head.data

    @decorate()
    def end(self) -> Any:
        """end(): 返回最后一个元素"""
        if self.empty():
            raise IndexError("Cannot get end from empty linked list")  # 修正错误信息
        return self.tail.data

    @decorate()
    def size(self) -> int:
        """size(): 获取链表长度"""
        return self._size

    @decorate()
    def erase(self, first: int, last: int = None) -> None:
        """erase(): 删除[first, last)区间元素"""
        ERROR([first], [int])
        if last is not None:
            ERROR([last], [int])
            if last <= first:
                raise ValueError("last must be greater than first")
        if first < 0 or (last is not None and last > self._size) or first >= self._size:
            raise IndexError("erase index out of range")
        delete_count = 1 if last is None else last - first

        if last is None:
            if first == 0:
                new_head = self.head.next
                if new_head:
                    new_head.prev = None
                else:
                    self.tail = None
                self.head = new_head
            else:
                prev_node = self.head
                for _ in range(first - 1):
                    prev_node = prev_node.next
                next_node = prev_node.next.next
                prev_node.next = next_node
                if next_node:
                    next_node.prev = prev_node
                else:
                    self.tail = prev_node
        else:
            if first == 0:
                new_head = self.head
                for _ in range(last):
                    new_head = new_head.next
                if new_head:
                    new_head.prev = None
                else:
                    self.tail = None
                self.head = new_head
            else:
                prev_node = self.head
                for _ in range(first - 1):
                    prev_node = prev_node.next
                last_node = prev_node
                for _ in range(delete_count + 1):
                    last_node = last_node.next
                prev_node.next = last_node
                if last_node:
                    last_node.prev = prev_node
                else:
                    self.tail = prev_node
        self._size -= delete_count

    @decorate()
    def remove(self, value: Any) -> None:
        """remove(): 删除所有值为value的元素"""
        ERROR([value], [self._Tp])
        del_nums = 0
        while not self.empty() and self.head.data == value:
            new_head = self.head.next
            if new_head:
                new_head.prev = None
            else:
                self.tail = None
            self.head = new_head
            self._size -= 1
            del_nums += 1

        if not self.empty():
            current = self.head
            while current.next:
                if current.next.data == value:
                    next_node = current.next.next
                    current.next = next_node
                    if next_node:
                        next_node.prev = current
                    else:
                        self.tail = current
                    self._size -= 1
                    del_nums += 1
                else:
                    current = current.next

        if del_nums == 0:
            raise ValueError(f"The value {value} is not in linked list")

    @decorate()
    def clear(self) -> None:  # 补充返回值注解
        """clear(): 清空链表"""
        self.head = None
        self.tail = None
        self._size = 0

    @decorate()
    def empty(self) -> bool:
        """empty(): 返回链表是否为空"""
        return self.head is None

    @decorate()
    def reverse(self) -> None:
        """reverse(): 反转链表（维护双向指针）"""
        if self._size <= 1:
            return
        prev, current = None, self.head
        while current:
            next_node = current.next
            current.next = prev  # 反转后向指针
            current.prev = next_node  # 反转前向指针
            prev, current = current, next_node
        # 交换头尾
        self.head, self.tail = self.tail, self.head

    @decorate()
    def sort(self) -> None:
        """sort(): 归并排序（维护双向指针）"""
        if self._size <= 1:
            return

        def merge_sort(head: DoublyNode) -> DoublyNode:
            """merge_sort(): 归并排序"""
            if not head or not head.next:
                return head
            # 拆分
            slow, fast = head, head.next
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
            mid = slow.next
            slow.next = None
            if mid:
                mid.prev = None  # 断开前向指针
            # 递归排序
            left = merge_sort(head)
            right = merge_sort(mid)
            # 合并（维护双向指针）
            dummy = DoublyNode(None)
            current = dummy
            while left and right:
                if left.data <= right.data:
                    current.next = left
                    left.prev = current  # 设置前向指针
                    left = left.next
                else:
                    current.next = right
                    right.prev = current  # 设置前向指针
                    right = right.next
                current = current.next
            # 处理剩余节点
            if left:
                current.next = left
                left.prev = current
            else:
                current.next = right
                if right:
                    right.prev = current
            return dummy.next

        self.head = merge_sort(self.head)
        # 重新定位tail
        self.tail = self.head
        while self.tail.next:
            self.tail = self.tail.next

    @decorate()
    def unique(self) -> None:
        """unique(): 移除连续重复元素（维护双向指针）"""
        if self._size <= 1:
            return
        current = self.head
        while current.next:
            if current.data == current.next.data:
                del_node = current.next
                current.next = del_node.next
                if del_node.next:
                    del_node.next.prev = current  # 更新前向指针
                else:
                    self.tail = current  # 更新tail
                self._size -= 1
            else:
                current = current.next

    @decorate()
    def merge(self, other: DoublyLinkedList) -> None:
        """merge(): 合并两个有序双向链表（维护双向指针）"""
        if not isinstance(other, DoublyLinkedList):
            raise TypeError("other must be a DoublyLinkedList instance")
        if self._Tp != other._Tp:
            raise TypeError("Cannot merge lists with different element types")
        if self.empty():
            self.head = other.head
            self.tail = other.tail
            self._size = other._size
            other.clear()
            return
        if other.empty():
            return

        dummy = DoublyNode(None)
        current = dummy
        p1, p2 = self.head, other.head
        while p1 and p2:
            if p1.data <= p2.data:
                current.next = p1
                p1.prev = current  # 设置前向指针
                p1 = p1.next
            else:
                current.next = p2
                p2.prev = current  # 设置前向指针
                p2 = p2.next
            current = current.next

        # 处理剩余节点并维护前向指针
        if p1:
            current.next = p1
            p1.prev = current
        else:
            current.next = p2
            if p2:
                p2.prev = current

        # 更新头和尾
        self.head = dummy.next
        self.head.prev = None  # 新头节点prev置空
        # 重新定位tail
        self.tail = self.head
        while self.tail.next:
            self.tail = self.tail.next
        self._size += other._size
        other.clear()

    @decorate()
    def print(self) -> None:  # 补充返回值注解，优化输出格式
        """print(): 打印链表元素（空格分隔）"""
        if self.empty():
            return
        current = self.head
        result = []
        while current:
            result.append(str(current.data))
            current = current.next
        print(" ".join(result))  # 一行输出，空格分隔


# 测试代码
if __name__ == "__main__":
    # 单向链表测试
    sll = SinglyLinkedList((3, 1, 2), int)
    sll.sort()
    sll.print()  # 输出：1 2 3

    # 双向链表测试
    dll1 = DoublyLinkedList((1, 3, 5), int)
    dll2 = DoublyLinkedList((2, 4, 6), int)
    dll1.merge(dll2)
    dll1.print()  # 输出：1 2 3 4 5 6
    dll1.reverse()
    dll1.print()  # 输出：6 5 4 3 2 1
