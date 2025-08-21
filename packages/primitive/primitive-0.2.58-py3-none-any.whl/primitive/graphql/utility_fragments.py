operation_info_fragment = """
fragment OperationInfoFragment on OperationInfo {
      messages {
        kind
        message
        field
        code
    }
}
"""

page_info_fragment = """
fragment PageInfoFragment on PageInfo {
    hasNextPage
    hasPreviousPage
    startCursor
    endCursor
}
"""
