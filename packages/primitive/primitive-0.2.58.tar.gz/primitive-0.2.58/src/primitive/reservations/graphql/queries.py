from primitive.graphql.utility_fragments import page_info_fragment

from .fragments import reservation_fragment

reservations_query = (
    page_info_fragment
    + reservation_fragment
    + """
query reservations(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: ReservationFilters
) {
  reservations(
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
        ...ReservationFragment
      }
    }
  }
}
"""
)

reservation_query = (
    reservation_fragment
    + """
query reservation($id: GlobalID!) {
  reservation(id: $id) {
    ...ReservationFragment
  }
}
"""
)
