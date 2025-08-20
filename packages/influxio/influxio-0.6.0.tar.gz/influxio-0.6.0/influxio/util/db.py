def get_sqlalchemy_dialects():
    """
    Return list of available SQLAlchemy dialects.

    TODO: Synchronize with influxio.util.report.
    """
    import sqlalchemy.dialects

    from influxio.util.compat import entry_points

    dialects = list(sqlalchemy.dialects.__all__)
    eps = entry_points(group="sqlalchemy.dialects")
    dialects += [dialect.name for dialect in eps]
    return sorted(set(dialects))
