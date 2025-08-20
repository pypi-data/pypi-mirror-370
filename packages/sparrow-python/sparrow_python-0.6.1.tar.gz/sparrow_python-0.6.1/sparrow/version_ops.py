import os
from .io import yaml_load, yaml_dump, rm, replace_var_in_file
from .path import relp


class VersionControl:
    def __init__(
            self,
            pkgname: str,
            version: str,
    ):
        self.name = pkgname
        self.version = version

    def set_version(self, version):
        self.version = version

    def _update_pyproject(self, pyproject_path="pyproject.toml"):
        # import toml
        # pyproject = toml.load(pyproject_path)
        # pyproject['tool']['poetry']['version'] = self.config["version"]
        # pyproject['tool']['poetry']['version'] = 0.9
        # with open(pyproject_path, "w", encoding="utf8") as f:
        #     toml.dump(pyproject, f)
        replace_var_in_file(pyproject_path, "version", f'"{self.version}"', from_line=0, to_line=10)

    def update_version(self):
        init_path = relp("__init__.py")
        replace_var_in_file(init_path, "__version__", f'"{self.version}"')

    def update_readme(
            self,
            readme_path="README.md",
            license="MIT",
            author="kunyuan",
            replace_flag=19 * "-",
    ):
        with open(readme_path, "r", encoding="UTF-8") as fr:
            readme = fr.read()
        replace_begin = f"""\
# {self.name}
[![image](https://img.shields.io/badge/Pypi-{self.version}-green.svg)](https://pypi.org/project/{self.name})
[![image](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![image](https://img.shields.io/badge/license-{license}-blue.svg)](LICENSE)
[![image](https://img.shields.io/badge/author-{author}-orange.svg?style=flat-square&logo=appveyor)](https://github.com/beidongjiedeguang)


"""
        readme_list = readme.split(replace_flag)
        readme_list[0] = replace_begin
        new_readme = replace_flag.join(readme_list)

        with open(readme_path, "w", encoding="UTF-8") as fo:
            fo.write(new_readme)

    def upload_pypi(self):
        rm("build", "dist", "eggs", f"{self.name}.egg-info")
        os.system("python -m build")
        os.system("twine upload dist/*")
        rm("build", "dist", "eggs", f"{self.name}.egg-info")

    def install(self):
        pkgname = self.name
        rm("build", "dist", "eggs", f"{pkgname}.egg-info")
        os.system(f"pip uninstall {pkgname} -y && python setup.py install")
        rm("build", "dist", "eggs", f"{pkgname}.egg-info")

    @staticmethod
    def build():
        os.system(f"pythom -m build")
