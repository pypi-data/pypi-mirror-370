from datetime import date
import os
import signal
import sys
from typing import Annotated, List, Optional
import certifi
import httpx
import ssl
from dotenv import load_dotenv

from fastmcp import FastMCP, Context

from pydantic import Field
from rich import print as print
from frankfurtermcp.common import (
    CurrencyConversionResponse,
    EnvironmentVariables,
    get_text_content,
    parse_env,
)

from frankfurtermcp.common import package_metadata, frankfurter_api_url

app = FastMCP(
    name=package_metadata["Name"],
    instructions=package_metadata["Description"],
    on_duplicate_prompts="error",
    on_duplicate_resources="error",
    on_duplicate_tools="error",
)


def _obtain_httpx_client() -> httpx.Client:
    """
    Obtain an HTTPX client for making requests to the Frankfurter API.
    """
    verify = parse_env(
        EnvironmentVariables.HTTPX_VERIFY_SSL,
        default_value=EnvironmentVariables.DEFAULT__HTTPX_VERIFY_SSL,
        type_cast=bool,
    )
    if verify is False:
        print(
            "[yellow]SSL verification is disabled. This is not recommended for production use.[/yellow]"
        )
    ctx = ssl.create_default_context(
        cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
        capath=os.environ.get("SSL_CERT_DIR"),
    )
    client = httpx.Client(
        verify=verify if (verify is not None and verify is False) else ctx,
        follow_redirects=True,
        trust_env=True,
        timeout=parse_env(
            EnvironmentVariables.HTTPX_TIMEOUT,
            default_value=EnvironmentVariables.DEFAULT__HTTPX_TIMEOUT,
            type_cast=float,
        ),
    )
    return client


