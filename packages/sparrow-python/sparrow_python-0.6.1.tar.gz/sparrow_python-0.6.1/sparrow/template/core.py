from __future__ import annotations
import os
from pathlib import Path
import chevron
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import shutil


class expand_template:
    """替换单个文件模板

    Example
    -------
    >>> expand_template(
    ...     name='config_gen.py',
    ...     template='./config.template.ts',
    ...     out="../web/apps/chatroom/src/",
    ...     substitutions={
    ...         "xxx_key": "xxx_value",
    ...         },
    ...     )
    """

    def __init__(self,
                 name: str | Path,
                 out: str | Path,
                 substitutions: dict,
                 template: str | Path,
                 stdout=False):
        self.name = name if isinstance(name, str) else Path(name)
        self.out = out
        self.template = template if isinstance(template, str) else Path(template)
        self.substitutions = substitutions
        self.show = stdout
        self._gen_code()

    @staticmethod
    def write_targe_path(target_path: str | Path, content: str):
        with open(target_path, 'w') as f:
            f.write(content)

    def _gen_code(self):
        with open(self.template, 'r') as f:
            try:
                result = chevron.render(f, self.substitutions)
            except Exception as e:
                # 非utf8格式跳过
                print(f"substitute {self.template} failed, skip")
                result = f.read()
            if self.show:
                table = Table(title="", box=None)
                table.add_row(Text("\n".join(result.split('\n')[:10]), tab_size=4))
                table.add_row("...")
                print(Panel(table, title=self.template.name, expand=False, ))
            out_path = Path(os.path.join(self.out, self.name))
            if not out_path.parent.exists():
                os.makedirs(out_path.parent)
            self.write_targe_path(str(out_path), result)


class Substituter:
    def __init__(self, stdout=True):
        self._root_dir = None
        self._stdout = stdout

    def render(self, src_dir: str | Path, out_dir: str | Path, substitutions: dict,
               exclude: list | None = None):
        """将`src_dir`中所有文件替换`substitutions`中的key为value
        并输出相同目录树到`out_dir`目录。

        Parameters
        ----------
        src_dir : str or Path
            源目录; 递归遍历指定文件目录下的每个文件目录
        out_dir : str or Path
            输出目录; 递归过程中保持不变
        substitutions : dict
            替换字典; 对文件目录中的每个文件执行替换
        exclude: list or None
            路径中无需替换的文件名/路径

        Examples
        --------
        >>> subst = Substituter()
        ... subst.render("./src", "./out", {"package_name": "sparrow"})
        """
        src_dir = Path(src_dir) if type(src_dir) == 'str' else src_dir
        if exclude is None:
            exclude = [".so", ".pyc"]
        if self._root_dir is None:
            self._root_dir = src_dir
        for i in src_dir.iterdir():
            if i.is_dir():
                self.render(i, out_dir, substitutions)
            elif any([i.name.endswith(_) for _ in exclude]):
                # print(f"skipping:{str(i)}")
                continue
            else:
                rel_name = i.relative_to(self._root_dir)
                expand_template(
                    name=rel_name,
                    out=out_dir,
                    template=i,
                    substitutions=substitutions,
                    stdout=self._stdout
                )

    @staticmethod
    def render_dir(src_name: str | Path, target_name: str | Path):
        p1 = Path(src_name)
        p2 = Path(target_name)
        if p2.exists():
            p2_file = str(p2)
            p2_file_bk = f"{p2_file}.bk"
            shutil.move(p2_file, p2_file_bk)
            print(f"Warning: Path {p2_file} \nexists! Backup to {p2_file_bk}")
        p1.rename(p2)
