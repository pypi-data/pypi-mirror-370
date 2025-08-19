import enum

class SourceEnum(enum.Enum):
    Douyin = "douyin"
    Toutiao = "toutiao"
    Weibo = "weibo"
    Wechat = "wechat"
    South_weekend = "south_weekend"

class ContextField(enum.Enum):
    Batch = "batch"
    Source = "source"
    Keyword = "keyword"
    Event = "event"
    Record = "record"
    User = "user"
    PushConfig = "push_config"
    PushConfigKeyword = "push_config_keyword"
    SourceKeywordOffset = "source_keyword_offset"