@app.tool(
    tags=["currency-rates", "supported-currencies"],
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def get_supported_currencies(ctx: Context):
    """
    Returns a list of three-letter currency codes for the supported currencies.
    """
    try:
        with _obtain_httpx_client() as client:
            await ctx.info(
                f"Fetching supported currencies from Frankfurter API at {frankfurter_api_url}"
            )
            http_response = client.get(f"{frankfurter_api_url}/currencies")
            result = http_response.json()
            client.close()
            return get_text_content(data=result, http_response=http_response)
    except httpx.RequestError as e:
        raise ValueError(
            f"Failed to fetch supported currencies from {frankfurter_api_url}: {e}"
        )
    except ValueError as e:
        raise ValueError(f"Failed to parse response from {frankfurter_api_url}: {e}")


def _get_latest_exchange_rates(base_currency: str = None, symbols: list[str] = None):
    """
    Internal function to get the latest exchange rates.
    This is a helper function for the main tool.
    """
    try:
        params = {}
        if base_currency:
            params["base"] = base_currency
        if symbols:
            params["symbols"] = ",".join(symbols)
        with _obtain_httpx_client() as client:
            http_response = client.get(
                f"{frankfurter_api_url}/latest",
                params=params,
            )
            result = http_response.json()
            client.close()
            return result, http_response
    except httpx.RequestError as e:
        raise ValueError(
            f"Failed to fetch latest exchange rates from {frankfurter_api_url}: {e}"
        )
    except ValueError as e:
        raise ValueError(f"Failed to parse response from {frankfurter_api_url}: {e}")


def _get_historical_exchange_rates(
    specific_date: str = None,
    start_date: str = None,
    end_date: str = None,
    base_currency: str = None,
    symbols: list[str] = None,
):
    """
    Internal function to get historical exchange rates.
    This is a helper function for the main tool.
    """
    try:
        params = {}
        if base_currency:
            params["base"] = base_currency
        if symbols:
            params["symbols"] = ",".join(symbols)

        frankfurter_url = frankfurter_api_url
        if start_date and end_date:
            frankfurter_url += f"/{start_date}..{end_date}"
        elif start_date:
            # If only start_date is provided, we assume the end date is the latest available date
            frankfurter_url += f"/{start_date}.."
        elif specific_date:
            # If only specific_date is provided, we assume it is the date for which we want the rates
            frankfurter_url += f"/{specific_date}"
        else:
            raise ValueError(
                "You must provide either a specific date, a start date, or a date range."
            )

        with _obtain_httpx_client() as client:
            http_response = client.get(
                frankfurter_url,
                params=params,
            )
            result = http_response.json()
            client.close()
            return result, http_response
    except httpx.RequestError as e:
        raise ValueError(
            f"Failed to fetch historical exchange rates from {frankfurter_api_url}: {e}"
        )
    except ValueError as e:
        raise ValueError(f"Failed to parse response from {frankfurter_api_url}: {e}")


@app.tool(
    tags=["currency-rates", "exchange-rates"],
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def get_latest_exchange_rates(
    ctx: Context,
    base_currency: Annotated[
        str,
        Field(description="A base currency code for which rates are to be requested."),
    ],
    symbols: Annotated[
        Optional[List[str] | str],
        Field(
            description="A list of target currency codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
        ),
    ] = None,
):
    """
    Returns the latest exchange rates for specific currencies. The
    symbols can be used to filter the results to specific currencies.
    If symbols is not provided, all supported currencies will be returned.
    """
    # Some LLMs make this mistake of passing just one currency but not as a list!
    if type(symbols) is str:
        symbols = [symbols]
    await ctx.info(
        f"Fetching latest exchange rates from Frankfurter API at {frankfurter_api_url}"
    )
    result, http_response = _get_latest_exchange_rates(
        base_currency=base_currency,
        symbols=symbols,
    )
    return get_text_content(data=result, http_response=http_response)


@app.tool(
    tags=["currency-rates", "currency-conversion"],
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def convert_currency_latest(
    ctx: Context,
    amount: Annotated[
        float, Field(description="The amount in the source currency to convert.")
    ],
    from_currency: Annotated[str, Field(description="The source currency code.")],
    to_currency: Annotated[str, Field(description="The target currency code.")],
):
    """
    Converts an amount from one currency to another using the latest exchange rates.
    """
    if from_currency.lower() == to_currency.lower():
        # If the source and target currencies are the same, no conversion is needed
        raise ValueError(
            f"Source currency '{from_currency}' and target currency '{to_currency}' are the same. No conversion needed."
        )
    await ctx.info(
        f"Obtaining latest exchange rates for {from_currency} to {to_currency} from Frankfurter API at {frankfurter_api_url}"
    )
    latest_rates, http_response = _get_latest_exchange_rates(
        base_currency=from_currency,
        symbols=[to_currency],
    )
    await ctx.info(f"Converting {amount} of {from_currency} to {to_currency}")
    if not latest_rates or "rates" not in latest_rates:
        raise ValueError(
            f"Could not retrieve exchange rates for {from_currency} to {to_currency}."
        )
    rate = latest_rates["rates"].get(to_currency)
    if rate is None:
        raise ValueError(
            f"Exchange rate for {from_currency} to {to_currency} not found."
        )
    converted_amount = amount * float(rate)
    result = CurrencyConversionResponse(
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount,
        converted_amount=converted_amount,
        exchange_rate=rate,
        rate_date=latest_rates["date"],
    )
    return get_text_content(data=result, http_response=http_response)


@app.tool(
    tags=["currency-rates", "historical-exchange-rates"],
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def get_historical_exchange_rates(
    ctx: Context,
    base_currency: Annotated[
        str,
        Field(description="A base currency code for which rates are to be requested."),
    ],
    symbols: Annotated[
        Optional[List[str] | str],
        Field(
            description="A list of target currency codes for which rates against the base currency will be provided. If not provided, all supported currencies will be shown."
        ),
    ] = None,
    specific_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="The specific date for which the historical rates are requested in the YYYY-MM-DD format.",
        ),
    ] = None,
    start_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="The start date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
        ),
    ] = None,
    end_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="The end date, of a date range, for which the historical rates are requested in the YYYY-MM-DD format.",
        ),
    ] = None,
):
    """
    Returns historical exchange rates for a specific date or date range.
    If the exchange rates for a specified date is not available, the rates available for
    the closest date before the specified date will be provided.
    Either a specific date, a start date, or a date range must be provided.
    The symbols can be used to filter the results to specific currencies.
    If symbols are not provided, all supported currencies will be returned.
    """
    await ctx.info(
        f"Fetching historical exchange rates from Frankfurter API at {frankfurter_api_url}"
    )
    # Some LLMs make this mistake of passing just one currency but not as a list!
    if type(symbols) is str:
        symbols = [symbols]
    result, http_response = _get_historical_exchange_rates(
        specific_date=specific_date,
        start_date=start_date,
        end_date=end_date,
        base_currency=base_currency,
        symbols=symbols,
    )
    await ctx.info(
        f"Historical exchange rates fetched for {len(result.get('rates', []))} dates."
    )
    return get_text_content(data=result, http_response=http_response)


