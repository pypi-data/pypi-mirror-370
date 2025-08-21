from primitive.graphql.utility_fragments import operation_info_fragment

file_update_mutation = (
    operation_info_fragment
    + """
mutation fileUpdate($input: FileInputPartial!) {
    fileUpdate(input: $input) {
        ... on File {
            id
            pk
        }
        ...OperationInfoFragment
    }
}
"""
)

pending_file_create_mutation = (
    operation_info_fragment
    + """
mutation pendingFileCreate($input: PendingFileCreateInput!) {
    pendingFileCreate(input: $input) {
        ... on File {
            id
            pk
            partsDetails
        }
        ...OperationInfoFragment
    }
}
"""
)

update_parts_details = (
    operation_info_fragment
    + """
mutation updatePartsDetails($input: UpdatePartsDetailsInput!) {
    updatePartsDetails(input: $input) {
        ... on File {
            id
            pk
            partsDetails
        }
        ...OperationInfoFragment
    }
}
"""
)
