SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID = "social-intelligence-read-db"
SOCIAL_INTELLIGENCE_DB_SECRET_ID = "social-intelligence-db"

GET_TOKEN_DETAILS_FROM_SYMBOL_QUERY = """
SELECT chain, token_id, token_symbol
FROM blockchains.active_pairs_dextools
WHERE token_symbol = %(symbol)s
AND vol24h > 0
ORDER BY vol24h DESC
LIMIT %(limit)s
"""

GET_TOKEN_SYMBOL_FOR_MULTIPLE_SYMBOLS_QUERY = """
SELECT *
FROM (
	SELECT chain, token_id, token_symbol, 
	DENSE_RANK() OVER (PARTITION BY token_symbol ORDER BY vol24h DESC) AS token_rank
	FROM blockchains.active_pairs_dextools
	WHERE token_symbol IN {symbols}
	AND vol24h > 0
	ORDER BY vol24h DESC
) AS sub
WHERE token_rank <= %(limit)s
"""

GET_ACTIVE_COINS_DATA_QUERY = """
SELECT symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, 
marketcap, 
CASE
	WHEN icon IS NULL
	THEN profile_image_url 
	ELSE icon
END AS icon, buy_tax, sell_tax, pair_created_at, twitter, telegram, website
FROM blockchains.active_symbols AS ats
WHERE is_coin = 1
AND ({search_condition})
ORDER BY marketcap DESC
"""

GET_ACTIVE_SYMBOLS_DATA_QUERY = """
WITH ranked_token AS (
    SELECT *, 
    	ROW_NUMBER() OVER (PARTITION BY chain_id ORDER BY score DESC) AS row_num
    FROM (
        SELECT overall_rank, token_rank, pair_rank, symbol, name, is_coin, 
        CASE
        	WHEN is_coin = 2
        	THEN CONCAT(symbol, '_', name)
        	else chain_id
        END AS chain_id,
        token_id, pair_id, vol_24_hr, liquidity, marketcap, 
        CASE 
            WHEN icon IS NULL
            THEN profile_image_url
            ELSE icon
        END AS icon, buy_tax, sell_tax, pair_created_at, twitter, telegram, website,
        CASE
            WHEN symbol = '{search_term}' OR name = '{search_term}' THEN 1
            ELSE 2
        END AS match_priority,
        CASE
            WHEN security_tag = "scam" 
            THEN NULL
            ELSE ((liquidity * 7) + (marketcap * 2) + (vol_24_hr * 7))
        END AS score,
        is_honeypot, can_mint, is_proxy, is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified,
        pc_24_hr
        FROM blockchains.active_symbols
        WHERE is_coin != 1
        AND ({search_condition})
    ) AS sub
), all_chains_top_result AS (
    SELECT 
        overall_rank, token_rank, pair_rank, symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, 
        marketcap, icon, buy_tax, sell_tax, pair_created_at, twitter, telegram, website, score, 
        is_honeypot, can_mint, is_proxy, is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified,
        pc_24_hr, 1 AS order_number, match_priority
    FROM ranked_token
    WHERE row_num = 1
    ORDER BY match_priority, score DESC
    LIMIT {internal_search_limit}
), remaining_results AS (
    SELECT 
        overall_rank, token_rank, pair_rank, symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, 
        marketcap, icon, buy_tax, sell_tax, pair_created_at, twitter, telegram, website, score, 
        is_honeypot, can_mint, is_proxy, is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified,
        pc_24_hr, 2 AS order_number, match_priority
    FROM ranked_token
    WHERE token_id NOT IN (SELECT token_id FROM all_chains_top_result)
    AND pair_rank = 1
    ORDER BY match_priority, score DESC
)       
SELECT symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, marketcap, icon, 
buy_tax, sell_tax, pair_created_at, twitter, telegram, website, order_number, score,
is_honeypot, can_mint, is_proxy, is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified,
pc_24_hr, match_priority
FROM all_chains_top_result
UNION
SELECT symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, marketcap, icon, 
buy_tax, sell_tax, pair_created_at, twitter, telegram, website, order_number, score,
is_honeypot, can_mint, is_proxy, is_blacklisted, can_burn, is_scam, can_freeze, is_contract_verified,
pc_24_hr, match_priority
FROM remaining_results
ORDER BY match_priority, order_number, score DESC
LIMIT {limit}
OFFSET {start}
"""

GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY = """
WITH filtered_twitter_profile AS (
	SELECT handle, name, bio, url_in_bio, profile_image_url, profile_banner_url, followers_count, followings_count, 
	account_created_at, lifetime_tweets, lifetime_views, engagement_score, followers_impact
	FROM tickr.twitter_profile
	WHERE handle LIKE '{author_handle}%' OR name LIKE '{author_handle}%'
	ORDER BY followers_count DESC
	LIMIT {limit}
    OFFSET {start}
)
SELECT ftp.handle, ftp.name, ftp.bio, ftp.url_in_bio, ftp.profile_image_url, ftp.profile_banner_url, ftp.followers_count, 
ftp.followings_count, ftp.account_created_at, ftp.lifetime_tweets, ftp.lifetime_views, ftp.engagement_score, ftp.followers_impact,
ahk.total_symbols, ahk.total_mention_count, ahk.symbols_in_last_24hr, ahk.new_symbols_in_last_24hr, 
ahk.unique_author_handle_count, ahm.total_mentions AS author_handle_mentions,
(
        SELECT GROUP_CONCAT(DISTINCT tpt.tag_name SEPARATOR ',') AS tag
        FROM twitter.twitter_profile_tags AS tpt 
        WHERE tpt.handle = ftp.handle
) AS tags, ahm.mindshare
FROM filtered_twitter_profile AS ftp
LEFT JOIN twitter.author_handle_kpi AS ahk ON ftp.handle = ahk.author_handle
LEFT JOIN twitter.author_handle_mentions AS ahm ON ftp.handle = ahm.author_handle
"""

GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_EXACT_MATCH_QUERY = """
SELECT tp.handle, tp.name, tp.bio, tp.url_in_bio, tp.profile_image_url, tp.profile_banner_url, tp.followers_count, 
tp.followings_count, tp.account_created_at, tp.lifetime_tweets, tp.lifetime_views, tp.engagement_score, tp.followers_impact,
ahk.total_symbols, ahk.total_mention_count, ahk.symbols_in_last_24hr, ahk.new_symbols_in_last_24hr, 
ahk.unique_author_handle_count, ahm.total_mentions AS author_handle_mentions,
(
	SELECT GROUP_CONCAT(DISTINCT tpt.tag_name SEPARATOR ',') AS tag
	FROM twitter.twitter_profile_tags AS tpt 
	WHERE tpt.handle = tp.handle
) AS tags, ahm.mindshare
FROM tickr.twitter_profile AS tp 
LEFT JOIN twitter.author_handle_kpi AS ahk ON tp.handle = ahk.author_handle
LEFT JOIN twitter.author_handle_mentions AS ahm ON tp.handle = ahm.author_handle
WHERE tp.handle = '{author_handle}'
OR tp.name = '{author_handle}'
ORDER BY followers_count DESC
LIMIT {limit}
OFFSET {start};
"""

SEARCH_TELEGRAM_DATA_QUERY = """
SELECT
    tcp.channel_id,
    tcp.total_mentions,
    tcp.token_mentions,
    tcp.average_mentions_per_day,
    te.name,
    te.image_url,
    te.tg_link,
    te.members_count,
    te.channel_age,
    tcp.win_rate_30_day
FROM
    telegram.telegram_channel_properties AS tcp
LEFT JOIN
    telegram.telegram_entity AS te
ON
    tcp.channel_id = te.channel_id
WHERE
    te.name LIKE '%{search_term}%'
    ORDER BY tcp.total_mentions DESC
LIMIT {limit}
OFFSET {start};
"""

SEARCH_TELEGRAM_DATA_EXACT_MATCH_QUERY = """
SELECT
    tcp.channel_id,
    tcp.total_mentions,
    tcp.token_mentions,
    tcp.average_mentions_per_day,
    te.name,
    te.image_url,
    te.tg_link,
    te.members_count,
    te.channel_age,
    tcp.win_rate_30_day
FROM
    telegram.telegram_channel_properties AS tcp
LEFT JOIN
    telegram.telegram_entity AS te
ON
    tcp.channel_id = te.channel_id
WHERE
    te.name = '{search_term}'
    ORDER BY tcp.total_mentions DESC
LIMIT {limit}
OFFSET {start};
"""

GET_TWEETS_QUERY = """
SELECT tweet_id, body, author_handle, tweet_create_time
FROM twitter.enhanced_tweets
WHERE {where_condition}
ORDER BY tweet_create_time DESC
LIMIT {limit}
OFFSET {start};
"""

GET_CONFIGURATION_FOR_SEARCH_QUERY = """
SELECT search
FROM blockchains.configuration
"""
