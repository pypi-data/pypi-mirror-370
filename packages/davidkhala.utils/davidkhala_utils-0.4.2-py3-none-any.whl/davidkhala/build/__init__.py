import subprocess
from subprocess import CompletedProcess

from davidkhala.syntax.fs import rm


class Installer:
    def __init__(self, default_directory: str, source_py: str):
        self.dist = default_directory  # directory for executable binary
        self.spec = default_directory  # directory for *.spec
        self.work = default_directory  # directory for build/
        self.file = source_py
        self.name: str | None = None

    @property
    def name_options(self) -> list:
        return ["--name", self.name] if self.name else []

    def build(self) -> CompletedProcess:
        return subprocess.run([
            "pyinstaller",
            '--distpath', self.dist,
            '--specpath', self.spec,
            "--workpath", self.work,
            *self.name_options,
            "--onefile", self.file,
        ])

    def clean(self, force: bool):
        if self.dist != self.spec or force:
            rm(self.spec)
        if self.dist != self.work or force:
            rm(self.work)
