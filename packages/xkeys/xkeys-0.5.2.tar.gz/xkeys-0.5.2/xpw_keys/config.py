# coding:utf-8

from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import join
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple


class GeneralName:
    def __init__(self, domain_or_address: str, subdomains: bool = False, getaddress: bool = False):  # noqa:E501
        name, is_domain = self.format(domain_or_address)
        self.__subdomains: bool = is_domain and subdomains
        self.__getaddress: bool = is_domain and getaddress
        self.__is_domain: bool = is_domain
        self.__name: str = name

    def __str__(self) -> str:
        return f"{__class__.__name__}({self.name})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_domain(self) -> bool:
        return self.__is_domain

    @property
    def subdomains(self) -> bool:
        return self.__subdomains

    @subdomains.setter
    def subdomains(self, value: bool) -> None:
        self.__subdomains = self.is_domain and value

    @property
    def getaddress(self) -> bool:
        return self.__getaddress

    @getaddress.setter
    def getaddress(self, value: bool) -> None:
        self.__getaddress = self.is_domain and value

    @property
    def options(self) -> Dict[str, Any]:
        options: Dict[str, Any] = {"generalname": self.name}
        if self.subdomains:
            options["subdomains"] = True
        if self.getaddress:
            options["getaddress"] = True
        return options

    @property
    def values(self) -> List[str]:
        values: List[str] = [self.name]
        if self.subdomains:
            values.append(f"*.{self.name}")
        if self.getaddress:
            values.append(self.resolve(self.name))
        return values

    @classmethod
    def format(cls, domain_or_address: str) -> Tuple[str, bool]:
        try:
            from ipaddress import ip_address  # pylint: disable=C0415
            return str(ip_address(domain_or_address)), False
        except ValueError:
            return domain_or_address, True

    @classmethod
    def resolve(cls, domain_name: str) -> str:
        """resolve domain name"""
        from socket import gethostbyname  # pylint: disable=C0415
        return gethostbyname(domain_name)

    @classmethod
    def load(cls, options: Dict[str, Any]):
        subdomains: bool = options.get("subdomains", False)
        getaddress: bool = options.get("getaddress", False)
        return cls(options["generalname"], subdomains, getaddress)


class CustomCert:
    ALTNAME: str = "SubjectAlternativeName"
    VALIDITY: str = "MinimumValidityDays"

    def __init__(self, cached_cert: str, config_file: str, config_data: Dict[str, Any]):  # noqa:E501
        items: List[GeneralName] = [GeneralName.load(i) for i in config_data.get(self.ALTNAME, [])]   # noqa:E501
        self.__names: Dict[str, GeneralName] = {gn.name: gn for gn in items}
        self.__validity: int = max(30, config_data.get(self.VALIDITY, 90))
        self.__config_file: str = abspath(config_file)
        self.__cached_cert: str = abspath(cached_cert)

    def __iter__(self) -> Iterator[GeneralName]:
        return iter(self.__names.values())

    def __len__(self) -> int:
        return len(self.__names)

    def __delitem__(self, name: str):
        self.delete(name)

    def __getitem__(self, name: str) -> GeneralName:
        return self.lookup(name)

    def __contains__(self, name: str) -> bool:
        return name in self.__names

    @property
    def cached_cert(self) -> str:
        return self.__cached_cert

    @property
    def config_file(self) -> str:
        return self.__config_file

    @property
    def validity(self) -> int:
        return self.__validity

    @validity.setter
    def validity(self, value: int):
        self.__validity = max(30, value)

    def lookup(self, name: str) -> GeneralName:
        if name not in self.__names:
            self.__names.setdefault(name, GeneralName(name))
        return self.__names[name]

    def delete(self, name: str) -> bool:
        if name in self.__names:
            del self.__names[name]
        return name not in self.__names

    def dumps(self) -> str:
        from toml import dumps  # pylint: disable=import-outside-toplevel
        return dumps({
            self.ALTNAME: [gn.options for gn in self.__names.values()],
            self.VALIDITY: self.validity,
        })

    def dumpf(self, config_file: Optional[str] = None) -> None:
        from xkits_file import SafeWrite  # pylint: disable=C0415
        with SafeWrite(config_file or self.config_file, encoding="utf-8", truncate=True) as whdl:  # noqa:E501
            whdl.write(self.dumps())

    @classmethod
    def loadf(cls, cert: str, conf: str, name: str) -> "CustomCert":
        cached_cert: str = cls.get_cached_cert(cert, name)

        if not exists(config_file := cls.get_config_file(conf, name)):
            return cls(cached_cert=cached_cert, config_file=config_file,
                       config_data={})

        from toml import loads  # pylint: disable=import-outside-toplevel
        from xkits_file import SafeRead  # pylint: disable=C0415

        with SafeRead(config_file, encoding="utf-8") as rhdl:
            return cls(cached_cert=cached_cert, config_file=config_file,
                       config_data=loads(rhdl.read()))

    @classmethod
    def get_cached_cert(cls, folder: str, name: str) -> str:
        return join(folder, f"{name}.tar")

    @classmethod
    def get_config_file(cls, folder: str, name: str) -> str:
        return join(folder, f"{name}.toml")


