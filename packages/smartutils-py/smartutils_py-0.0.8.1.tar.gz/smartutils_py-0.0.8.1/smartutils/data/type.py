import difflib
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar

__all__ = ["ZhEnumBase", "LowStr"]


T = TypeVar("T", bound="ZhEnumBase")


class ZhEnumBase(Enum):
    """
    支持变量-中文双向映射的通用枚举基类。
    子类不要在类体里写映射字典，需在类外写。
    """

    @property
    def zh(self) -> str:
        return self._obj_zh_map()[self]

    @classmethod
    def from_zh(cls: Type[T], zh: str) -> T:
        return cls._zh_obj_map()[zh]

    @classmethod
    def from_zh_fuzzy(cls: Type[T], zh_fuzzy: str, cutoff: float = 0.6) -> Optional[T]:
        """
        从中文模糊匹配到Enum类型对象。
        :param zh_fuzzy: 模糊中文字符串
        :param cutoff: 匹配相似度阈值，0.0-1.0之间，越高匹配越严格
        :return: 匹配到的Enum对象
        """
        zh_map = cls._zh_obj_map()
        matches = difflib.get_close_matches(zh_fuzzy, zh_map.keys(), n=1, cutoff=cutoff)
        if not matches:
            return None
        return zh_map[matches[0]]

    @classmethod
    def zh_from_value(cls: Type[T], value: Any) -> str:
        return cls(value).zh

    @classmethod
    def value_from_zh(cls: Type[T], zh: str) -> Any:
        return cls.from_zh(zh).value

    @classmethod
    def zh_choices(cls: Type[T]):
        return [(e, e.zh) for e in cls]

    @classmethod
    def zh_choices_str(cls) -> str:
        return " ".join(f"{item.value}: {item.zh}" for item in cls)

    @classmethod
    def zh_list(cls: Type[T]):
        return [e.zh for e in cls]

    @staticmethod
    def _obj_zh_map() -> Dict[Any, str]:
        raise NotImplementedError("子类必须实现 _obj_zh_map 方法")

    @staticmethod
    def _zh_obj_map() -> Dict[str, Any]:
        raise NotImplementedError("子类必须实现 _zh_obj_map 方法")


class LowStr(str):
    def __new__(cls, s: str):
        return str.__new__(cls, s.lower())


class SharedData:
    _data = {}

    @classmethod
    def set(cls, key, value):
        cls._data[key] = value

    @classmethod
    def get(cls, key, default=None) -> Any:
        return cls._data.get(key, default)

    @classmethod
    def get_or_set(cls, key, default) -> Any:
        value = cls.get(key)
        if value:
            return value

        if default:
            value = default

        if value:
            cls.set(key, value)

        return value
