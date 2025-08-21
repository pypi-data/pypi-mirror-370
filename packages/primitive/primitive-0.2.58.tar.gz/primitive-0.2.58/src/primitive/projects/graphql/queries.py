from primitive.graphql.utility_fragments import page_info_fragment

from .fragments import project_fragment

projects_query = (
    page_info_fragment
    + project_fragment
    + """
query projects(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $filters: ProjectFilters
) {
    projects(
        before: $before
        after: $after
        first: $first
        last: $last
        filters: $filters
    ) {
        totalCount
        pageInfo {
            ...PageInfoFragment
        }
        edges {
            cursor
            node {
                ...ProjectFragment
            }
        }
    }
}
"""
)
