from primitive.graphql.utility_fragments import operation_info_fragment

register_hardware_mutation = (
    operation_info_fragment
    + """
mutation registerHardware($input: RegisterHardwareInput!) {
    registerHardware(input: $input) {
        ... on Hardware {
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)

register_child_hardware_mutation = (
    operation_info_fragment
    + """
mutation registerChildHardware($input: RegisterChildHardwareInput!) {
    registerChildHardware(input: $input) {
        ... on Hardware {
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)

unregister_hardware_mutation = (
    operation_info_fragment
    + """
mutation unregisterHardware($input: UnregisterHardwareInput!) {
    unregisterHardware(input: $input) {
        ... on Hardware {
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)


hardware_update_mutation = (
    operation_info_fragment
    + """
mutation hardwareUpdate($input: HardwareUpdateInput!) {
    hardwareUpdate(input: $input) {
        ... on Hardware {
            systemInfo
        }
        ...OperationInfoFragment
    }
}
"""
)

hardware_checkin_mutation = (
    operation_info_fragment
    + """
mutation checkIn($input: CheckInInput!) {
    checkIn(input: $input) {
        ... on Hardware {
            createdAt
            updatedAt
            lastCheckIn
        }
        ...OperationInfoFragment
    }
}
"""
)
