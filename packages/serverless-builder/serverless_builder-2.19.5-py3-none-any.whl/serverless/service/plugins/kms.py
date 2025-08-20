from serverless.aws.resources.kms import EncryptableResource
from serverless.service.plugins.generic import Generic
from serverless.service.plugins.iam_roles import IAMRoles


class KMSGrant(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-kms-grants
    """

    def __init__(self, **kwds):
        super().__init__("serverless-kms-grants")

    def enable(self, service):
        super().enable(service)
        service.custom.kmsGrants = []

    def pre_render(self, service):
        if service.plugins.get(IAMRoles):
            for fn in service.functions.all():
                service.custom["kmsGrants"].append(
                    dict(
                        kmsKeyId=EncryptableResource.encryption_alias(),
                        roleName=fn.iam.role,
                    )
                )

        else:
            service.custom["kmsGrants"].append(
                dict(kmsKeyId=EncryptableResource.encryption_alias(), roleName=service.provider.iam.role)
            )
