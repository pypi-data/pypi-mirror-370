"""
测试函数模块

提供用于RQ测试的函数。
"""


def test_simple_function():
    """简单的测试函数"""
    return "Hello from RQ test function!"


def test_function_with_args(name: str, age: int):
    """带参数的测试函数"""
    return f"Hello {name}, you are {age} years old!"


def test_function_with_error():
    """会抛出错误的测试函数"""
    raise ValueError("This is a test error")


def test_long_running_function():
    """长时间运行的测试函数"""
    import time
    time.sleep(2)
    return "Long running task completed!"
