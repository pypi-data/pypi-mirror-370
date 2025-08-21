whoami_query = """
query whoami {
    whoami {
        username
        defaultOrganization {
            id
            pk
            name
            slug
        }
    }
}
"""
