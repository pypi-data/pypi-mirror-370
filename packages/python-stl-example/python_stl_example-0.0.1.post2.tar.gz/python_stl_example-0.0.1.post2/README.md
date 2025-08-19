# python_stl_example

## 一个STL扩展库

Python要求：版本≥3.5.0

## 安装方法（重点！！！）
1. 在cmd中使用`pip install python_stl_example`下载安装
2. 在PYPI网站中下载：
   - 可下载.whl文件，在下载目录的cmd中输入`pip install 文件名.whl`安装
   - 可下载压缩包，解压后在当前目录的cmd中输入`python setup.py install`安装

## 项目分支
1. **vector**
   - 模拟向量STL结构的`vector`，提供类似函数接口。

2. **deque**
   - 模拟双向队列STL结构的`deque`，提供类似函数接口。

3. **list**
   - 模拟单向和双向链表STL结构的`list`，提供类似函数接口。

4. **set**
   - 模拟集合STL结构的`set`，提供类似函数接口。

5. **stack**
   - 模拟栈STL结构的`stack`，提供类似函数接口。

## 异常处理
- 内置`decorate`装饰器，为各类函数提供统一的异常处理机制，支持日志记录、异常抑制、返回默认值等功能，增强代码的健壮性。

## 使用示例
```python
# 栈演示
from python_stl_example import stack

s = stack((1, 2, 3, 4), int)
s.push(5)
print(s.top()) # 输出：5

s.pop()
s.pop()
s.pop()
s.pop()
print(s.top()) # 输出：1
```
