[![doi](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.13352143-red.svg)](https://zenodo.org/records/13352143)
[![doc](https://img.shields.io/static/v1?label=Pages&message=User%20Guide&color=blue&style=flat&logo=gitlab)](https://dlr-sy.gitlab.io/pyxmake)
[![PyPi](https://img.shields.io/pypi/v/pyx-core?label=PyPi)](https://pypi.org/project/pyx-core)

# PyXMake
> This subpackage belongs to [PyXMake](https://gitlab.com/dlr-sy/pyxmake) and contains all core functionalities. It is installed automatically with the parent project. However, it is also separately available as a build system dependency. Please refer to the linked [repository](https://gitlab.com/dlr-sy/pyxmake) for documentation and application examples. If you came across the project via the [GitLab Catalog Explorer](https://gitlab.com/explore/catalog), you can jump directly to the [CI/CD Catalog section](#cicd-catalog)

## Downloading
Use GIT to get the latest code base. From the command line, use
```
git clone https://gitlab.dlr.de/dlr-sy/pyxmake pyxmake
```
If you check out the repository for the first time, you have to initialize all submodule dependencies first. Execute the following from within the repository. 
```
git submodule update --init --recursive
```
To fetch all required metadata for each submodule, use
```
git submodule foreach --recursive 'git checkout $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master) || git checkout main'
```
To update all refererenced submodules to the latest production level, use
```
git submodule foreach --recursive 'git pull origin $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master) || git pull origin main'
```
## Installation
PyXMake can be installed from source using [poetry](https://python-poetry.org). If you don't have [poetry](https://python-poetry.org) installed, run
```
pip install poetry --pre --upgrade
```
to install the latest version of [poetry](https://python-poetry.org) within your python environment. Use
```
poetry update
```
to update all dependencies in the lock file or directly execute
```
poetry install
```
to install all dependencies from the lock file. Last, you should be able to import PyXMake as a python package.
```python
import PyXMake
```
## CI/CD Catalog
[PyXMake](https://gitlab.com/dlr-sy/pyxmake) provides its software development and deployment capabilities as pre-built [CI/CD components](https://docs.gitlab.com/ee/ci/components/). The individual components can be integrated either directly via the CI/CD Catalog or classically via the "include" syntax. The components are divided into three groups:
* General
* Python
* Docker

To include a given component, use
```yaml
include:
  - component: $CI_SERVER_FQDN/<groupname>/PyXMake/<component>@<tag>
```
where *\<groupname\>* depends on the local Gitlab repository, *\<component\>* refers to the name of the component under *templates\/*\* and *\<tag\>* to a specific version. *\<tag\>* can also be set to *master* to always use the latest yet potentially unstable version.
## Contact
* [Marc Garbade](mailto:marc.garbade@dlr.de)