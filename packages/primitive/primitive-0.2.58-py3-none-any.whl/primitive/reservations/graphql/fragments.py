reservation_fragment = """
fragment ReservationFragment on Reservation {
  id
  pk
  createdAt
  updatedAt
  createdBy {
    id
    pk
    email
    username
    displayName
  }
  hardware {
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
  }
  reason
  startedAt
  endedAt
  # elapsedTime
  status
  conclusion
  conclusionMessage
  reservationNumber
}
"""
