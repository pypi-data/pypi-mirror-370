from common_utils.constants import GET_ALL_PROXY_QUERY, SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID
from db.databases import RDSConnection

read_db = RDSConnection(db_secret_name=SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID)


def get_proxy_list():
    proxies = []
    proxies_data = read_db.fetchall(query=GET_ALL_PROXY_QUERY)
    if proxies_data:
        for pd in proxies_data:
            address, port, username, password = pd
            proxies.append({
                'http': f"http://{username}:{password}@{address}:{port}",
                'https': f"http://{username}:{password}@{address}:{port}",
            })

    return proxies
