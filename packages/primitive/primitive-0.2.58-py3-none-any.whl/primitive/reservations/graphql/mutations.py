from primitive.graphql.utility_fragments import operation_info_fragment

from .fragments import reservation_fragment

reservation_create_mutation = (
    operation_info_fragment
    + reservation_fragment
    + """
mutation reservationCreate($input: ReservationCreateInput!) {
  reservationCreate(input: $input) {
    ...ReservationFragment
    ...OperationInfoFragment
  }
}
"""
)

reservation_release_mutation = (
    operation_info_fragment
    + reservation_fragment
    + """
mutation reservationRelease($input: ReservationReleaseInput!) {
  reservationRelease(input: $input) {
    ...ReservationFragment
    ...OperationInfoFragment
  }
}
"""
)
