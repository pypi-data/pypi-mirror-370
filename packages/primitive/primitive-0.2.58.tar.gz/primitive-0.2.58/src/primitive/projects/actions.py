from typing import Optional

from gql import gql

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.queries import projects_query


class Projects(BaseAction):
    @guard
    def get_projects(
        self,
        organization_id: Optional[str] = None,
        slug: Optional[str] = None,
        first: Optional[int] = 1,
        last: Optional[int] = None,
    ):
        query = gql(projects_query)

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
        if slug:
            filters["slug"] = {"exact": slug}

        variables = {
            "first": first,
            "last": last,
            "filters": filters,
        }

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        projects = [edge["node"] for edge in result.data["projects"]["edges"]]
        return projects
