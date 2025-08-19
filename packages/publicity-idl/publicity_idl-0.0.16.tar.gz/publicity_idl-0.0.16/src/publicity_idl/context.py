from .enum import SourceEnum, ContextField
from .domain import Batch, Keyword, Event, Record, User, PushConfig, SourceKeywordOffset, PushConfigKeyword
from .exception import ContextException_NoSuchField

class Context:
    def __init__(self, fields: dict = None):
        # fields为None的情况，使用空字典作为默认值，否则拷贝一份
        self.fields = fields.copy() if fields is not None else {}

    def _must_get(self, field: ContextField) -> any:
        if field not in self.fields:
            raise ContextException_NoSuchField
        return self.fields[field]

    def must_get_batch(self):
        return self._must_get(ContextField.Batch)

    def must_get_source(self):
        return self._must_get(ContextField.Source)

    def must_get_keyword(self):
        return self._must_get(ContextField.Keyword)

    def must_get_event(self):
        return self._must_get(ContextField.Event)

    def must_get_record(self):
        return self._must_get(ContextField.Record)

    def must_get_user(self):
        return self._must_get(ContextField.User)

    def must_get_push_config(self):
        return self._must_get(ContextField.PushConfig)

    def must_get_push_config_keyword(self):
        return self._must_get(ContextField.PushConfigKeyword)

    def must_get_source_keyword_offset(self):
        return self._must_get(ContextField.SourceKeywordOffset)

    # 返回一个新的Context对象, 包含新的key-value
    def _with(self, key: ContextField, value: any):
        new_fields = self.fields.copy()
        new_fields[key] = value
        return Context(new_fields)

    def with_source(self, source: SourceEnum):
        return self._with(key=ContextField.Source, value=source)

    def with_batch(self, batch: Batch):
        return self._with(key=ContextField.Batch, value=batch)

    def with_keyword(self, keyword: Keyword):
        return self._with(key=ContextField.Keyword, value=keyword)

    def with_event(self, event: Event):
        return self._with(key=ContextField.Event, value=event)

    def with_user(self, user: User):
        return self._with(key=ContextField.User, value=user)

    def with_record(self, record: Record):
        return self._with(key=ContextField.Record, value=record)

    def with_push_config(self, push_config: PushConfig):
        return self._with(key=ContextField.PushConfig, value=push_config)

    def with_push_config_keyword(self, push_config_keyword: PushConfigKeyword):
        return self._with(key=ContextField.PushConfigKeyword, value=push_config_keyword)

    def with_source_keyword_offset(self, source_keyword_offset: SourceKeywordOffset):
        return self._with(key=ContextField.SourceKeywordOffset, value=source_keyword_offset)

    def __str__(self) -> str:
        """自定义字符串表示，直观展示所有字段信息"""
        # 存储格式化后的字段信息
        field_strings = []

        for key, value in self.fields.items():
            field_strings.append(f"  {key}: {value}")

        # 使用",\n"作为连接符，实现逗号加换行的效果
        fields_str = ",\n".join(field_strings)
        return f"Context(fields: {{\n{fields_str}\n}})"
