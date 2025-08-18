import argparse
import os
from gitlab import Packages, __version__


class CLIHandler:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Toolbox for GitLab generic packages"
        )
        parser.add_argument("-v", "--version", action="store_true")
        parser.set_defaults(action=self._print_version)
        subparsers = parser.add_subparsers()
        list_parser = subparsers.add_parser(
            name="list",
            description="Lists the available version of a package from the package registry.",
        )
        self._register_list_parser(list_parser)
        download_parser = subparsers.add_parser(
            name="download",
            description="Downloads all files from a specific package version to the current directory.",
        )
        self._register_download_parser(download_parser)
        upload_parser = subparsers.add_parser(
            name="upload", description="Uploads file to a specific package version."
        )
        self._register_upload_parser(upload_parser)
        self.args = parser.parse_args()

    def _print_version(self, args) -> int:
        print(__version__)
        return 0

    def do_it(self) -> int:
        return self.args.action(self.args)

    def _register_common_arguments(self, parser) -> None:
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-H",
            "--host",
            default="gitlab.com",
            type=str,
            help="The host address of GitLab instance without scheme, for example gitlab.com. Note that only https scheme is supported.",
        )
        group.add_argument(
            "-c",
            "--ci",
            action="store_true",
            help="Use this to run the tool in GitLab pipelines. In this case CI_SERVER_HOST, CI_PROJECT_ID, and CI_JOB_TOKEN variables from the environment are used. --project and --token can be used to override project ID and the CI_JOB_TOKEN to a personal or project access token.",
        )
        parser.add_argument(
            "-p",
            "--project",
            type=str,
            help="The project ID or path. For example 123456 or namespace/project.",
        )
        parser.add_argument("-n", "--name", type=str, help="The package name.")
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Private or project access token that is used to authenticate with the package registry. Leave empty if the registry is public. The token must have 'read API' or 'API' scope.",
        )

    def _register_download_parser(self, parser):
        self._register_common_arguments(parser)
        parser.add_argument("-v", "--version", type=str, help="The package version.")
        parser.set_defaults(action=self._download_handler)

    def _args(self, args):
        if args.ci:
            host = os.environ["CI_SERVER_HOST"]
            if args.project:
                project = args.project
            else:
                project = os.environ["CI_PROJECT_ID"]
            if args.token:
                token_user = "PRIVATE-TOKEN"
                token = args.token
            else:
                token_user = "JOB-TOKEN"
                token = os.environ["CI_JOB_TOKEN"]
        else:
            host = args.host
            project = args.project
            token_user = "PRIVATE-TOKEN"
            token = args.token
        name = args.name
        return host, project, name, token_user, token

    def _download_handler(self, args) -> int:
        host, project, name, token_user, token = self._args(args)
        version = args.version
        gitlab = Packages(host, token_user, token)
        package_id = gitlab.get_package_id(project, name, version)
        files = gitlab.list_files(project, package_id)
        ret = 1
        for file in files:
            ret = gitlab.download_file(project, name, version, file)
            if not ret:
                break
        return ret

    def _register_list_parser(self, parser):
        self._register_common_arguments(parser)
        parser.set_defaults(action=self._list_packages)

    def _list_packages(self, args: argparse.Namespace) -> int:
        host, project, name, token_user, token = self._args(args)
        gitlab = Packages(host, token_user, token)
        packages = gitlab.list_packages(project, name)
        print("Name" + "\t\t" + "Version")
        for package in packages:
            print(package["name"] + "\t" + package["version"])

    def _register_upload_parser(self, parser):
        self._register_common_arguments(parser)
        parser.add_argument("-v", "--version", type=str, help="The package version.")
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="The file to be uploaded, for example my_file.txt. Note that only relative paths are supported and the relative path is preserved when uploading the file.",
        )
        parser.set_defaults(action=self._upload)

    def _upload(self, args) -> int:
        host, project, name, token_user, token = self._args(args)
        version = args.version
        file = args.file
        gitlab = Packages(host, token_user, token)
        ret = gitlab.upload_file(project, name, version, file)
        return ret
