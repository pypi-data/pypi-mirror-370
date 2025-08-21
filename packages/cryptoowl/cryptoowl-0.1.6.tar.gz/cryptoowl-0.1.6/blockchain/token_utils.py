from blockchain import read_db
from blockchain.constants import GET_TOKEN_DETAILS_FROM_SYMBOL_QUERY, GET_TOKEN_SYMBOL_FOR_MULTIPLE_SYMBOLS_QUERY


def get_token_by_symbol(symbol, limit=1):
    final_token_list = []

    query = GET_TOKEN_DETAILS_FROM_SYMBOL_QUERY
    if data := read_db.fetchall(query=query, values={"symbol": symbol, "limit": limit}):
        for i in data:
            chain, token_id, token_symbol = i
            final_token_list.append({
                "token_id": token_id,
                "chain": chain,
                "token_symbol": token_symbol.upper()
            })
        return True, final_token_list
    else:
        return False, f"No token found for {symbol}"


def get_token_for_multiple_symbol(symbols, limit=1):
    if not isinstance(symbols, list):
        return False, "Please pass the list of symbols. Ex: ['btc', 'pepe']"

    final_token_list = []

    symbols = tuple(symbols)
    query = GET_TOKEN_SYMBOL_FOR_MULTIPLE_SYMBOLS_QUERY.format(symbols=symbols)
    query = query.replace(",)", ")")
    if data := read_db.fetchall(query=query, values={"limit": limit}):
        for i in data:
            chain, token_id, token_symbol, token_rank = i
            final_token_list.append({
                "token_id": token_id,
                "chain": chain,
                "token_symbol": token_symbol.upper(),
                "token_rank": token_rank
            })
        return True, final_token_list
    else:
        return False, f"No token found for {symbols}"
