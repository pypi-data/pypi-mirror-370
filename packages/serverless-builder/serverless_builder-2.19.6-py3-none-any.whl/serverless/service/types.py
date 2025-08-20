import abc
import hashlib
import re
from collections import OrderedDict

import inflection
import yaml


class YamlOrderedDict(OrderedDict, yaml.YAMLObject):
    yaml_tag = "!YamlOrderedDict"

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data)


class SmartString:
    def __init__(self, val, prefix="", suffix=""):
        self.val = val
        self.prefix = prefix
        self.suffix = suffix

    def __str__(self):
        if not self.val:
            return ""

        return f"{self.prefix}{self.val}{self.suffix}"

    def __call__(self, prefix="", suffix=""):
        return SmartString(self.val, prefix=prefix, suffix=suffix)


class Identifier(yaml.YAMLObject):
    yaml_tag = "Identifier"

    def __init__(self, identifier, safe=False):
        super().__init__()
        if safe:
            identifier = re.sub(r"\${.*?}-?", "", identifier)
            identifier = re.sub(r"\W", "-", identifier)

        self.identifier = identifier

    @property
    def camel(self):
        return inflection.camelize(inflection.underscore(self.identifier))

    @property
    def pascal(self):
        return inflection.camelize(inflection.underscore(self.identifier), uppercase_first_letter=True).replace("_", "")

    @property
    def snake(self):
        return inflection.underscore(self.identifier).lower()

    @property
    def spinal(self):
        return inflection.dasherize(inflection.underscore(self.identifier)).lower()

    @property
    def resource(self):
        identifier = re.sub(r"\${.*?}-?", "", self.identifier)
        identifier = re.sub(r"\W", "-", identifier)
        identifier = identifier.strip("-")
        return inflection.camelize(inflection.underscore(identifier), uppercase_first_letter=True)

    def __str__(self):
        return self.identifier

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_str(str(data.identifier))


class ResourceName:
    def __init__(self, name: str, service=None):
        self.name = name
        self.service = service

    def __str__(self):
        safe = self.name.replace("${aws:region}", "us-east-1")
        safe = safe.replace("${self:service}", (self.service.service.spinal if self.service else ""))
        safe = safe.replace("${sls:stage}", "staging")

        if len(safe) > 50:
            parts = []
            for part in self.name.split("-"):
                if "$" in part or part == "lambda":
                    parts.append(part)
                else:
                    parts.append(part[0:3])
            name = "-".join(parts)
        else:
            name = self.name

        name = name + "-" + hashlib.md5(safe.encode("utf-8")).hexdigest()[:5]

        return name


class ResourceId(ResourceName):
    def __str__(self):
        return Identifier(super().__str__()).pascal


class ProviderMetadata(type(YamlOrderedDict), type(abc.ABC)):
    pass


class Provider(YamlOrderedDict, abc.ABC, metaclass=ProviderMetadata):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)

    @abc.abstractmethod
    def configure(self, service):
        pass


class Feature(abc.ABC):
    @abc.abstractmethod
    def enable(self, service):
        pass

    def pre_render(self, service):
        pass


class Integration(abc.ABC):
    @abc.abstractmethod
    def enable(self, service):
        pass

    def pre_render(self, service):
        pass


class PluginMetadata(type(YamlOrderedDict), type(abc.ABC)):
    pass


class Plugin(YamlOrderedDict, abc.ABC, metaclass=PluginMetadata):
    @abc.abstractmethod
    def enable(self, service):
        pass
