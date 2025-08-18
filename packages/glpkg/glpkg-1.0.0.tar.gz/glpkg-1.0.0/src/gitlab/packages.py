import json
from urllib import request, parse


class Packages:
    def __init__(self, host: str, token_type: str, token: str):
        self.host = host
        self.token_type = token_type
        self.token = token

    def api_url(self) -> str:
        return "https://{}/api/v4/".format(parse.quote(self.host))

    def project_api_url(self, project: str) -> str:
        return self.api_url() + "projects/{}/".format(parse.quote_plus(project))

    def get_headers(self):
        headers = {}
        if self.token_type and self.token:
            headers = {self.token_type: self.token}
        return headers

    def list_packages(self, project: str, package_name: str) -> list:
        packages = []
        with request.urlopen(
            request.Request(
                self.project_api_url(project)
                + "packages?package_name="
                + parse.quote_plus(package_name),
                headers=self.get_headers(),
            )
        ) as res:
            data = res.read()
            for package in json.loads(data):
                name = parse.unquote(package["name"])
                version = parse.unquote(package["version"])
                # The GitLab API returns packages that have some match to the filter;
                # let's filter out non-exact matches
                if package_name != name:
                    continue
                packages.append({"name": name, "version": version})
        return packages

    def list_files(self, project: str, package_id: int) -> list:
        files = []
        with request.urlopen(
            request.Request(
                self.project_api_url(project)
                + "packages/"
                + parse.quote_plus(str(package_id))
                + "/package_files",
                headers=self.get_headers(),
            )
        ) as x:
            data = x.read()
            for package in json.loads(
                data,
            ):
                # Only append the filename once to the list of files
                # as there's no way to download them separately through
                # the API
                filename = parse.unquote(package["file_name"])
                if filename not in files:
                    files.append(filename)
        return files

    def get_package_id(
        self, project: str, package_name: str, package_version: str
    ) -> int:
        id = 0
        with request.urlopen(
            request.Request(
                self.project_api_url(project)
                + "packages?package_name="
                + parse.quote_plus(package_name)
                + "&package_version="
                + parse.quote_plus(package_version),
                headers=self.get_headers(),
            )
        ) as res:
            data = res.read()
            package = json.loads(data)
            if len(package) == 1:
                package = package.pop()
                id = package["id"]
        return id

    def download_file(
        self, project: str, package_name: str, package_version: str, file: str
    ) -> int:
        ret = 1
        with request.urlopen(
            request.Request(
                self.project_api_url(project)
                + "packages/generic/"
                + parse.quote_plus(package_name)
                + "/"
                + parse.quote_plus(package_version)
                + "/"
                + parse.quote(str(file)),
                headers=self.get_headers(),
            )
        ) as req:
            with open(str(file), "wb") as file:
                file.write(req.read())
                ret = 0
        return ret

    def upload_file(
        self, project: str, package_name: str, package_version: str, file: str
    ) -> int:
        ret = 1
        with open(str(file), "rb") as data:
            res = request.urlopen(
                request.Request(
                    self.project_api_url(project)
                    + "packages/generic/"
                    + parse.quote_plus(package_name)
                    + "/"
                    + parse.quote_plus(package_version)
                    + "/"
                    + parse.quote(str(file)),
                    method="PUT",
                    data=data,
                    headers=self.get_headers(),
                )
            )
            if res.getcode() == 201:  # 201 is created
                ret = 0
        return ret
