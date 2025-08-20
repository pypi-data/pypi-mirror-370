import abc
import hashlib
import json
from abc import ABC

from serverless.aws.resources import Resource
from serverless.service.types import ResourceName, YamlOrderedDict


class PolicyBuilder(YamlOrderedDict):
    yaml_tag = "!IAM"

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.statements = []

    def append(self, policy):
        if len(list(filter(lambda x: x["Sid"] == policy["Sid"], self.statements))):
            return

        self.statements.append(policy)

    def allow(self, permissions, resources, sid=None):
        sid = sid or "Policy" + str(hashlib.sha224(json.dumps([permissions, resources]).encode("ascii")).hexdigest())
        self.append(dict(Sid=sid, Effect="Allow", Action=permissions, Resource=resources))

    def deny(self, permissions, resources, sid=None):
        sid = sid or "Policy" + str(hashlib.sha224(json.dumps([permissions, resources]).encode("ascii")).hexdigest())
        self.append(dict(Sid=sid, Effect="Deny", Action=permissions, Resource=resources))

    def apply(self, preset: "IAMPreset"):
        preset.apply(self)

    def allow_read(self, resource: Resource):
        resource.enable_read(self)

    def allow_write(self, resource: Resource):
        resource.enable_write(self)

    def allow_delete(self, resource: Resource):
        resource.enable_delete(self)

    @property
    def role_arn(self):
        return "arn:aws:iam::${aws:accountId}:role/" + self.role

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_list(data.statements)


class ServicePolicyBuilder(PolicyBuilder):
    yaml_tag = "!IAM"

    def __init__(self, service, name=None, **kwds):
        super().__init__(**kwds)
        self.service = service
        self.name = name or "${self:service}-${sls:stage}-${aws:region}-service"

    @property
    def role(self):
        return str(ResourceName(self.name, self.service))

    @classmethod
    def to_yaml(cls, dumper, data):
        export = dict(data.items())
        export.pop("service", None)
        export["name"] = data.role
        return dumper.represent_dict(dict(role=export))


class FunctionPolicyBuilder(PolicyBuilder):
    yaml_tag = "!IAM"

    def __init__(self, function_name, service, **kwds):
        super().__init__(**kwds)
        self.function_name = function_name
        self.service = service

    @property
    def role(self):
        name = str(self.function_name)
        name = name.replace("${sls:stage}", "${sls:stage}-${aws:region}")
        return str(ResourceName(f"{name}-lambda", self.service))


class IAMPreset(ABC):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    @abc.abstractmethod
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        pass
