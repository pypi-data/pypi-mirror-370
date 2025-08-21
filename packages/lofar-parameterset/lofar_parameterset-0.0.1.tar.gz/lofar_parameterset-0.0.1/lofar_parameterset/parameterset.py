#  Copyright (C) 2012 ASTRON (Netherlands Institute for Radio Astronomy)
#  SPDX-License-Identifier: GPL-3.0-or-later

"""Drop-in replacement for LCS/pyparameterset, which in turn wraps LCS/Common/src/ParameterSet.cc.

This replacement provides a narrow implementation. It writes compatible parsets, but cannot read
all the syntax variants supported by pyparameterset. Those variants are thus deprecated.

Not supported are:

* Vector expansion, f.e. foo=['bar'*4] and foo=[1..5],
* Most value interpretation, including booleans,
* Multi-line values,
* String escaping beyond either " or ' in the string,
* Modellng of ParameterValue as a separate class,
* Case-insensitivity,
* Tracking unused keys.

"""


class parameterset(dict):
    def __init__(self, content: dict = {}):
        self.update(content)

    def __str__(self):
        def encode(v):
            if isinstance(v, str):
                return f"'{v}'" if '"' in v else f'"{v}"'
            return str(v)

        return "\n".join(
            sorted([f"{key}={encode(value)}" for key, value in self.items()])
        )

    def add(self, key, value):
        self[key] = value

    def dict(self) -> dict:
        return self

    def isDefined(self, key) -> bool:
        return key in self

    def makeSubset(self, prefix: str):
        """
        Creates a Subset from the current ParameterSetImpl containing all the
        parameters that start with the given baseKey.
        The baseKey is cut off from the Keynames in the created subset, the
        optional prefix is put before the keynames.
        """
        return parameterset(
            {
                key[len(prefix) :]: value
                for key, value in self.items()
                if key.startswith(prefix)
            }
        )

    def fullModuleName(self, module: str):
        """
        Searches for a key ending in the given 'shortkey' and returns it full name.
        e.g: a.b.c.d.param=xxxx --> fullModuleName(d)      --> a.b.c.d
        e.g: a.b.c.d.param=xxxx --> fullModuleName(b.c)    --> a.b.c
        e.g: a.b.c.d.param=xxxx --> fullModuleName(d.param)-->
        """
        for key in self:
            if key == module:
                return key
            if key.startswith(f"{module}."):
                return module
            if key.endswith(f".{module}"):
                return key
            if (pos := key.find(f".{module}.")) >= 0:
                return key[: pos + len(module) + 1]

        return ""

    @staticmethod
    def fromString(parset: str):
        """
        Create a parameterset from a string of key=value pairs.
        """
        result = parameterset()
        result._importString(parset)
        return result

    def _importString(self, parset: str):
        lines = parset.split("\n")
        for line in lines:
            # strip comments
            if "#" in line:
                line, _ = line.split("#", 1)

            # ignore empty lines
            line = line.strip()
            if not line:
                continue

            # parse single-line key=value pairs
            assert "=" in line

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            self[key] = value

    def adoptArgv(self, argv: list[str]):
        """
        Add keys as provided on the command line in the form
        of "key=value".
        """
        for arg in argv:
            kv = arg.split("=", 1)
            if len(kv) == 2:
                self[kv[0]] = kv[1]

    def getString(self, key: str, default: str | None = None) -> str:
        """
        Return a value as string, with the given default if it is not
        found. If no default is provided either, a KeyError
        is thrown.
        """
        return self.get(key, default) if default is not None else self[key]

    def _getVector(self, key: str) -> list[str]:
        """
        Return the values of a vector, encoded as [a, b, c] or
        with the values quoted.
        """
        value = self[key]

        # value is "[element, element, element]"
        assert value[0] == "["
        assert value[-1] == "]"

        values = value[1:-1]
        elements = values.split(",")
        return [e.strip() for e in elements]

    def getIntVector(self, key: str, expandable: bool = True) -> list[int]:
        """
        Return a parset value as an integer list.

        expandable: deprecated, will be ignored.
        """
        return [int(x) for x in self._getVector(key)]

    def getDoubleVector(self, key: str, expandable: bool = True) -> list[float]:
        """
        Return a parset value as a float list.

        expandable: deprecated, will be ignored.
        """
        return [float(x) for x in self._getVector(key)]

    def getStringVector(self, key: str, expandable: bool = True) -> list[str]:
        """
        Return a parset value as a string list.

        expandable: deprecated, will be ignored.
        """

        def parse_str(s):
            if s[0] == '"' and s[-1] == '"':
                # strip double quotes
                return s[1:-1]
            elif s[0] == "'" and s[-1] == "'":
                # strip single quotes
                return s[1:-1]
            else:
                return s

        return [parse_str(x) for x in self._getVector(key)]
