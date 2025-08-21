job_run_update_mutation = """
mutation jobRunUpdate($input: JobRunUpdateInput!) {
    jobRunUpdate(input: $input) {
        ... on JobRun {
            id
            status
            conclusion
        }
    }
}
"""
