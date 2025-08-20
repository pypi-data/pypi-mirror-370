class ExtractionQuery:
    """contains both statement and parameters for the query"""

    def __init__(self, statement: str, params: dict):
        self.statement = statement
        self.params = params
