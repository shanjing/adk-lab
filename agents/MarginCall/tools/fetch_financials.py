"""Fetch key financials (revenue, net income, balance sheet, cash flow) for a stock ticker using yfinance."""

from datetime import datetime

import yfinance as yf

from tools.logging_utils import logger

# Keys we read from Ticker.info; use stable names and fallbacks
INFO_KEYS = [
    ("totalRevenue", "total_revenue"),
    ("revenuePerShare", "revenue_per_share"),
    ("netIncomeToCommon", "net_income"),
    ("grossProfits", "gross_profits"),
    ("ebitda", "ebitda"),
    ("totalDebt", "total_debt"),
    ("totalCash", "total_cash"),
    ("freeCashflow", "free_cash_flow"),
    ("operatingCashflow", "operating_cash_flow"),
    ("marketCap", "market_cap"),
    ("debtToEquity", "debt_to_equity"),
    ("currentRatio", "current_ratio"),
    ("trailingPE", "trailing_pe"),
    ("forwardPE", "forward_pe"),
]


def fetch_financials(ticker: str) -> dict:
    """
    Fetch key financial metrics for a stock ticker from yfinance.

    Returns total revenue, net income, debt, cash, market cap, and related ratios when available.
    """
    logger.info("--- Tool: fetch_financials called for %s ---", ticker)

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            return {
                "status": "error",
                "error_message": f"Could not fetch financials for {ticker}",
            }

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        financials = {"status": "success", "ticker": ticker, "timestamp": current_time}

        for info_key, out_key in INFO_KEYS:
            val = info.get(info_key)
            if val is not None:
                financials[out_key] = val

        if len(financials) <= 3:
            return {
                "status": "error",
                "error_message": f"No financial data available for {ticker}",
            }

        return financials

    except Exception as e:
        logger.exception("Error fetching financials for %s", ticker)
        return {
            "status": "error",
            "error_message": f"Error fetching financials: {str(e)}",
        }
