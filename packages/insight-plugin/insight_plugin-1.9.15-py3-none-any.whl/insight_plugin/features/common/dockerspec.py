import yaml
from jinja2 import Environment, FileSystemLoader


class Dockerspec(object):
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        plugin_name: str,
        vendor: str,
        sdk_version: int,
        sdk_type: str,
        packages: [str],
        custom_cmd: [str],
        user: str,
    ):
        self.plugin_name = plugin_name
        self.vendor = vendor
        self.sdk_version = sdk_version
        self.sdk_type = sdk_type
        self.packages = packages
        self.custom_cmd = custom_cmd
        self.user = user

    def __eq__(self, other):
        return (
            self.plugin_name == other.plugin_name
            and self.vendor == other.vendor
            and self.sdk_version == other.sdk_version
            and self.sdk_type == other.sdk_type
            and self.packages == other.packages
            and self.custom_cmd == other.custom_cmd
            and self.user == other.user
        )

    @classmethod
    def from_dockerspec_file(
        cls, plugin_name: str, vendor: str = "rapid7", path: str = "dockerspec.yaml"
    ):
        """
        Instantiate a Dockerspec object from a dockerspec.yaml file
        :param plugin_name: Plugin name
        :param vendor: Vendor (default rapid7)
        :param path: Path to the dockerspec.yaml file
        :return: Dockerspec object
        """
        with open(path, encoding="utf-8") as f:
            dockerspec = yaml.safe_load(f)
            sdk_version = dockerspec["sdk_version"]
            sdk_type = dockerspec["sdk_type"]
            packages = dockerspec["packages"]
            custom_cmd = dockerspec["custom_cmd"]
            user = dockerspec["user"]

            return cls(
                plugin_name=plugin_name,
                vendor=vendor,
                sdk_version=sdk_version,
                sdk_type=sdk_type,
                packages=packages,
                custom_cmd=custom_cmd,
                user=user,
            )

    def generate_raw_dockerfile(self) -> str:
        """
        Generate a raw Dockerfile, as a string
        :return: Dockerfile string
        """

        env = Environment(
            loader=FileSystemLoader("../../templates/v1/"), autoescape=True
        )
        template = env.get_template("Dockerfile.jinja")

        return template.render(
            version=self.sdk_version,
            vendor="rapid7",
            sdk_type=self.sdk_type,
            packages=self.packages,
            custom_cmd=self.custom_cmd,
        )
