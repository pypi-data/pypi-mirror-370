"""
Register 将发现的 Typer 实例按路径合并并注册到主应用。
"""

from typing import Dict, List

from typer import Typer, Context

from flexagg.models import TyperModel
from flexagg.utils import panic


def default_callback(ctx: Context):
    ctx.help_option_names = ["-h", "--help"]


class TrieNode:
    """字典树节点"""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.data: List[TyperModel] = []

    def get_sub_typer(self) -> List[TyperModel]:
        """获取当前节点下的所有Typer实例"""
        typers = []
        typers.extend(self.data)
        for child in self.children.values():
            typers.extend(child.get_sub_typer())
        return typers

    def get_conflicts(self) -> List[List[TyperModel]]:
        if len(self.data) > 1 or self.data and self.children:
            return [self.get_sub_typer()]
        conflicts = []
        for node in self.children.values():
            conflict = node.get_conflicts()
            if conflict:
                conflicts.extend(conflict)
        return conflicts

    def merge_typer(self) -> Typer:
        if self.data:
            return self.data[0].typer
        root = Typer()
        for name, node in self.children.items():
            typer = node.merge_typer()
            typer.info.name = name
            typer.info.no_args_is_help = True
            if not typer.registered_callback:
                typer.callback(invoke_without_command=True)(default_callback)
            root.add_typer(typer)
        return root


class Register:
    def __init__(self):
        self.root = TrieNode()

    def add_typer(self, typer: TyperModel) -> None:
        """添加路径"""
        node = self.root
        for part in typer.command_path:
            if part not in node.children:
                node.children[part] = TrieNode()
            node = node.children[part]
        node.data.append(typer)

    def check_conflicts(self):
        conflicts = self.root.get_conflicts()
        if not conflicts:
            return []
        msg = ["[ERROR] Conflict found!!!"]
        for conflict in conflicts:
            msg.append(f"{'.'.join(min(conflict, key=lambda x: len(x.command_path)).command_path)}:")
            for typer in conflict:
                msg.append(f"  - {typer.source_path}:[{'.'.join(typer.command_path)}]({typer.attr_name})")
        msg.append("You can use `FA_SKIP_EXTERNAL_PATH=1 fa config path ls`")
        msg.append("and `FA_SKIP_EXTERNAL_PATH=1 fa config path del <path>` to remove the conflicting paths.")

        panic("\n".join(msg))

    def register_typer(self, app: Typer):
        app.add_typer(self.root.merge_typer())
        if not app.registered_callback:
            app.callback(invoke_without_command=True)(default_callback)
