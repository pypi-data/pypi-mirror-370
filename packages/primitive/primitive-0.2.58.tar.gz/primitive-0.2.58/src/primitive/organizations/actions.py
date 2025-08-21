from typing import Optional

from gql import gql

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.queries import organizations_query


class Organizations(BaseAction):
    @guard
    def get_organizations(
        self,
        organization_id: Optional[str] = None,
        slug: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ):
        query = gql(organizations_query)

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
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
        organizations = [edge["node"] for edge in result.data["organizations"]["edges"]]
        return organizations

    @guard
    def get_organization(
        self,
        organization_id: Optional[str] = None,
        slug: Optional[str] = None,
    ):
        query = gql(organizations_query)

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
        if slug:
            filters["slug"] = {"exact": slug}

        variables = {
            "first": 1,
            "filters": filters,
            "order": {
                "createdAt": "DESC",
            },
        }

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        organizations = [edge["node"] for edge in result.data["organizations"]["edges"]]
        return organizations[0]
