from sparrow.template.core import Substituter
from sparrow.path import relp
from sparrow.cli import print_directory_tree
from pathlib import Path
from rich import print
import os


def create_project(project_name="my-project", out_dir='./out', verbose=True):
    project_name = project_name.replace('-', '_')
    src_path = relp('src', return_str=False)
    out_path = Path(out_dir)
    substituter = Substituter(stdout=False)
    substituter.render(src_path,
                       out_path.absolute(),
                       substitutions={"project_name": project_name},
                       exclude=[".so", ".pyc"]
                       )
    substituter.render_dir(os.path.join(out_path, "project_name"),
                           os.path.join(out_path, project_name))
    print(f"project generate success!")
    if verbose:
        print_directory_tree(out_path)


if __name__ == "__main__":
    create_project()
