from .fragments import file_fragment

files_list = (
    file_fragment
    + """

query files(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: FileFilters
) {
  files(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...FileFragment
      }
    }
  }
}
"""
)