@app.tool(
    tags=["currency-rates", "currency-conversion", "historical-exchange-rates"],
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def convert_currency_specific_date(
    ctx: Context,
    amount: Annotated[
        float, Field(description="The amount in the source currency to convert.")
    ],
    from_currency: Annotated[str, Field(description="The source currency code.")],
    to_currency: Annotated[str, Field(description="The target currency code.")],
    specific_date: Annotated[
        date,
        Field(
            description="The specific date for which the conversion is requested in the YYYY-MM-DD format."
        ),
    ],
):
    """
    Convert an amount from one currency to another using the exchange rates for a specific date.
    If there is no exchange rate available for the specific date, the rate for the closest available date before
    the specified date will be used.
    """
    if from_currency.lower() == to_currency.lower():
        # If the source and target currencies are the same, no conversion is needed
        raise ValueError(
            f"Source currency '{from_currency}' and target currency '{to_currency}' are the same. No conversion needed."
        )
    await ctx.info(
        f"Obtaining historical exchange rates for {from_currency} to {to_currency} on {specific_date} from Frankfurter API at {frankfurter_api_url}"
    )
    date_specific_rates, http_response = _get_historical_exchange_rates(
        specific_date=specific_date,
        base_currency=from_currency,
        symbols=[to_currency],
    )
    await ctx.info(
        f"Converting {amount} of {from_currency} to {to_currency} on {specific_date}"
    )
    if not date_specific_rates or "rates" not in date_specific_rates:
        raise ValueError(
            f"Could not retrieve exchange rates for {from_currency} to {to_currency} for {specific_date}."
        )
    rate = date_specific_rates["rates"].get(to_currency)
    if rate is None:
        raise ValueError(
            f"Exchange rate for {from_currency} to {to_currency} not found."
        )
    converted_amount = amount * float(rate)
    result = CurrencyConversionResponse(
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount,
        converted_amount=converted_amount,
        exchange_rate=rate,
        rate_date=date_specific_rates["date"],
    )
    return get_text_content(data=result, http_response=http_response)


def main():
    def sigint_handler(signal, frame):
        """
        Signal handler to shut down the server gracefully.
        """
        # Is this handler necessary since we are not doing anything and uvicorn already handles this?
        # Commenting out the following status outputs because it may confuse some MCP clients.
        # print("[green]Attempting graceful shutdown[/green], please wait...")
        # This is absolutely necessary to exit the program
        sys.exit(0)

    load_dotenv()
    # TODO: Should we also catch SIGTERM, SIGKILL, etc.? What about Windows?
    signal.signal(signal.SIGINT, sigint_handler)

    # Commenting out the following status outputs because it may confuse some MCP clients.
    # print(
    #     f"[green]Initiating startup[/green] of [bold]{package_metadata['Name']} {package_metadata['Version']}[/bold], [red]press CTRL+C to exit...[/red]"
    # )
    transport_type = parse_env(
        EnvironmentVariables.MCP_SERVER_TRANSPORT,
        default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_TRANSPORT,
        allowed_values=EnvironmentVariables.ALLOWED__MCP_SERVER_TRANSPORT,
    )
    (
        app.run(
            transport=transport_type,
            host=parse_env(
                EnvironmentVariables.MCP_SERVER_HOST,
                default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_HOST,
            ),
            port=parse_env(
                EnvironmentVariables.MCP_SERVER_PORT,
                default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_PORT,
                type_cast=int,
            ),
            uvicorn_config={
                "timeout_graceful_shutdown": 5,  # seconds
            },
        )
        if transport_type != "stdio"
        else app.run(transport=transport_type)
    )


if __name__ == "__main__":
    main()
