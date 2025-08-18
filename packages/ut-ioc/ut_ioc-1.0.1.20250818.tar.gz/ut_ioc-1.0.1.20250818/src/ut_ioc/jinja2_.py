# coding=utf-8
# from collections.abc import Callable
from typing import Any

import os
import yaml
import jinja2
from logging import Logger

TyAny = Any
TyDic = dict[Any, Any]
TyLogger = Logger
TyPath = str
TyStr = str
TyJinja2Env = jinja2.environment.Environment
TyJinja2Tmpl = jinja2.environment.Template

TnDic = None | TyDic
TnStr = None | TyStr


class Jinja2_:
    """
    Manage Object to Json file affilitation
    """
    @staticmethod
    def read_template(path: TyPath) -> TyJinja2Tmpl:
        directory, file = os.path.split(path)
        env: TyJinja2Env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(directory))
        return env.get_template(file)

    @classmethod
    def read(cls, path: TyPath, **kwargs) -> Any:
        try:
            # read jinja template from file
            template: TyJinja2Tmpl = cls.read_template(path)

            # render template as yaml string
            template_rendered: str = template.render(kwargs)

            # load yaml string into object
            return yaml.safe_load(template_rendered)
        except IOError as exc:
            msg = f"Exception: {exc}\nNo such file or directory with path='{path}'"
            raise Exception(msg)
