hardware_fragment = """
fragment HardwareFragment on Hardware {
  id
  pk
  name
  slug
  createdAt
  updatedAt
  isAvailable
  isOnline
  isQuarantined
  isHealthy
  systemInfo
  hostname
  sshUsername
  organization {
    id
    pk
    name
    slug
  }
  activeReservation {
    id
    pk
    status
    reservationNumber
    reason
    createdBy {
      username
    }
  }
}
"""
