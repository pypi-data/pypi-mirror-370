#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = [
    "DirNode", "MultipartResumeData", "P115Cookies", "P115DictAttrLikeMixin", 
    "P115DictAttrLike", "P115ID", "P115StrID", "P115URL", 
]

from functools import cached_property
from http.cookiejar import CookieJar
from re import compile as re_compile
from types import MappingProxyType
from typing import Any, Final, NamedTuple, NotRequired, Self, TypedDict

from cookietools import cookies_str_to_dict
from undefined import undefined


CRE_UID_FORMAT_match: Final = re_compile("(?P<user_id>[1-9][0-9]*)_(?P<login_ssoent>[A-Z][1-9][0-9]*)_(?P<login_timestamp>[1-9][0-9]{9,})").fullmatch
CRE_CID_FORMAT_match: Final = re_compile("[0-9a-f]{32}").fullmatch
CRE_SEID_FORMAT_match: Final = re_compile("[0-9a-f]{120}").fullmatch


class DirNode(NamedTuple):
    """用来保存某个 id 对应的 name 和 parent_id 的元组
    """
    name: str
    parent_id: int


class RequestKeywords(TypedDict):
    """一个请求函数，至少需要包括的参数
    """
    url: str
    method: str
    data: Any
    headers: Any
    parse: Any


class MultipartResumeData(TypedDict):
    """分块上传的所需参数的封装，便于中断后下次继续
    """
    bucket: str
    object: str
    token: NotRequired[dict]
    callback: dict
    upload_id: str
    partsize: int
    parts: NotRequired[list[dict]]
    filesize: NotRequired[int]


class P115Cookies(str):
    """cookies 的封装
    """
    def __getattr__(self, attr: str, /):
        try:
            return self.mapping[attr]
        except KeyError as e:
            raise AttributeError(attr) from e

    def __getitem__(self, key, /): # type: ignore
        if isinstance(key, str):
            return self.mapping[key]
        return super().__getitem__(key)

    def __repr__(self, /) -> str:
        cls = type(self)
        if (module := cls.__module__) == "__main__":
            name = cls.__qualname__
        else:
            name = f"{module}.{cls.__qualname__}"
        return f"{name}({str(self)!r})"

    def __setattr__(self, attr, value, /):
        raise TypeError("can't set attribute")

    @cached_property
    def mapping(self, /) -> MappingProxyType:
        return MappingProxyType(cookies_str_to_dict(str(self)))

    @cached_property
    def uid(self, /) -> str:
        return self.mapping["UID"]

    @cached_property
    def cid(self, /) -> str:
        return self.mapping["CID"]

    @cached_property
    def kid(self, /) -> str:
        return self.mapping["KID"]

    @cached_property
    def seid(self, /) -> str:
        return self.mapping["SEID"]

    @cached_property
    def user_id(self, /) -> int:
        d: dict = CRE_UID_FORMAT_match(self.uid).groupdict() # type: ignore
        self.__dict__.update(d)
        return d["user_id"]

    @cached_property
    def login_ssoent(self, /) -> int:
        d: dict = CRE_UID_FORMAT_match(self.uid).groupdict() # type: ignore
        self.__dict__.update(d)
        return d["login_ssoent"]

    @cached_property
    def login_timestamp(self, /) -> int:
        d: dict = CRE_UID_FORMAT_match(self.uid).groupdict() # type: ignore
        self.__dict__.update(d)
        return d["login_timestamp"]

    @cached_property
    def is_well_formed(self, /) -> bool:
        return (
            CRE_UID_FORMAT_match(self.uid) and 
            CRE_CID_FORMAT_match(self.cid) and 
            CRE_SEID_FORMAT_match(self.seid)
        ) is not None

    @cached_property
    def cookies(self, /) -> str:
        """115 登录的 cookies，包含 UID、CID、KID 和 SEID 这 4 个字段
        """
        cookies = f"UID={self.uid}; CID={self.cid}; SEID={self.seid}"
        if "KID" in self.mapping:
            cookies += f"; KID={self.mapping['KID']}"
        return cookies

    @classmethod
    def from_cookiejar(cls, cookiejar: CookieJar, /) -> Self:
        return cls("; ".join(
            f"{cookie.name}={cookie.value}" 
            for cookie in cookiejar 
            if cookie.domain == "115.com" or cookie.domain.endswith(".115.com")
        ))


class P115DictAttrLikeMixin:

    def __getattr__(self, attr: str, /):
        try:
            return self.__dict__[attr]
        except KeyError as e:
            raise AttributeError(attr) from e

    def __delitem__(self, key: str, /):
        del self.__dict__[key]

    def __getitem__(self, key, /):
        try:
            if isinstance(key, str):
                return self.__dict__[key]
        except KeyError:
            return super().__getitem__(key) # type: ignore

    def __setitem__(self, key: str, val, /):
        self.__dict__[key] = val

    def __repr__(self, /) -> str:
        cls = type(self)
        if (module := cls.__module__) == "__main__":
            name = cls.__qualname__
        else:
            name = f"{module}.{cls.__qualname__}"
        return f"{name}({super().__repr__()}, {self.__dict__!r})"

    @property
    def mapping(self, /) -> dict[str, Any]:
        return self.__dict__

    def get(self, key, /, default=None):
        return self.__dict__.get(key, default)

    def items(self, /):
        return self.__dict__.items()

    def keys(self, /):
        return self.__dict__.keys()

    def values(self, /):
        return self.__dict__.values()


class P115DictAttrLike(P115DictAttrLikeMixin):

    def __new__(cls, val: Any = undefined, /, *args, **kwds):
        if val is undefined:
            return super().__new__(cls)
        else:
            return super().__new__(cls, val) # type: ignore

    def __init__(self, val: Any = undefined, /, *args, **kwds):
        self.__dict__.update(*args, **kwds)

    @classmethod
    def of(cls, val: Any = undefined, /, ns: None | dict = None) -> Self:
        if val is undefined:
            self = cls.__new__(cls)
        else:
            self = cls.__new__(cls, val)
        if ns is not None:
            self.__dict__ = ns
        return self

    @classmethod
    def derive(cls, base: type, name: str = "", /, **ns) -> type[Self]:
        return type(name, (cls, base), ns)

    @classmethod
    def derive_backend(cls, base: type, name: str = "", /, **ns) -> type[Self]:
        return type(name, (base, cls), ns)


class P115ID(P115DictAttrLike, int):
    """整数 id 的封装
    """
    def __str__(self, /) -> str:
        return int.__repr__(self)


class P115StrID(P115DictAttrLike, str):
    """字符串 id 的封装
    """


class P115URL(P115DictAttrLike, str):
    """下载链接的封装
    """
    def geturl(self, /) -> str:
        return str(self)

    url = property(geturl)

