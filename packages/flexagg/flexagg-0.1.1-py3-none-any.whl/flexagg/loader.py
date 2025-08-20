"""
TyperLoader类，负责扫描目录、识别包、加载脚本和发现Typer实例。
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Tuple

from typer import Typer

from flexagg.config import config
from flexagg.models import TyperModel, PackageConfig
from flexagg.models import TyperTypeEnum
from flexagg.register import Register
from flexagg.utils import panic


class TyperLoader:
    """Typer实例加载器，负责扫描和加载脚本中的Typer实例"""

    def __init__(self):
        self.config = config
        self.typer_list = []

    @staticmethod
    def _load_module_from_file(file_path: Path, module_name: str = None, top_path: Optional[Path] = None):
        """封装模块加载逻辑，包括临时sys.path更新"""
        if not module_name:
            module_name = file_path.stem

        # 临时更新sys.path以支持相对导入
        original_sys_path = list(sys.path)
        if top_path:
            package_dir = top_path
        else:
            package_dir = file_path.parent

        try:
            if str(package_dir) not in sys.path:
                sys.path.insert(0, str(package_dir))

            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module
        except Exception as e:
            print(f"[Skip] Failed to load module {file_path}: {e}")
            return None

        finally:
            sys.path[:] = original_sys_path

    def _load_package(self, path: Path, root_path: Path):
        """加载 flexagg 包"""
        try:
            # 读取 flexagg.yaml 配置
            config_path = path / "flexagg.yaml"
            package_config = PackageConfig.load(config_path)

            # 获取主应用配置
            apps = package_config.apps
            for app in apps:
                mod_name, attr_name = app.split(":", 1)
                typer_ins = self._load_typer_from_package(path, mod_name, attr_name)
                if typer_ins:
                    self.typer_list.append(TyperModel(
                        typer=typer_ins,
                        root_path=root_path,
                        source_path=path,
                        type=TyperTypeEnum.PACKAGE,
                        dependencies=package_config.dependencies,
                        attr_name=attr_name,
                    ))
        except Exception as e:
            panic(f"failed to load package {path}: {e}")

    def _load_typer_from_package(self, package_path: Path, module_name: str, attr_name: str) -> Typer:
        """从包中加载指定的Typer实例"""
        try:
            # 构建模块路径
            module_file = package_path
            if "." in module_name:
                dir_names, file_name = module_name.rsplit(".", 1)
            else:
                dir_names, file_name = [], module_name
            for _dir in dir_names:
                module_file /= _dir
            module_file = module_file / f"{file_name}.py"

            if not module_file.exists():
                panic(f"module_file does not exist: {module_file}")

            # 加载模块
            module = self._load_module_from_file(module_file, module_name, package_path)

            # 获取指定的属性
            typer_instance = getattr(module, attr_name, None)
            if isinstance(typer_instance, Typer):
                return typer_instance
            else:
                panic(f"{attr_name} is not Typer instance")

        except Exception as e:
            panic(f"failed to load typer instance: {e}")

    @staticmethod
    def _find_typer_instances(module: ModuleType) -> List[Tuple[Typer, str]]:
        apps: List[Tuple[Typer, str]] = []
        typer_set = set()

        if hasattr(module, "__fa_apps__"):
            fa_apps = getattr(module, "__fa_apps__")

            if isinstance(fa_apps, Typer):
                typer_set.add(fa_apps)
                apps.append((fa_apps, "__fa_apps__"))
            elif isinstance(fa_apps, list):
                apps.extend((_app, f"__fa_apps__[{idx}]")
                            for idx, _app in enumerate(fa_apps) if isinstance(_app, Typer))
            return apps

        for attr in dir(module):
            if attr.startswith('_'):
                continue
            value = getattr(module, attr)
            if isinstance(value, Typer) and value not in typer_set:
                typer_set.add(value)
                apps.append((value, attr))

        return apps

    def walk_and_load(self, path: Path, root_path: Optional[Path] = None):
        """递归扫描目录，加载Typer实例"""
        if not path.exists():
            print(f"[Skip] Path does not exist: {path}")
            return

        if not path.is_dir():
            return

        if not root_path:
            root_path = path

        if (path / "flexagg.yaml").exists():
            self._load_package(path, root_path)
            return

        init_file = path / "__init__.py"
        if init_file.exists():
            try:
                # __init__.py模块
                module_name = ".".join(path.relative_to(root_path).parts)
                module = self._load_module_from_file(init_file, module_name)
                for ins, attr_name in self._find_typer_instances(module):
                    self.typer_list.append(TyperModel(
                        typer=ins,
                        root_path=root_path,
                        source_path=path,
                        type=TyperTypeEnum.SIMPLE_PACKAGE,
                        attr_name=attr_name,
                    ))
                if hasattr(module, "__fa_apps__"):
                    return

            except Exception as e:
                print(f"failed to load module {init_file}: {e}")

        # 递归扫描子目录和文件
        for item in path.iterdir():
            if item.is_symlink():
                continue
            if item.is_dir():
                self.walk_and_load(item, root_path)
            elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                module_name = ".".join(list(path.relative_to(root_path).parts) + [item.stem])
                module = self._load_module_from_file(item, module_name=module_name)
                if module:
                    for ins, attr_name in self._find_typer_instances(module):
                        self.typer_list.append(TyperModel(
                            typer=ins,
                            root_path=root_path,
                            source_path=item,
                            type=TyperTypeEnum.SCRIPT,
                            attr_name=attr_name,
                        ))

    def create_app(self) -> Typer:
        """
        创建一个新的Typer实例，执行扫描和动态加载，然后返回该实例

        Returns:
            配置好的Typer实例，包含所有动态注册的命令
        """

        # 创建新的Typer实例
        app = Typer(
            name="fa",
            help=("🚀 Flexagg - A flexible aggregator CLI for dynamic script execution\n\n"
                  "Automatically discover and execute CLI tools from configured directories and packages.\n"
                  "Use 'fa --help' to see available commands or 'fa commands' for detailed information."),
            no_args_is_help=True,
            add_completion=True,
        )

        for _dir in self.config.app_dirs:
            self.walk_and_load(_dir)

        register = Register()
        for obj in self.typer_list:
            register.add_typer(obj)
        register.check_conflicts()
        register.register_typer(app)

        return app
