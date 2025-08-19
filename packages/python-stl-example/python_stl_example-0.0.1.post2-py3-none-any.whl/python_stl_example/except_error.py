# encoding:utf-8
import functools
import logging
import asyncio
from typing import Callable, Optional, Any
import math

# 配置日志记录
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def decorate(
        log_message: str = "函数 {func_name} 出错: {error}",
        log_level: int = logging.ERROR,
        suppress_exception: bool = False,
        default_return: Any = math.nan,
        custom_logger: Optional[logging.Logger] = None
) -> Callable:
    """
    功能强大的异常处理装饰器，支持同步和异步函数、类方法

    特别说明:
    - 兼容类方法装饰，不会改变原方法的类型特性
    - 保留方法的元数据，确保isinstance等类型检查正常工作

    参数:
        log_message: 自定义日志消息模板，可包含{func_name}和{error}占位符
        log_level: 日志级别，默认ERROR
        suppress_exception: 是否抑制异常并返回默认值
        default_return: 异常发生时的默认返回值
        custom_logger: 自定义logger实例，默认使用函数名作为logger名称
    """

    def decorator(func: Callable) -> Callable:
        # 共享异常处理逻辑
        def handle_exception(e: Exception) -> Any:
            # 获取或创建logger
            logger = custom_logger or logging.getLogger(func.__name__)

            # 格式化日志消息
            msg = log_message.format(func_name=func.__name__, error=str(e)) if log_message \
                else f"函数 {func.__name__} 执行失败: {str(e)}"

            # 记录日志
            logger.log(log_level, msg, exc_info=True)

            # 处理异常抑制
            if not suppress_exception:
                raise  # 保持原有异常上下文
            return default_return

        @functools.wraps(func)
        def Except_Error(*args, **kwargs) -> Any:
            try:
                # 对于类方法，确保self参数正确传递
                return func(*args, **kwargs)
            except Exception as e:
                return handle_exception(e)

        @functools.wraps(func)
        async def Async_Except_Error(*args, **kwargs) -> Any:
            try:
                # 对于异步类方法，确保self参数正确传递
                return await func(*args, **kwargs)
            except Exception as e:
                return handle_exception(e)

        # 根据函数类型返回对应包装器，保持原函数类型特性
        if asyncio.iscoroutinefunction(func):
            return Async_Except_Error
        else:
            return Except_Error

    return decorator
