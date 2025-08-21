from typing import List, Optional

from gql import gql

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.mutations import job_run_update_mutation
from .graphql.queries import (
    github_app_token_for_job_run_query,
    job_run_query,
    job_run_status_query,
    job_runs_query,
    job_secrets_for_job_run_query,
    jobs_query,
)


class Jobs(BaseAction):
    @guard
    def get_jobs(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        slug: Optional[str] = None,
        first: Optional[int] = 1,
        last: Optional[int] = None,
    ):
        query = gql(jobs_query)

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
        if project_id:
            filters["project"] = {"id": project_id}
        if job_id:
            filters["id"] = job_id
        if slug:
            filters["slug"] = {"exact": slug}

        variables = {
            "first": first,
            "last": last,
            "filters": filters,
            "order": {
                "createdAt": "DESC",
            },
        }

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        jobs = [edge["node"] for edge in result.data["jobs"]["edges"]]
        return jobs

    def get_job_runs(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        reservation_id: Optional[str] = None,
        git_commit_id: Optional[str] = None,
        status: Optional[str] = None,
        conclusion: Optional[str] = None,
        first: Optional[int] = 1,
        last: Optional[int] = None,
    ):
        query = gql(job_runs_query)

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
        if project_id:
            filters["project"] = {"id": project_id}
        if job_id:
            filters["job"] = {"id": job_id}
        if reservation_id:
            filters["reservation"] = {"id": reservation_id}
        if git_commit_id:
            filters["gitCommit"] = {"id": git_commit_id}
        if status:
            filters["status"] = {"exact": status}
        if conclusion:
            filters["conclusion"] = {"exact": status}

        variables = {
            "first": first,
            "last": last,
            "filters": filters,
            "order": {
                "createdAt": "DESC",
            },
        }

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def get_job_run(self, id: str):
        query = gql(job_run_query)
        variables = {"id": id}
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def job_run_update(
        self,
        id: str,
        status: str = None,
        conclusion: str = None,
        file_ids: Optional[List[str]] = [],
        number_of_files_produced: Optional[int] = None,
        parent_pid: Optional[int] = None,
    ):
        mutation = gql(job_run_update_mutation)
        input = {"id": id}
        if status:
            input["status"] = status
        if conclusion:
            input["conclusion"] = conclusion
        if file_ids and len(file_ids) > 0:
            input["files"] = file_ids
        if number_of_files_produced is not None:
            input["numberOfFilesProduced"] = number_of_files_produced
        if parent_pid is not None:
            input["parentPid"] = parent_pid
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    async def ajob_run_update(
        self,
        id: str,
        status: str = None,
        conclusion: str = None,
        file_ids: Optional[List[str]] = [],
        number_of_files_produced: Optional[int] = None,
        parent_pid: Optional[int] = None,
    ):
        mutation = gql(job_run_update_mutation)
        input = {"id": id}
        if status:
            input["status"] = status
        if conclusion:
            input["conclusion"] = conclusion
        if file_ids and len(file_ids) > 0:
            input["files"] = file_ids
        if number_of_files_produced is not None:
            input["numberOfFilesProduced"] = number_of_files_produced
        if parent_pid is not None:
            input["parentPid"] = parent_pid
        variables = {"input": input}
        result = await self.primitive.session.execute_async(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def github_access_token_for_job_run(self, job_run_id: str):
        query = gql(github_app_token_for_job_run_query)
        variables = {"jobRunId": job_run_id}
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result.data["ghAppTokenForJobRun"]

    def get_latest_job_run_for_job(
        self, job_slug: Optional[str] = None, job_id: Optional[str] = None
    ):
        if not job_slug and not job_id:
            raise ValueError("job_slug or job_id is required")
        jobs_results = self.get_jobs(slug=job_slug)
        jobs = [edge["node"] for edge in jobs_results.data["jobs"]["edges"]]

        job_id = jobs.id
        job_run_results = self.get_job_runs(job_id=job_id, first=1)
        job_run = [edge["node"] for edge in job_run_results.data["job_runs"]["edges"]][
            0
        ]
        return job_run

    @guard
    def get_job_status(self, id: str):
        query = gql(job_run_status_query)
        variables = {"id": id}
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def get_job_secrets_for_job_run(self, id: str):
        query = gql(job_secrets_for_job_run_query)
        variables = {"jobRunId": id}
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result.data["jobSecretsForJobRun"]
