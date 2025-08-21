SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID = 'social-intelligence-read-db'
INVOCATION_AND_ERROR_LOGGING_URL = "https://sqs.eu-west-1.amazonaws.com/682280826030/invocation_and_error_logging"


GET_ALL_PROXY_QUERY = """
SELECT address, port, username, password
FROM blockchains.proxies
WHERE status
"""
