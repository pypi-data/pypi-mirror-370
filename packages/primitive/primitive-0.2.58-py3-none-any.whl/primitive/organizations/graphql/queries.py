from primitive.graphql.utility_fragments import page_info_fragment

from .fragments import organization_fragment

organizations_query = (
    page_info_fragment
    + organization_fragment
    + """
query organizations(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $filters: OrganizationFilters
    $order: OrganizationOrder
) {
    organizations(
        before: $before
        after: $after
        first: $first
        last: $last
        filters: $filters
        order: $order
    ) {
        totalCount
        pageInfo {
            ...PageInfoFragment
        }
        edges {
            cursor
            node {
                ...OrganizationFragment
            }
        }
    }
}
"""
)
