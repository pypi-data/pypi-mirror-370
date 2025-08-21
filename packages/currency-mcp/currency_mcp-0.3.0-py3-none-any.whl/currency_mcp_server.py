from __future__ import annotations

import contextlib
import datetime as dt

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

API_BASE = "https://api.frankfurter.app"
DEFAULT_TIMEOUT = 12.0

_http_client: httpx.AsyncClient | None = None


class ListCurrenciesResult(BaseModel):
    """Representation of the result of the list_currencies tool."""

    count: int
    currencies: dict[str, str]
    source: str


class ConvertCurrencyArguments(BaseModel):
    """Representation of the arguments of the convert_currency tool."""

    amount: float = Field(..., description="The amount to convert.")
    from_code: str = Field(
        ...,
        description="Source currency code, for example, 'USD'.",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )
    to_code: str = Field(
        ...,
        description="Target currency code, for example, 'VND'.",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )
    date: str | None = Field(
        None,
        description=(
            "Historical date in YYYY-MM-DD format. If omitted, uses latest rates."
        ),
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    @field_validator("date")
    def validate_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            request_date = dt.datetime.strptime(v, "%Y-%m-%d").date()
            if request_date > dt.date.today():
                raise ValueError("Date cannot be in the future.")
            return request_date.isoformat()
        except ValueError as exc:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.") from exc


class ConvertCurrencyResult(BaseModel):
    """Representation of the result of the convert_currency tool."""

    amount: float
    from_code: str
    to_code: str
    date: str
    rate: float
    converted_amount: float
    source: str


async def _get_http_client() -> httpx.AsyncClient:
    """Return a shared HTTP client."""
    global _http_client
    if _http_client:
        return _http_client
    _http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(DEFAULT_TIMEOUT),
    )
    return _http_client


async def _fetch_symbols() -> dict[str, str]:
    """Fetch the list of supported currencies from the API."""
    client = await _get_http_client()
    response = await client.get(f"{API_BASE}/currencies")
    response.raise_for_status()
    data = response.json()
    # Frankfurter returns a simple dict: {"USD": "US Dollar", "EUR": "Euro", ...}
    return {symbol.upper(): description for symbol, description in data.items()}


async def _fetch_rate_once(
    from_code: str,
    to_code: str,
    on_date: dt.date | None = None,
) -> tuple[float | None, str | None]:
    """Fetch the exchange rate for a given currency pair."""
    client = await _get_http_client()

    if on_date is None:
        url = f"{API_BASE}/latest"
    else:
        url = f"{API_BASE}/{on_date.isoformat()}"
    params = {
        "from": from_code.upper(),
        "to": to_code.upper(),
    }
    response = await client.get(url, params=params)
    with contextlib.suppress(Exception):
        response.raise_for_status()
    try:
        data = response.json()
    except Exception:
        return None, None

    # Frankfurter returns { 'amount': 1.0, 'base': 'USD', 'date': 'YYYY-MM-DD', 'rates': { 'EUR': 0.8583 } }
    rates = data.get("rates", {})
    rate = rates.get(to_code.upper())
    effective_date = data.get("date")
    if not rate:
        return None, None
    return float(rate), effective_date


async def _fetch_rate_with_fallback(
    from_code: str,
    to_code: str,
    on_date: dt.date | None = None,
) -> tuple[float | None, str | None]:
    """Fetch the exchange rate for a given currency pair."""
    if from_code.upper() == to_code.upper():
        effective_date = on_date or dt.date.today().isoformat()
        return 1.0, effective_date

    # If no date requested, just fetch once
    if on_date is None:
        rate, effective_date = await _fetch_rate_once(from_code, to_code)
        if not rate:
            raise ValueError("Could not fetch the latest rate.")
        return rate, effective_date or dt.date.today().isoformat()

    # Historical: try that date, then walk back up to 7 days
    attempts = 0
    current_date = on_date
    while attempts < 8:
        rate, effective_date = await _fetch_rate_once(
            from_code.upper(),
            to_code.upper(),
            current_date,
        )
        if rate and effective_date:
            return rate, effective_date
        attempts += 1
        current_date -= dt.timedelta(days=1)

    raise ValueError("No rate found for the requested date or the previous 7 days.")


mcp = FastMCP("Currency Conversion MCP Server")


@mcp.tool()
async def list_currencies():
    """List all supported currencies."""
    symbols = await _fetch_symbols()
    return ListCurrenciesResult(
        count=len(symbols),
        currencies=symbols,
        source=f"{API_BASE}/currencies",
    )


@mcp.tool()
async def convert_currency(
    args: ConvertCurrencyArguments,
) -> ConvertCurrencyResult:
    """Convert a currency amount to another currency."""
    with contextlib.suppress(Exception):
        symbols = await _fetch_symbols()
        if args.from_code.upper() not in symbols:
            raise ValueError(f"Invalid source currency code: {args.from_code}")
        if args.to_code.upper() not in symbols:
            raise ValueError(f"Invalid target currency code: {args.to_code}")

    historical_date: dt.date | None = None
    if args.date:
        historical_date = dt.datetime.strptime(args.date, "%Y-%m-%d").date()

    rate, effective_date = await _fetch_rate_with_fallback(
        args.from_code.upper(),
        args.to_code.upper(),
        historical_date,
    )
    converted_amount = args.amount * rate
    return ConvertCurrencyResult(
        amount=args.amount,
        from_code=args.from_code.upper(),
        to_code=args.to_code.upper(),
        date=effective_date,
        rate=rate,
        converted_amount=converted_amount,
        source=(
            f"{API_BASE}/latest"
            if not historical_date
            else f"{API_BASE}/{effective_date}"
        ),
    )


if __name__ == "__main__":
    mcp.run()
