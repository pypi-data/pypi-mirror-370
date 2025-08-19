# coding:utf-8

from os import chmod
from os import listdir
from os import makedirs
from os import popen
from os import remove
from os import rename
from os import system
from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import join
import tarfile
from tempfile import TemporaryDirectory
from typing import Iterator
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from uuid import uuid4

from xkits_lib import CachePool

from xpw_keys.attribute import __project__

SSHKeyType = Literal[
    "rsa",
    "dsa",
    "ecdsa",
    "ecdsa-sk",
    "ed25519",
    "ed25519-sk",
]

SSHAttrType = Tuple[int, str, str, SSHKeyType]


class SSHKeyPair:
    def __init__(self, private: str, public: Optional[str] = None,
                 attributes: Optional[SSHAttrType] = None):
        self.__attributes: Optional[SSHAttrType] = attributes
        self.__public: Optional[str] = public.strip() if public else None
        self.__attributes_is_valid: Optional[bool] = None
        self.__public_is_valid: Optional[bool] = None
        self.__private: str = private.strip()

    def __bool__(self) -> bool:
        return self.public_is_valid and self.attributes_is_valid

    def __repr__(self) -> str:
        return f"{__class__.__name__} attributes={self.attributes}"

    def __str__(self) -> str:
        return self.fingerprint

    @property
    def bits(self) -> int:
        """Key length of the SSH key pair"""
        return self.attributes[0]

    @property
    def type(self) -> SSHKeyType:
        """Algorithm of the SSH key pair"""
        return self.attributes[3]

    @property
    def fingerprint(self) -> str:
        """Fingerprint of the SSH key pair"""
        return self.attributes[1]

    @property
    def comment(self) -> str:
        """Comment of the SSH key pair"""
        return self.attributes[2]

    @property
    def attributes(self) -> SSHAttrType:
        """The contents of one or more certificate

        Tuple[bits, fingerprint, comment, type]
        """
        if self.__attributes is None:  # lazy loading
            self.__attributes = self.extract(self.public)
            self.__attributes_is_valid = True
        return self.__attributes

    @property
    def public(self) -> str:
        """Public key"""
        if self.__public is None:  # lazy loading
            self.__public = self.parser(self.private)
            self.__public_is_valid = True
        return self.__public

    @property
    def private(self) -> str:
        """Private key"""
        return self.__private

    @property
    def attributes_is_valid(self) -> bool:
        if self.__attributes_is_valid is None:  # lazy checking
            is_valid: bool = self.extract(self.public) == self.attributes
            self.__attributes_is_valid = is_valid
        return self.__attributes_is_valid

    @property
    def public_is_valid(self) -> bool:
        if self.__public_is_valid is None:  # lazy checking
            is_valid: bool = self.parser(self.private) == self.public
            self.__public_is_valid = is_valid
        return self.__public_is_valid

    @classmethod
    def generate(cls,  # pylint: disable=R0913,R0917
                 bits: int = 4096,
                 type: SSHKeyType = "rsa",  # pylint: disable=redefined-builtin
                 comment: Optional[str] = None,
                 passphrase: Optional[str] = None
                 ) -> "SSHKeyPair":
        """Generate SSH key pair"""
        with TemporaryDirectory() as tmpdir:
            if not comment:
                comment = f"{__project__}-generate"

            if not passphrase:
                passphrase = "\"\""

            keyfile: str = join(tmpdir, __project__)
            if system(f"ssh-keygen -b {bits} -t {type} -f {keyfile} -C {comment} -N {passphrase}") != 0:  # noqa:E501
                raise RuntimeError("failed to generate SSH key pair")  # noqa:E501, pragma: no cover

            return cls.read(keyfile)

    @classmethod
    def extract(cls, public: str) -> SSHAttrType:
        """Extract attributes from public key"""
        with TemporaryDirectory() as tmpdir:
            with open(path := join(tmpdir, "public"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{public.strip()}\n")

            with popen(f"ssh-keygen -l -f {path}") as phdl:
                output: List[str] = phdl.read().split()
                if len(output) != 4:
                    raise ValueError(f"invalid public key: '{public}'")  # noqa:E501, pragma: no cover
                bits: int = int(output[0])
                fingerprint: str = output[1].strip()
                comment: str = output[2].strip()
                keytype: str = output[3].strip().lstrip("(").rstrip(")").lower()  # noqa:E501

                from typing import cast  # pylint: disable=C0415
                from typing import get_args  # pylint: disable=C0415
                if keytype not in get_args(SSHKeyType):
                    raise ValueError(f"unsupported SSH key type: {keytype}")  # noqa:E501, pragma: no cover
                return bits, fingerprint, comment, cast(SSHKeyType, keytype)

    @classmethod
    def parser(cls, private: str) -> str:
        """Parse public key from private key"""
        with TemporaryDirectory() as tmpdir:
            with open(path := join(tmpdir, "private"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{private.strip()}\n")

            chmod(path, 0o600)  # bad permissions

            with popen(f"ssh-keygen -y -f {path}") as phdl:
                public: str = phdl.read().strip()
                assert isinstance(public, str)
                return public

    def dump(self, name: str) -> None:
        """Dump SSH key pair to a file"""
        if not exists(base := dirname(name)):
            makedirs(base, mode=0o700)

        if exists(name):
            raise FileExistsError(f"SSH key pair '{name}' already exists")

        with TemporaryDirectory() as tmpdir:
            with open(attribute := join(tmpdir, "attributes"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{self.fingerprint}\n")
                whdl.write(f"{self.comment}\n")
                whdl.write(f"{self.type}\n")
                whdl.write(f"{self.bits}\n")

            with open(private := join(tmpdir, "private"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{self.private}\n")

            with open(public := join(tmpdir, "public"), "w", encoding="utf-8") as whdl:  # noqa:E501
                whdl.write(f"{self.public}\n")

            chmod(attribute, 0o644)
            chmod(private, 0o600)
            chmod(public, 0o644)

            if exists(temp := f"{name}.tmp"):
                remove(name)  # pragma: no cover

            with tarfile.open(temp, "w") as thdl:
                thdl.add(attribute, arcname="attributes.txt")
                thdl.add(public, arcname="key.pub")
                thdl.add(private, arcname="key")

            rename(temp, name)
            assert not exists(temp)
            assert isfile(name)

    @classmethod
    def load(cls, name: str) -> "SSHKeyPair":
        """Load SSH key pair from file"""
        if not exists(name) or not isfile(name):
            raise FileNotFoundError(f"sshkey '{name}' not exists")

        with TemporaryDirectory() as tmpdir:
            with tarfile.open(name, "r") as thdl:
                thdl.extract("attributes.txt", path=tmpdir)
                thdl.extract("key.pub", path=tmpdir)
                thdl.extract("key", path=tmpdir)

            with open(join(tmpdir, "attributes.txt"), encoding="utf-8") as rhdl:  # noqa:E501
                fingerprint = rhdl.readline().strip()
                comment = rhdl.readline().strip()
                keytype = rhdl.readline().strip()
                bits = int(rhdl.readline().strip())

            with open(join(tmpdir, "key.pub"), encoding="utf-8") as rhdl:
                public = rhdl.read()

            with open(join(tmpdir, "key"), encoding="utf-8") as rhdl:
                private = rhdl.read()

            from typing import cast  # pylint: disable=import-outside-toplevel
            from typing import get_args  # pylint: disable=C0415
            if keytype not in get_args(SSHKeyType):
                raise ValueError(f"unsupported SSH key type: {keytype}")  # noqa:E501, pragma: no cover
            attributes: SSHAttrType = (bits, fingerprint, comment, cast(SSHKeyType, keytype))  # noqa:E501
            return cls(private=private, public=public, attributes=attributes)

    @classmethod
    def read(cls, keyfile: str) -> "SSHKeyPair":
        """Read SSH private key (and public key, if it exists)"""
        public: Optional[str] = None
        private: str

        if not exists(keyfile) or not isfile(keyfile):
            raise FileNotFoundError(f"private key file '{keyfile}' not exists")  # noqa:E501, pragma: no cover

        with open(keyfile, encoding="utf-8") as rhdl:
            private = rhdl.read()

        if exists(pubfile := f"{keyfile}.pub") and isfile(pubfile):
            with open(pubfile, encoding="utf-8") as rhdl:
                public = rhdl.read()

        return SSHKeyPair(private, public)


class SSHKeyRing():
    def __init__(self, base: Optional[str] = None):
        self.__cache: CachePool[str, SSHKeyPair] = CachePool(lifetime=0)
        self.__base: str = base or "."

    @property
    def base(self) -> str:
        return self.__base

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __iter__(self) -> Iterator[str]:
        for item in listdir(self.base):
            if item.endswith(".tar") and isfile(self.join(name := item[:-4])):
                yield name

    def __contains__(self, name: str) -> bool:
        return name in self.__cache or isfile(self.join(name))

    def __getitem__(self, name: str) -> SSHKeyPair:
        if name not in self.__cache:
            self.__cache.put(name, self.load(name))
        return self.__cache.get(name)

    def __delitem__(self, name: str):
        self.remove(name)

    def join(self, name: str) -> str:
        return join(self.base, f"{name}.tar")

    def dump(self, name: str, pair: SSHKeyPair) -> SSHKeyPair:
        pair.dump(self.join(name))
        self.__cache.put(name, pair)
        return self.__cache.get(name)

    def load(self, name: str) -> SSHKeyPair:
        return SSHKeyPair.load(self.join(name))

    def remove(self, name: str) -> bool:
        self.__cache.delete(name)
        if exists(path := self.join(name)) and isfile(path):
            remove(path)
        return not exists(path)

    def rename(self, origin: str, target: str) -> bool:
        self.__cache.delete(origin)

        if not isfile(src := self.join(origin)) or exists(dst := self.join(target)):  # noqa:E501
            return False  # pragma: no cover

        rename(src=src, dst=dst)
        return not exists(src) and isfile(dst)

    def update(self, name: str, private: str) -> None:
        if not self.rename(origin=name, target=(backup := f"{name}.old")):
            raise ValueError(f"failed to create '{name}' backup")  # noqa:E501, pragma: no cover

        self.create(private=private, name=name)

        if not self.remove(name=backup):
            raise ValueError(f"failed to delete '{name}' backup")  # noqa:E501, pragma: no cover

    def create(self, private: str, name: Optional[str] = None) -> str:
        if not (value := SSHKeyPair(private=private)):
            raise ValueError("invalid private key")  # pragma: no cover

        index: str = name or value.comment or str(uuid4())
        self.dump(name=index, pair=value)
        return index

    def generate(self,  # pylint: disable=R0913,R0917
                 bits: int = 4096,
                 type: SSHKeyType = "rsa",  # pylint: disable=redefined-builtin
                 name: Optional[str] = None,
                 comment: Optional[str] = None,
                 passphrase: Optional[str] = None
                 ) -> str:
        value = SSHKeyPair.generate(bits=bits, type=type, comment=comment, passphrase=passphrase)  # noqa:E501
        index = name or comment or str(uuid4())
        self.dump(name=index, pair=value)
        return index


if __name__ == "__main__":
    SSHKeyPair.generate().dump(file := join("test", "example.tar"))
    key = SSHKeyPair.load(file)
    print(f"private key: {key.private}")
    print(f"public key: {key.public}")
    print(f"{key} valid: {bool(key)}")