class CertConfig:
    DEFAULT_CONFIG: str = "certificates.toml"
    CACHED_CERT: str = "cached_cert"
    CUSTOM_CERT: str = "custom_cert"
    GLOBAL_NAME: str = "globals"

    def __init__(self, path: str, data: Dict[str, Any]):
        base: str = abspath(path)
        cached_cert: str = data.get(self.CACHED_CERT, join(dirname(base), "cached"))  # noqa:E501
        custom_cert: str = data.get(self.CUSTOM_CERT, join(dirname(base), "custom"))  # noqa:E501
        global_name: List = data.get(self.GLOBAL_NAME, [])
        makedirs(custom_cert, mode=0o740, exist_ok=True)

        self.__global_name: List[str] = global_name
        self.__custom_cert: str = custom_cert
        self.__cached_cert: str = cached_cert
        self.__base: str = base

    def __iter__(self) -> Iterator[str]:
        from os import listdir  # pylint: disable=import-outside-toplevel
        for item in listdir(self.custom_cert):
            if item.endswith(".toml") and isfile(CustomCert.get_config_file(self.custom_cert, name := item[:-5])):  # noqa:E501
                yield name

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __delitem__(self, name: str):
        self.delete_cert(name)

    def __getitem__(self, name: str) -> CustomCert:
        return self.lookup_cert(name)

    def __contains__(self, name: str) -> bool:
        return exists(CustomCert.get_config_file(self.custom_cert, name))

    @property
    def base(self) -> str:
        return self.__base

    @property
    def global_name(self) -> List[str]:
        return self.__global_name

    @property
    def custom_cert(self) -> str:
        return self.__custom_cert

    @property
    def cached_cert(self) -> str:
        return self.__cached_cert

    def lookup_cert(self, name: str) -> CustomCert:
        return CustomCert.loadf(cert=self.cached_cert, conf=self.custom_cert, name=name)  # noqa:E501

    def delete_cert(self, name: str) -> bool:
        from os import remove  # pylint: disable=import-outside-toplevel
        if isfile(cached_cert := CustomCert.get_cached_cert(self.cached_cert, name)):  # noqa:E501
            remove(cached_cert)
        if isfile(config_file := CustomCert.get_config_file(self.custom_cert, name)):  # noqa:E501
            remove(config_file)
        return not exists(cached_cert) and not exists(config_file)

    def dumps(self) -> str:
        from toml import dumps  # pylint: disable=import-outside-toplevel
        return dumps({self.CACHED_CERT: self.cached_cert,
                      self.CUSTOM_CERT: self.custom_cert,
                      self.GLOBAL_NAME: self.global_name})

    def dumpf(self, path: Optional[str] = None) -> None:
        from xkits_file import SafeWrite  # pylint: disable=C0415
        with SafeWrite(path or self.base, encoding="utf-8", truncate=True) as whdl:  # noqa:E501
            whdl.write(self.dumps())

    @classmethod
    def loadf(cls, path: str = DEFAULT_CONFIG) -> "CertConfig":
        if not exists(path):
            return cls(path=path, data={})

        from toml import loads  # pylint: disable=import-outside-toplevel
        from xkits_file import SafeRead  # pylint: disable=C0415

        with SafeRead(path, encoding="utf-8") as rhdl:
            return cls(path=path, data=loads(rhdl.read()))


if __name__ == "__main__":
    print(GeneralName.resolve("localhost"))
    print(GeneralName.resolve("127.0.0.1"))
    CertConfig.loadf().dumpf()
