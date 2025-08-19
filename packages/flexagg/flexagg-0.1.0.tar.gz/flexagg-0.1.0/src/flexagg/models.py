"""
数据模型定义，用于存储Typer实例的元数据。
"""

from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict
from typer import Typer


class TyperTypeEnum(str, Enum):
    PACKAGE = auto()
    SIMPLE_PACKAGE = auto()
    SCRIPT = auto()


class TyperModel(BaseModel):
    """Typer实例的数据模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    typer: Typer = Field(description="Typer实例")
    root_path: Path = Field(description="根路径")
    source_path: Path = Field(description="源文件路径")
    type: TyperTypeEnum = Field(description="Typer类型")
    attr_name: str = Field(description="Typer实例的属性名称")

    dependencies: Optional[str] = Field(None, description="依赖文件路径")

    @computed_field
    @property
    def name(self) -> str:
        if self.typer.info.name:
            if self.typer.info.name.startswith("<") and self.typer.info.name.endswith(">"):
                return self.typer.info.name[1:-1].split(".")[-1].strip()
            return self.typer.info.name
        return self.source_path.stem

    @computed_field
    @property
    def command_path(self) -> List[str]:
        if self.typer.info.name:
            if self.typer.info.name.startswith("<") and self.typer.info.name.endswith(">"):
                return self.typer.info.name[1:-1].split(".")
        relative = list(self.source_path.relative_to(self.root_path).parts)
        if self.type == TyperTypeEnum.SCRIPT:
            relative[-1] = self.name
            return relative

        if self.typer.info.name:
            relative.append(self.typer.info.name)
        return relative


class PackageConfig(BaseModel):
    """flexagg 包配置模型"""
    apps: List[str] = Field(default_factory=lambda: ["main:app"], description="主Typer位置，如 'main:app'")
    dependencies: Optional[str] = Field(None, description="依赖文件路径")

    @classmethod
    def load(cls, config_file: Path):
        with open(config_file, 'r') as f:
            return cls.model_validate(yaml.safe_load(f))


