import json
from typing import List, overload, Any, Union


class DotDict:
    __slots__ = ("_data",)

    def __init__(self, data=None):
        """
        初始化 DotDict 对象

        Args:
            data (dict): 初始数据
        """
        object.__setattr__(self, "_data", {})
        if isinstance(data, dict):
            for k, v in data.items():
                self._data[k] = self._wrap(v)

    @overload
    def _wrap(self, v: dict) -> 'DotDict': ...

    @overload
    def _wrap(self, v: list) -> List['DotDict']: ...

    @overload
    def _wrap(self, v: Any) -> Any: ...

    def _wrap(self, v) -> Union['DotDict', List['DotDict'], Any]:
        """
        包装值

        Args:
            v (Any): 值

        Returns:
            Any: 包装后的值
        """
        if isinstance(v, dict):
            return DotDict(v)
        if isinstance(v, list):
            return [self._wrap(i) for i in v]
        return v

    def __getattr__(self, name):
        """
        自动“生长”层级：访问不存在的键时创建子节点

        Args:
            name (str): 属性名

        Returns:
            DotDict: 子节点
        """
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._data:
            self._data[name] = DotDict()
        return self._data[name]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = self._wrap(value)

    def __delattr__(self, name):
        del self._data[name]

    def __getitem__(self, key):
        """ 
        兼容 dict 行为

        Args:
            key (str): 键

        Returns:
            DotDict: 子节点
        """
        return self._data[key]

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def to_dict(self):
        """
        将 DotDict 转换为 dict 对象

        Returns:
            dict: 转换后的 dict 对象
        """
        def unwrap(v):
            if isinstance(v, DotDict):
                return v.to_dict()
            if isinstance(v, list):
                return [unwrap(i) for i in v]
            return v
        return {k: unwrap(v) for k, v in self._data.items()}

    def __str__(self):
        """
        将 DotDict 转换为字符串

        Returns:
            str: 转换后的字符串
        """
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def __repr__(self):
        """
        将 DotDict 转换为字符串

        Returns:
            str: 转换后的字符串
        """
        return f"DotDict({self.to_dict()})"
