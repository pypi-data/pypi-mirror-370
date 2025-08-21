from pathlib import Path
import shutil
from subprocess import run, CalledProcessError

from gql import gql
from loguru import logger

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.queries import github_app_token_query


class Git(BaseAction):
    @guard
    def get_github_access_token(self) -> str:
        query = gql(github_app_token_query)
        filters = {}
        variables = {
            "filters": filters,
        }
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    def download_git_repository_at_ref(
        self,
        git_repo_full_name: str,
        github_access_token: str,
        git_ref: str = "main",
        destination: Path = Path.cwd(),
    ) -> Path:
        logger.debug(f"Downloading source code from {git_repo_full_name} {git_ref}")

        url = (
            f"https://oauth2:{github_access_token}@github.com/{git_repo_full_name}.git"
        )
        source_dir = Path(destination).joinpath(git_repo_full_name.split("/")[-1])

        # Clone with throw an exception if the directory already exists
        if source_dir.exists():
            shutil.rmtree(path=source_dir)

        try:
            run(
                ["git", "clone", url, source_dir, "--no-checkout"],
                check=True,
                # stdout=DEVNULL,
                # stderr=DEVNULL,
            )
        except CalledProcessError:
            raise Exception("Failed to download repository")

        try:
            run(
                ["git", "checkout", git_ref],
                check=True,
                cwd=source_dir,
                # stdout=DEVNULL,
                # stderr=DEVNULL,
            )
        except CalledProcessError:
            # Clean up directory if checkout failed
            shutil.rmtree(path=source_dir)
            raise Exception("Failed to checkout ref")

        return source_dir
