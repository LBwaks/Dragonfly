from enum import StrEnum


class ProviderCapability(StrEnum):
    SYMBOL_UNIVERSE = "symbol_universe"
    INSTRUMENT_OVERVIEW = "instrument_overview"
    QUOTE = "quote"
    COMPANY_PROFILE = "company_profile"
    HISTORICAL_OHLCV = "historical_ohlcv"
    INTRADAY_OHLCV = "intraday_ohlcv"
    CORPORATE_ACTIONS = "corporate_actions"
    FUNDAMENTALS = "fundamentals"
    PEERS = "peers"
    COMPANY_NEWS = "company_news"
    MARKET_NEWS = "market_news"
    SEC_FILINGS = "sec_filings"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_SENTIMENT = "insider_sentiment"
    ANALYST_RECOMMENDATIONS = "analyst_recommendations"
    EARNINGS_HISTORY = "earnings_history"
    EARNINGS_CALENDAR = "earnings_calendar"
    IPO_CALENDAR = "ipo_calendar"
