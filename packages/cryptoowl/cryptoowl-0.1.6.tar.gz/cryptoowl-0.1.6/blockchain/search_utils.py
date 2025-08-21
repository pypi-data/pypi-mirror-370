from datetime import datetime

from blockchain import read_db
from blockchain.constants import GET_ACTIVE_SYMBOLS_DATA_QUERY, GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY, \
    SEARCH_TELEGRAM_DATA_QUERY, GET_TWEETS_QUERY, GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_EXACT_MATCH_QUERY, \
    SEARCH_TELEGRAM_DATA_EXACT_MATCH_QUERY, GET_ACTIVE_COINS_DATA_QUERY, GET_CONFIGURATION_FOR_SEARCH_QUERY
from common_utils.chain_utils import chain_to_id
from common_utils.time_utils import format_datetime


def get_onchain_data(search_term, limit=3, start=0, is_exact_match=False):
    result = []
    total_results = 0

    if len(search_term) >= 40:
        search_condition = f"token_id = '{search_term}' OR pair_id = '{search_term}'"
    elif len(search_term) < 40 and is_exact_match:
        search_condition = f"symbol = '{search_term}' OR name = '{search_term}'"
    else:
        search_condition = f"symbol LIKE '{search_term}%' OR symbol LIKE '${search_term}%' OR name LIKE '{search_term}%' OR name LIKE ' {search_term}%'"

    if start == 0:
        coin_data = read_db.fetchall(query=GET_ACTIVE_COINS_DATA_QUERY.format(search_condition=search_condition))

        for cd in coin_data:
            (symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, marketcap, icon, buy_tax,
             sell_tax, pair_created_at, twitter, telegram, website) = cd
            if not pair_created_at:
                age_in_seconds = None
            else:
                age_in_seconds = datetime.utcnow().timestamp() - int(pair_created_at)
            result.append({
                "symbol": symbol,  # will remove this
                "token_symbol": symbol,
                "name": name,  # will remove this
                "token_name": name,
                "is_coin": is_coin,
                "chain_id": None,
                "chain": None,
                "token_id": token_id,
                "pair_id": pair_id,
                "vol_24_hr": vol_24_hr,  # will remove this
                "vol_24hr": vol_24_hr,
                "liquidity": liquidity,
                "marketcap": marketcap,  # will remove this
                "market_cap": marketcap,
                "icon": icon,  # will remove this
                "token_icon": icon,
                "buy_tax": buy_tax,
                "sell_tax": sell_tax,
                "age_in_seconds": age_in_seconds,
                "pair_created_at": pair_created_at,
                "twitter": twitter,  # will remove this
                "token_twitter": twitter,
                "telegram": telegram,  # will remove this
                "token_telegram": telegram,
                "website": website,  # will remove this
                "token_website": website,
                "is_honeypot": None,
                "can_mint": None,
                "is_proxy": None,
                "is_blacklisted": None,
                "can_burn": None,
                "is_scam": None,
                "can_freeze": None,
                "is_contract_verified": None,
                "pc_24_hr": None
            })
            total_results += 1

        if len(result) >= limit:
            return True, (result[:limit], limit)
    
    internal_search_limit = read_db.fetchall(query=GET_CONFIGURATION_FOR_SEARCH_QUERY)[0][0]

    query = GET_ACTIVE_SYMBOLS_DATA_QUERY.format(search_condition=search_condition, search_term=search_term,
                                                 internal_search_limit=internal_search_limit, start=start,
                                                 limit=limit-len(result))

    if data := read_db.fetchall(query=query):
        for i in data:
            (symbol, name, is_coin, chain, token_id, pair_id, vol_24_hr, liquidity, marketcap, icon, buy_tax, sell_tax,
             pair_created_at, twitter, telegram, website, order_number, score, is_honeypot, can_mint, is_proxy,
             is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified, pc_24_hr, match_priority) = i
            chain = None if is_coin == 2 else chain
            is_coin = is_coin if not is_coin else 1
            chain_id = chain_to_id.get(chain)
            if not pair_created_at:
                age_in_seconds = None
            else:
                age_in_seconds = datetime.utcnow().timestamp() - int(pair_created_at)
            result.append({
                "symbol": symbol,   # will remove this
                "token_symbol": symbol,
                "name": name,   # will remove this
                "token_name": name,
                "is_coin": is_coin,
                "chain_id": chain_id,
                "chain": chain,
                "token_id": token_id,
                "pair_id": pair_id,
                "vol_24_hr": vol_24_hr, # will remove this
                "vol_24hr": vol_24_hr,
                "liquidity": liquidity,
                "marketcap": marketcap, # will remove this
                "market_cap": marketcap,
                "icon": icon,   # will remove this
                "token_icon": icon,
                "buy_tax": buy_tax,
                "sell_tax": sell_tax,
                "age_in_seconds": age_in_seconds,
                "pair_created_at": pair_created_at,
                "twitter": twitter, # will remove this
                "token_twitter": twitter,
                "telegram": telegram,   # will remove this
                "token_telegram": telegram,
                "website": website, # will remove this
                "token_website": website,
                "is_honeypot": is_honeypot,
                "can_mint": can_mint,
                "is_proxy": is_proxy,
                "is_blacklisted": is_blacklisted,
                "can_burn": can_burn,
                "is_scam": is_scam,
                "can_freeze": can_freeze,
                "is_contract_verified": is_contract_verified,
                "pc_24_hr": pc_24_hr
            })
            total_results += 1
        return True, (result, total_results)
    else:
        return False, "No match found!"


