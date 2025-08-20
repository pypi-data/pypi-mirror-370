from serverless.service.plugins.generic import Generic


class PythonRequirements(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-python-requirements
    """

    yaml_tag = "!PythonRequirementsPlugin"

    def __init__(
        self,
        dockerizePip=True,
        usePoetry=True,
        useDownloadCache=True,
        useStaticCache=True,
        layer=True,
        dockerImage=None,
        pipCmdExtraArgs=None,
        dockerSsh=False,
    ):
        super().__init__("serverless-python-requirements")

        self.dockerImage = dockerImage
        self.dockerizePip = dockerizePip
        self.usePoetry = usePoetry
        self.useDownloadCache = useDownloadCache
        self.useStaticCache = useStaticCache
        self.layer = layer
        self.pipCmdExtraArgs = pipCmdExtraArgs or []
        self.dockerSsh = dockerSsh

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        if not self.dockerImage:
            export.pop("dockerImage", None)

        service.custom.pythonRequirements = export
