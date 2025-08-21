# coding:utf-8

from os import remove
from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import join
from typing import List
from typing import Optional


class CA():
    def __init__(self, cert_file: str, key_file: str):
        with open(cert_file, "r", encoding="utf-8") as rhdl:
            self.__crt: str = rhdl.read().strip()
        with open(key_file, "r", encoding="utf-8") as rhdl:
            self.__key: str = rhdl.read().strip()
        self.__x509 = None

    def __str__(self) -> str:
        return f"{__class__.__name__}(expire after {self.notAfterDays} days)"

    @property
    def crt(self) -> str:
        return self.__crt

    @property
    def key(self) -> str:
        return self.__key

    @property
    def pem(self) -> str:
        return f"{self.crt}\n{self.key}"

    @property
    def x509(self):
        if not self.__x509:
            from cryptography import x509  # pylint:disable=C0415
            self.__x509 = x509.load_pem_x509_certificate(self.crt.encode("utf-8"))  # noqa:E501
        return self.__x509

    @property
    def notAfterDays(self) -> int:
        from datetime import datetime  # pylint:disable=C0415
        return (self.x509.not_valid_after - datetime.now()).days - 1

    @property
    def subjectAltName(self):
        from cryptography.x509.extensions import \
            SubjectAlternativeName  # pylint:disable=C0415
        return self.x509.extensions.get_extension_for_class(SubjectAlternativeName).value  # noqa:E501

    @property
    def general_names(self) -> List[str]:
        return [str(name.value) for name in self.subjectAltName]

    def dump(self, path: str, forced: bool = False) -> bool:
        from os.path import abspath  # pylint:disable=C0415
        path = abspath(path)

        from os import makedirs  # pylint:disable=import-outside-toplevel
        makedirs(dirname(path), mode=0o700, exist_ok=True)

        if exists(path):
            if not forced:
                raise FileExistsError(f"cert '{path}' already exists")
            remove(path)

        from tempfile import TemporaryDirectory  # pylint:disable=C0415
        with TemporaryDirectory() as tmpdir:
            with open(cert_file := join(tmpdir, "crt.pem"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{self.crt}\n")

            with open(key_file := join(tmpdir, "key.pem"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{self.key}\n")

            from os import chmod  # pylint:disable=import-outside-toplevel
            chmod(cert_file, 0o400)
            chmod(key_file, 0o400)

            if exists(temp := f"{path}.tmp"):
                remove(temp)  # pragma: no cover

            import tarfile  # pylint:disable=import-outside-toplevel
            with tarfile.open(temp, "w") as thdl:
                thdl.add(cert_file, arcname="crt.pem")
                thdl.add(key_file, arcname="key.pem")

            from os import rename  # pylint:disable=import-outside-toplevel
            rename(temp, path)

        return isfile(path)

    @classmethod
    def load(cls, path: str) -> "CA":
        if not exists(path) or not isfile(path):
            raise FileNotFoundError(f"cert '{path}' not exists")

        from tempfile import TemporaryDirectory  # pylint:disable=C0415
        with TemporaryDirectory() as tmpdir:
            import tarfile  # pylint:disable=import-outside-toplevel
            with tarfile.open(path, "r") as thdl:
                thdl.extract("crt.pem", path=tmpdir)
                thdl.extract("key.pem", path=tmpdir)
            return cls(cert_file=join(tmpdir, "crt.pem"), key_file=join(tmpdir, "key.pem"))  # noqa:E501


class RootCA(CA):
    def __init__(self, root: str):
        cert_file: str = join(root, "rootCA.pem")
        key_file: str = join(root, "rootCA-key.pem")
        super().__init__(cert_file=cert_file, key_file=key_file)
        self.__cert_file: str = cert_file
        self.__key_file: str = key_file

    @property
    def crt_file(self) -> str:
        return self.__cert_file

    @property
    def key_file(self) -> str:
        return self.__key_file


class MKCert():
    def __init__(self, base: Optional[str] = None):
        self.__base: str = base or dirname(__file__)
        self.__root: Optional[RootCA] = None

        from os import makedirs  # pylint:disable=import-outside-toplevel
        makedirs(self.__base, mode=0o700, exist_ok=True)

    @property
    def which(self) -> str:
        if not exists(path := join(self.__base, "mkcert")):
            try:
                self.download(file=path)
            except Exception:  # pylint:disable=broad-exception-caught
                if exists(path):
                    remove(path)

        if not exists(path) or not isfile(path):
            raise FileNotFoundError("mkcert not found")
        return path

    @property
    def rootCA(self) -> RootCA:
        if not self.__root:
            from os import makedirs  # pylint:disable=import-outside-toplevel
            from os import popen  # pylint:disable=import-outside-toplevel
            from os import system  # pylint:disable=import-outside-toplevel

            if not exists(caroot := popen(f"{self.which} -CAROOT").read().strip()):  # noqa:E501
                makedirs(caroot)  # pragma: no cover

            try:
                root: RootCA = RootCA(caroot)
            except FileNotFoundError:
                system(f"{self.which} -install")
                root: RootCA = RootCA(caroot)

            self.__root = root
        return self.__root

    def reset(self) -> bool:
        self.__root = None

        if isfile(crt_file := self.rootCA.crt_file):
            remove(crt_file)

        if isfile(key_file := self.rootCA.key_file):
            remove(key_file)

        self.__root = None
        return not exists(crt_file) and not exists(key_file)

    def generate(self, *names: str) -> CA:
        from os import system  # pylint:disable=import-outside-toplevel
        from tempfile import TemporaryDirectory  # pylint:disable=C0415

        with TemporaryDirectory() as temp:
            cert_file: str = join(temp, "crt.pem")
            key_file: str = join(temp, "key.pem")
            system(f"{self.which} -cert-file {cert_file} -key-file {key_file} {' '.join(names)}")  # noqa:E501
            return CA(cert_file=cert_file, key_file=key_file)

    @classmethod
    def download(cls, file: str) -> None:
        import platform  # pylint:disable=import-outside-toplevel

        os_name: str = platform.system()
        machine: str = platform.machine()

        if machine == "x86_64":  # pragma: no cover
            machine = "amd64"  # pragma: no cover
        elif machine == "aarch64":  # pragma: no cover
            machine = "arm64"  # pragma: no cover

        if os_name == "Linux":
            from urllib.request import urlretrieve  # pylint:disable=C0415

            from xkits_logger import Logger  # pylint:disable=C0415

            url = f"https://dl.filippo.io/mkcert/latest?for=linux/{machine}"
            Logger.stderr_green(f"Download mkcert from '{url}' to '{file}'")
            urlretrieve(url, file)

        if exists(file) and isfile(file):
            from os import chmod  # pylint:disable=import-outside-toplevel

            chmod(file, 0o0550)


if __name__ == "__main__":
    print((mkcert := MKCert()).rootCA)
    print(cert := mkcert.generate("example.com", "localhost", "127.0.0.1"))
    print(cert.dump("certificate.tar"))
    print(cert.general_names)
    print(mkcert.reset())
