# glpkg - GitLab Generic Package registry tools 

glpkg is a tool that makes it easy to work with [GitLab generic package registry](https://docs.gitlab.com/user/packages/generic_packages/).


## Installation

Install the tool from with pip:

```bash
pip install glpkg
```

To check the installation and version,  run:


```bash
glpkg --version
```

If you see a version in the terminal, you're good to go!

## Usage

By default, the used GitLab host is gitlab.com. If you use a self-hosted GitLab, use argument `--host my-gitlab.net` with the commands.

> Only https scheme is supported.

To authenticate with the package registry in any of the commands below, use `--token readapitoken123` argument where the `readapitoken123` is a [personal](https://docs.gitlab.com/user/profile/personal_access_tokens/#create-a-personal-access-token) or [project](https://docs.gitlab.com/user/project/settings/project_access_tokens/#create-a-project-access-token) access token, with read API scope. In case the package registry is public, you can omit this argument.

The above arguments are omitted in the examples below to focus on the functions. Add the arguments to change the host or to authenticate with the registry.

In general, run `glpkg --help` when needed.

### Listing package versions

To list the versions of a generic package, run

```bash
glpkg list --project 12345 --name mypackagename
```

Where:
- `12345` is your projects ID ([Find the Project ID](https://docs.gitlab.com/user/project/working_with_projects/#find-the-project-id)) or the path of the project (like `namespace/project`)
- `mypackagename` is the name of the generic package

The output will be, if package is found, something like:

```bash
Name            Version
mypackagename   1.0
mypackagename   1.5
mypackagename   2.0
```

### Download generic package

To download everything from a specific generic package, run

```bash
glpkg download --project 12345 --name mypackagename --version 1.0
```

Where:
- `12345` is your projects ID ([Find the Project ID](https://docs.gitlab.com/user/project/working_with_projects/#find-the-project-id)) or the path of the project (like `namespace/project`)
- `mypackagename` is the name of the generic package
- `1.0` is the version of the generic package from which the files are downloaded

The files will be downloaded in the current working directory. Any pre-existing files will be overridden without warning.

> If a package has multiple files with the same filename, the tool can only download the newest file. This is a restriction of GitLab API.

### Upload a file to a generic package

To upload a file to a version of a generic package, run

```bash
glpkg upload --project 12345 --name mypackagename --version 1.0 --file my-file.txt
```

Where:
- `12345` is your projects ID ([Find the Project ID](https://docs.gitlab.com/user/project/working_with_projects/#find-the-project-id)) or the path of the project (like `namespace/project`)
- `mypackagename` is the name of the generic package
- `1.0` is the version of the generic package to which the file is uploaded
- `my-file.txt` is the file that is uploaded to the generic package. Currently, only relative paths are supported, and the relative path (e.g. `folder/file.txt`) is preserved when uploading the file to the registry.

> A GitLab generic package may have multiple files with the same file name. However, it likely is not a great idea, as they cannot be downloaded separately from the GitLab API.

### Use in GitLab pipelines

If you use the tool in a GitLab pipeline, using `--ci` argument uses [GitLab predefined variables](https://docs.gitlab.com/ci/variables/predefined_variables/) to configure the tool. In this case `CI_SERVER_HOST`, `CI_PROJECT_ID`, and `CI_JOB_TOKEN` environment variables are used. The `--project`, and `--token` arguments can still be used to override the project ID and to use a personal or project access token instead of CI_JOB_TOKEN.

In other words, you don't need to give the `--host`, `--project`, or `--token` arguments if you are interacting with the package registry of the project where the pipeline is running. Example: uploading `my-file.txt` to generic package `mypackagename` version `1.0` in the project package registry in CI:

```bash
glpkg upload --ci --name mypackagename --version 1.0 --file my-file.txt
```

To use the `CI_JOB_TOKEN` with package registry of another projects, add `--project <otherproject ID>` argument. Remember that you may need to add [permissions for the CI_JOB_TOKEN](https://docs.gitlab.com/ci/jobs/ci_job_token/#control-job-token-access-to-your-project) in the other project.


## Limitations

The tool is not perfect (yet) and has limitations. The following limitations are known, but more can exist:

- Uploading files must be done one-by-one.
- Only project registries are supported for now.
- Pagination is not supported for now - in case you have more than 100 versions of a package, not all will be shown.
