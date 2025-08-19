import copy
from .context import Context


class GoodException(Exception):
    """
    :param code: 错误码（整数或字符串）
    :param ctx: 上下文
    """

    def __init__(self, code: int, name: str, ctx: Context = None):
        self.code = code  # 错误码
        self.name = name  # 异常名称
        self.message = ""  # 错误信息
        self.context = ctx  # 上下文
        self.cause = None
        super().__init__(name)  # 调用父类构造器，确保异常信息可被捕获

    def with_cause(self, cause: Exception):
        self.cause = cause
        return self

    def with_msg(self, msg: str):
        self.message = msg
        return self

    def with_context(self, ctx: Context):
        self.context = ctx
        return self

    def __str__(self) -> str:
        return f"GoodException(code={self.code}, name={self.name}, message={self.message!r}, ctx={self.context!r})"

    def raise_with_cause(self, cause: Exception):
        self.with_cause(cause)
        raise self


# 命名规范: 前五位-端口或业务ID  后四位-错误码

# 上下文错误
ContextException_NoSuchField = GoodException(10000, "上下文不存在对应的键值对")

# MySQL 03306 xxxx
MySQLException_Unknown = GoodException(33060000, "未知MySQL错误")
MySQLException_Select = GoodException(33060001, "查询数据失败")
MySQLException_Insert = GoodException(33060002, "插入数据失败")
MySQLException_Update = GoodException(33060003, "更新数据失败")
MySQLException_Delete = GoodException(33060004, "删除数据失败")
MySQLException_Connection = GoodException(33061000, "MySQL连接错误")

# Redis 06379 xxxx
RedisException_Unknown = GoodException(63790000, "未知Redis错误")
RedisException_Get = GoodException(63790001, "获取Redis数据失败")
RedisException_Set = GoodException(63790002, "设置Redis数据失败")
RedisException_Delete = GoodException(63790003, "删除Redis数据失败")

# RabbitMQ 05672 xxxx
RabbitMQException_Unknown = GoodException(56720000, "未知RabbitMQ错误")

# 三方Open API接口 90xxx
# DeepSeek 90000 xxxx
DeepSeekException_Unknown = GoodException(900000000, "未知DeepSeek错误")
DeepSeekException_Response_Format = GoodException(900000001, "DeepSeek返回格式错误")

# 尽量不要使用
Exception_Unknown = GoodException(-1, "未知错误")