def get_twitter_author_handle_data(search_term, limit=3, start=0, is_exact_match=False):
    result = []
    total_results = 0

    if is_exact_match:
        query = GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_EXACT_MATCH_QUERY.format(author_handle=search_term,
                                                                                        start=start, limit=limit)
    else:
        query = GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY.format(author_handle=search_term, start=start,
                                                                            limit=limit)

    if details_from_twitter_profile := read_db.fetchall(query=query):
        for dftp in details_from_twitter_profile:
            (author_handle, name, bio, url_in_bio, profile_image_url, profile_banner_url, followers_count,
             followings_count, account_created_at, lifetime_tweets, lifetime_views, engagement_score, followers_impact,
             symbol_mentions, total_mentions, symbols_in_last_24hr, new_symbols_in_last_24hr,
             unique_author_handle_mentions, author_handle_mentions, tags, mindshare) = dftp

            result.append({
                "author_handle": author_handle,
                "name": name,
                "bio": bio,
                "url_in_bio": url_in_bio,
                "profile_image_url": profile_image_url,
                "profile_banner_url": profile_banner_url,
                "followers_count": followers_count,
                "followings_count": followings_count,
                "account_created_at": account_created_at,
                "crypto_tweets_all": lifetime_tweets,
                "crypto_tweets_views_all": lifetime_views,
                "engagement_score": round(engagement_score) if engagement_score else engagement_score,
                "followers_impact": round(followers_impact) if followers_impact else followers_impact,
                "total_symbols_mentioned": symbol_mentions, # this the total unique symbol mentioned by the author handle
                "symbols_mentioned_in_last_24hr": symbols_in_last_24hr,
                "new_symbols_mentioned_in_last_24hr": new_symbols_in_last_24hr,
                "unique_author_handle_count": unique_author_handle_mentions,
                "total_mention_count": total_mentions,  # this is total mentions done by author handle
                "tags": tags.split(",") if tags else [],
                "mentions_24hr": author_handle_mentions,    # this is the total mention of author handle done by other users
                "mindshare": mindshare
            })
            total_results += 1
        return True, (result, total_results)
    else:
        return False, "No match found!"


def get_telegram_data(search_term, limit=3, start=0, is_exact_match=False):
    result = []
    total_results = 0

    if is_exact_match:
        query = SEARCH_TELEGRAM_DATA_EXACT_MATCH_QUERY.format(search_term=search_term, limit=limit, start=start)
    else:
        query = SEARCH_TELEGRAM_DATA_QUERY.format(search_term=search_term, limit=limit, start=start)

    if telegram_filter_data := read_db.fetchall(query=query):
        for tfd in telegram_filter_data:
            (channel_id, total_mentions, token_mentions, average_mentions_per_day, name, image_url, tg_link,
             members_count, channel_age, win_rate_30_day) = tfd
            telegram_response_dict = {
                "channel_id": channel_id,
                "channel_name": name,
                "image_url": image_url,
                "channel_link": tg_link,
                "total_mentions": total_mentions,
                "token_mentions": token_mentions,
                "members_count": members_count,
                "channel_age": str(channel_age.timestamp()) if channel_age else None,
                "average_mentions_per_day": average_mentions_per_day,
                "win_rate": win_rate_30_day
            }
            result.append(telegram_response_dict)
            total_results += 1
        return True, (result, total_results)
    else:
        return False, "No match found!"


def get_tweets_data(search_term=None, tweet_id=None, author_handle=None, limit=3, start=0):
    result = []
    if not search_term and not tweet_id and not author_handle:
        return False, "Either search_term, tweet_id or author_handle is required"

    where_condition = ""
    if search_term:
        where_condition = f"body LIKE '%{search_term}%'"
    elif tweet_id:
        where_condition = f"tweet_id = '{tweet_id}'"
    elif author_handle:
        where_condition = f"author_handle = '{author_handle}'"
    
    query = GET_TWEETS_QUERY.format(where_condition=where_condition, start=start, limit=limit)

    if data := read_db.fetchall(query=query):
        for i in data:
            tweet_id, body, author_handle, tweet_create_time = i
            result.append({
                "tweet_id": tweet_id,
                "tweet_body": body,
                "author_handle": author_handle,
                "tweet_create_time": format_datetime(input_date_string=str(tweet_create_time))
            })

        return True, result
    else:
        return False, "No match found!"
