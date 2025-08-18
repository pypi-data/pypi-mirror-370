import os
from metaflow import (
    FlowSpec,
    Config,
    config_expr,
    project,
    get_namespace,
    namespace,
    Task,
)

from subprocess import check_output

from .assets import Asset
from .evals_logger import EvalsLogger

project_ctx = None


def toml_parser(cfgstr):
    try:
        # python >= 3.11
        import tomllib as toml
    except ImportError:
        import toml
    return toml.loads(cfgstr)


class ProjectContext:
    def __init__(self, flow):
        self.flow = flow
        self.project_config = flow.project_config
        self.project_spec = flow.project_spec

        self.project = self.project_config["project"]
        if self.project_spec:
            self.branch = self.project_spec["branch"]
            self.read_only = False
        elif self.project_config.get("dev-assets"):
            self.branch = self.project_config["dev-assets"].get("branch", "main")
            print(f"Using dev assets from branch {self.branch}")
            self.read_only = self.project_config["dev-assets"].get("read-only", True)
        else:
            self.branch = "main"
            self.read_only = True
        print(
            f"Project initialized: {self.project}/{self.branch} | read-only: {self.read_only}"
        )
        self.asset = Asset(
            project=self.project, branch=self.branch, read_only=self.read_only
        )
        self.evals = EvalsLogger(project=self.project, branch=self.branch)

    def register_data(self, name, artifact):
        if hasattr(self.flow, artifact):
            self.asset.register_data_asset(name, kind="artifact", blobs=[artifact])
        else:
            raise AttributeError(
                f"The flow doesn't have an artifact '{artifact}'. Is self.{artifact} set?"
            )

    def get_data(self, name):
        ref = self.asset.consume_data_asset(name)
        kind = ref["data_properties"]["data_kind"]
        if kind == "artifact":
            ns = get_namespace()
            try:
                namespace(None)
                task = Task(ref["created_by"]["entity_id"])
                [artifact] = ref["data_properties"]["blobs"]
                return task[artifact].data
            finally:
                namespace(ns)
        else:
            raise AttributeError(
                f"Data asset '{name}' doesn't seem like an artifact. It is of kind '{kind}'"
            )


@project(name=config_expr("project_config.project"))
class ProjectFlow(FlowSpec):

    project_config = Config(
        "project_config", default="obproject.toml", parser=toml_parser
    )
    project_spec = Config("project_spec", default_value="{}")

    @property
    def prj(self):
        global project_ctx
        if project_ctx is None:
            project_ctx = ProjectContext(self)
        return project_ctx
