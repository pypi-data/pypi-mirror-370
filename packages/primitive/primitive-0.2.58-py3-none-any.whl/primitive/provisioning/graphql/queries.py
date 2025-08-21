authorized_keys_query = """
query authorizedKeys($reservationId: GlobalID!) {
    authorizedKeys(reservationId: $reservationId)
}
"""
