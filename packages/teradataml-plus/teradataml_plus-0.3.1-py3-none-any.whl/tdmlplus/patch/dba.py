import teradataml as tdml

def get_amps_count():
    """
    Returns the number of AMPs (Access Module Processors) in the Teradata system.

    This function queries  the number of AMPs available
    in the current Teradata session. Useful for workload estimation or data distribution insights.

    Returns:
    -------
    int
        Number of AMPs in the system.
    """
    return tdml.DataFrame.from_query("""
        SELECT HASHAMP() + 1 AS Number_of_AMPs
        """).to_pandas().values[0][0]