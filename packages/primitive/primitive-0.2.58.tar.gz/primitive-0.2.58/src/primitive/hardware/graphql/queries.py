from .fragments import hardware_fragment

hardware_list = (
    hardware_fragment
    + """

query hardwareList(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
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
        ...HardwareFragment
      }
    }
  }
}
"""
)

nested_children_hardware_list = (
    hardware_fragment
    + """

query hardwareList(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
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
        ...HardwareFragment
        children {
          ...HardwareFragment
          fingerprint
        }
      }
    }
  }
}
"""
)

hardware_details = (
    hardware_fragment
    + """

query hardwareDetails(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
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
        ...HardwareFragment
        children {
          ...HardwareFragment
          fingerprint
        }
      }
    }
  }
}
"""
)
