from typing import Any

from git import Repo, Git
import shlex

class PluginGit(Git):
    def __init__(self, repo):
        super().__init__(repo)

    def call_process(self, method: str, *args: Any, **kwargs: Any) -> str:
        return str(self._call_process(method, *args, **kwargs))


class PluginRepo(Repo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.git = PluginGit(self.working_dir)


class GitCommandService:
    @staticmethod
    def call_git_command(working_dir: str, command: str) -> str:
        try:
            repo = PluginRepo(working_dir)
            git = repo.git

            split_command = shlex.split(command)
            return git.call_process(split_command[0], *split_command[1:])
        except Exception as e:
            return str(e)
