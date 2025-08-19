# coding:utf-8

from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import join
from typing import Optional

from xpw_keys.config import CertConfig
from xpw_keys.config import CustomCert
from xpw_keys.config import GeneralName
from xpw_keys.mkcert import CA
from xpw_keys.mkcert import MKCert
from xpw_keys.mkcert import RootCA


class Certificate:
    def __init__(self, custom: CustomCert, mkcert: MKCert):
        self.__custom: CustomCert = custom
        self.__mkcert: MKCert = mkcert

    def lookup(self, name: str) -> GeneralName:
        return self.__custom.lookup(name)

    def delete(self, name: str) -> bool:
        return self.__custom.delete(name)

    def read(self, auto_generate: bool = False) -> "CA":
        if len(general_names := [gn.name for gn in self.__custom]) <= 0:
            raise ValueError("No general name provided")

        if not exists(cert_file := self.__custom.cached_cert) and auto_generate:  # noqa:E501
            self.__mkcert.generate(*general_names).dump(cert_file)

        if (cert := CA.load(cert_file)).notAfterDays < self.__custom.validity and auto_generate:  # noqa:E501
            cert = self.__mkcert.generate(*general_names)
            cert.dump(cert_file, forced=True)

        return cert

    def save(self) -> bool:
        return self.__custom.dumpf() is None and isfile(self.__custom.config_file)  # noqa:E501


class Certificates:
    def __init__(self, base: Optional[str] = None):
        root: str = base or dirname(__file__)
        config_file: str = join(root, CertConfig.DEFAULT_CONFIG)
        self.__config: CertConfig = CertConfig.loadf(path=config_file)
        self.__mkcert: MKCert = MKCert(self.__config.cached_cert)

    @property
    def config(self) -> CertConfig:
        return self.__config

    @property
    def rootca(self) -> RootCA:
        return self.__mkcert.rootCA

    def lookup(self, name: str) -> Certificate:
        return Certificate(custom=self.config.lookup_cert(name), mkcert=self.__mkcert)  # noqa:E501

    def delete(self, name: str) -> bool:
        return self.config.delete_cert(name)


if __name__ == "__main__":
    certs = Certificates(".")
    certs.config.dumpf()
