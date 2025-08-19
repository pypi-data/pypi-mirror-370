# compass_api_sdk

Developer-friendly & type-safe Python SDK specifically catered to leverage *compass_api_sdk* API.

<!-- Start Summary [summary] -->
## Summary

Compass API: Compass Labs DeFi API
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [compass_api_sdk](https://github.com/CompassLabs/mono/blob/master/python-sdk/#compassapisdk)
  * [SDK Installation](https://github.com/CompassLabs/mono/blob/master/python-sdk/#sdk-installation)
  * [IDE Support](https://github.com/CompassLabs/mono/blob/master/python-sdk/#ide-support)
  * [SDK Example Usage](https://github.com/CompassLabs/mono/blob/master/python-sdk/#sdk-example-usage)
  * [Authentication](https://github.com/CompassLabs/mono/blob/master/python-sdk/#authentication)
  * [Available Resources and Operations](https://github.com/CompassLabs/mono/blob/master/python-sdk/#available-resources-and-operations)
  * [Retries](https://github.com/CompassLabs/mono/blob/master/python-sdk/#retries)
  * [Error Handling](https://github.com/CompassLabs/mono/blob/master/python-sdk/#error-handling)
  * [Server Selection](https://github.com/CompassLabs/mono/blob/master/python-sdk/#server-selection)
  * [Custom HTTP Client](https://github.com/CompassLabs/mono/blob/master/python-sdk/#custom-http-client)
  * [Resource Management](https://github.com/CompassLabs/mono/blob/master/python-sdk/#resource-management)
  * [Debugging](https://github.com/CompassLabs/mono/blob/master/python-sdk/#debugging)
* [Development](https://github.com/CompassLabs/mono/blob/master/python-sdk/#development)
  * [Maturity](https://github.com/CompassLabs/mono/blob/master/python-sdk/#maturity)
  * [Contributions](https://github.com/CompassLabs/mono/blob/master/python-sdk/#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add compass_api_sdk
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install compass_api_sdk
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add compass_api_sdk
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from compass_api_sdk python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "compass_api_sdk",
# ]
# ///

from compass_api_sdk import CompassAPI

sdk = CompassAPI(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from compass_api_sdk import CompassAPI, models


with CompassAPI(
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:

    res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from compass_api_sdk import CompassAPI, models

async def main():

    async with CompassAPI(
        api_key_auth="<YOUR_API_KEY_HERE>",
    ) as compass_api:

        res = await compass_api.aave_v3.aave_aave_supported_tokens_async(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name           | Type   | Scheme  |
| -------------- | ------ | ------- |
| `api_key_auth` | apiKey | API key |

To authenticate with the API the `api_key_auth` parameter must be set when initializing the SDK client instance. For example:
```python
from compass_api_sdk import CompassAPI, models


with CompassAPI(
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:

    res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [aave_v3](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md)

* [aave_aave_supported_tokens](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_aave_supported_tokens) - Aave Supported Tokens
* [aave_rate](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_rate) - Interest Rates
* [aave_avg_rate](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_avg_rate) - Interest Rates: Time Average
* [aave_std_rate](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_std_rate) - Interest Rates: Standard Deviation
* [aave_reserve_overview](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_reserve_overview) - Reserve Overview
* [aave_token_price](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_token_price) - Token Prices
* [aave_liquidity_change](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_liquidity_change) - Liquidity Index
* [aave_user_position_summary](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_user_position_summary) - Positions - Total
* [aave_user_position_per_token](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_user_position_per_token) - Positions - per Token
* [aave_historical_transactions](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_historical_transactions) - Historical Transactions
* [aave_supply](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_supply) - Supply/Lend
* [aave_borrow](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_borrow) - Borrow
* [aave_repay](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_repay) - Repay Loans
* [aave_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aavev3/README.md#aave_withdraw) - Unstake

### [aerodrome_slipstream](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md)

* [aerodrome_slipstream_liquidity_provision_positions](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_liquidity_provision_positions) - List LP Positions
* [aerodrome_slipstream_pool_price](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_pool_price) - Pool Price
* [aerodrome_slipstream_swap_sell_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_swap_sell_exactly) - Swap - from Specified Amount
* [aerodrome_slipstream_swap_buy_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_swap_buy_exactly) - Swap - into Specified Amount
* [aerodrome_slipstream_liquidity_provision_mint](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_liquidity_provision_mint) - Open a New LP Position
* [aerodrome_slipstream_liquidity_provision_increase](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_liquidity_provision_increase) - Increase an LP Position
* [aerodrome_slipstream_liquidity_provision_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/aerodromeslipstream/README.md#aerodrome_slipstream_liquidity_provision_withdraw) - Withdraw an LP Position


### [erc_4626_vaults](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/erc4626vaults/README.md)

* [vaults_vault](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/erc4626vaults/README.md#vaults_vault) - Get Vault & User Position
* [vaults_deposit](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/erc4626vaults/README.md#vaults_deposit) - Deposit to Vault
* [vaults_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/erc4626vaults/README.md#vaults_withdraw) - Withdraw from Vault

### [ethena](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/ethena/README.md)

* [ethena_vault](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/ethena/README.md#ethena_vault) - Get Vault & User Position
* [ethena_deposit](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/ethena/README.md#ethena_deposit) - Deposit USDe
* [ethena_request](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/ethena/README.md#ethena_request) - Request to Withdraw USDe
* [ethena_unstake](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/ethena/README.md#ethena_unstake) - Unstake USDe

### [morpho](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md)

* [morpho_vaults](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_vaults) - Get Vaults
* [morpho_vault](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_vault) - Get Vault & User Position
* [morpho_markets](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_markets) - Get Markets
* [morpho_market](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_market) - Get Market
* [morpho_market_position](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_market_position) - Check Market Position
* [morpho_user_position](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_user_position) - Check User Position
* [morpho_deposit](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_deposit) - Deposit to Vault
* [morpho_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_withdraw) - Withdraw from Vault
* [morpho_supply_collateral](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_supply_collateral) - Supply Collateral to Market
* [morpho_withdraw_collateral](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_withdraw_collateral) - Withdraw Collateral from Market
* [morpho_borrow](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_borrow) - Borrow from Market
* [morpho_repay](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/morpho/README.md#morpho_repay) - Repay to Market

### [pendle](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md)

* [pendle_market](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_market) - Get Market & User Position
* [pendle_positions](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_positions) - List User's Market Positions
* [pendle_markets](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_markets) - List Market Data
* [pendle_pt](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_pt) - Trade Principal Token (PT)
* [pendle_yt](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_yt) - Trade Yield Token (YT)
* [pendle_liquidity](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_liquidity) - Manage Liquidity (LP)
* [pendle_redeem_yield](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/pendle/README.md#pendle_redeem_yield) - Redeem Claimable Yield

### [sky](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md)

* [sky_position](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md#sky_position) - Check USDS Position
* [sky_buy](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md#sky_buy) - Buy USDS
* [sky_sell](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md#sky_sell) - Sell USDS
* [sky_deposit](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md#sky_deposit) - Deposit USDS
* [sky_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/sky/README.md#sky_withdraw) - Withdraw USDS

### [smart_account](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/smartaccount/README.md)

* [smart_account_batched_user_operations](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/smartaccount/README.md#smart_account_batched_user_operations) - Get Smart Account Batched User Operations

### [swap](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/swap/README.md)

* [swap_odos](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/swap/README.md#swap_odos) - Odos Swap

### [token](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/tokensdk/README.md)

* [token_address](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/tokensdk/README.md#token_address) - Token Address
* [token_price](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/tokensdk/README.md#token_price) - Token Price
* [token_balance](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/tokensdk/README.md#token_balance) - Token Balance
* [token_transfer](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/tokensdk/README.md#token_transfer) - Transfer Tokens

### [transaction_bundler](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/transactionbundler/README.md)

* [transaction_bundler_authorization](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/transactionbundler/README.md#transaction_bundler_authorization) - Enable Transaction Bundling
* [transaction_bundler_execute](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/transactionbundler/README.md#transaction_bundler_execute) - Construct Bundled Transaction
* [transaction_bundler_aave_loop](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/transactionbundler/README.md#transaction_bundler_aave_loop) - AAVE Leverage Long/Short

### [uniswap_v3](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md)

* [uniswap_quote_buy_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_quote_buy_exactly) - Get Quote - to Specified Amount
* [uniswap_quote_sell_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_quote_sell_exactly) - Get quote - From Specified Amount
* [uniswap_pool_price](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_pool_price) - Pool Price
* [uniswap_liquidity_provision_in_range](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_liquidity_provision_in_range) - Check if LP is Active.
* [uniswap_liquidity_provision_positions](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_liquidity_provision_positions) - List LP
* [uniswap_swap_buy_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_swap_buy_exactly) - Buy exact amount
* [uniswap_swap_sell_exactly](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_swap_sell_exactly) - Sell exact amount
* [uniswap_liquidity_provision_mint](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_liquidity_provision_mint) - Open a new LP position
* [uniswap_liquidity_provision_increase](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_liquidity_provision_increase) - Increase an LP position
* [uniswap_liquidity_provision_withdraw](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/uniswapv3/README.md#uniswap_liquidity_provision_withdraw) - Withdraw an LP position

### [universal](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md)

* [generic_portfolio](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_portfolio) - List User Portfolio
* [generic_supported_tokens](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_supported_tokens) - List Supported Tokens
* [generic_supported_chains](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_supported_chains) - List Supported Chains
* [generic_allowance](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_allowance) - Get Allowance
* [generic_ens](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_ens) - Resolve ENS
* [generic_wrap_eth](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_wrap_eth) - Wrap ETH
* [generic_unwrap_weth](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_unwrap_weth) - Unwrap WETH
* [generic_allowance_set](https://github.com/CompassLabs/mono/blob/master/python-sdk/docs/sdks/universal/README.md#generic_allowance_set) - Set Allowance

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from compass_api_sdk import CompassAPI, models
from compass_api_sdk.utils import BackoffStrategy, RetryConfig


with CompassAPI(
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:

    res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM,
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from compass_api_sdk import CompassAPI, models
from compass_api_sdk.utils import BackoffStrategy, RetryConfig


with CompassAPI(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:

    res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`CompassAPIError`](https://github.com/CompassLabs/mono/blob/master/python-sdk/./src/compass_api_sdk/errors/compassapierror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](https://github.com/CompassLabs/mono/blob/master/python-sdk/#error-classes). |

### Example
```python
from compass_api_sdk import CompassAPI, errors, models


with CompassAPI(
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:
    res = None
    try:

        res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

        # Handle response
        print(res)


    except errors.CompassAPIError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.HTTPValidationError):
            print(e.data.detail)  # Optional[List[models.ValidationError]]
```

### Error Classes
**Primary errors:**
* [`CompassAPIError`](https://github.com/CompassLabs/mono/blob/master/python-sdk/./src/compass_api_sdk/errors/compassapierror.py): The base class for HTTP error responses.
  * [`HTTPValidationError`](https://github.com/CompassLabs/mono/blob/master/python-sdk/./src/compass_api_sdk/errors/httpvalidationerror.py): Validation Error. Status code `422`.

<details><summary>Less common errors (5)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`CompassAPIError`](https://github.com/CompassLabs/mono/blob/master/python-sdk/./src/compass_api_sdk/errors/compassapierror.py)**:
* [`ResponseValidationError`](https://github.com/CompassLabs/mono/blob/master/python-sdk/./src/compass_api_sdk/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from compass_api_sdk import CompassAPI, models


with CompassAPI(
    server_url="https://api.compasslabs.ai",
    api_key_auth="<YOUR_API_KEY_HERE>",
) as compass_api:

    res = compass_api.aave_v3.aave_aave_supported_tokens(chain=models.V1AaveAaveSupportedTokensChain.ARBITRUM)

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from compass_api_sdk import CompassAPI
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = CompassAPI(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from compass_api_sdk import CompassAPI
from compass_api_sdk.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = CompassAPI(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `CompassAPI` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from compass_api_sdk import CompassAPI
def main():

    with CompassAPI(
        api_key_auth="<YOUR_API_KEY_HERE>",
    ) as compass_api:
        # Rest of application here...


# Or when using async:
async def amain():

    async with CompassAPI(
        api_key_auth="<YOUR_API_KEY_HERE>",
    ) as compass_api:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from compass_api_sdk import CompassAPI
import logging

logging.basicConfig(level=logging.DEBUG)
s = CompassAPI(debug_logger=logging.getLogger("compass_api_sdk"))
```
<!-- End Debugging [debug] -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

<!-- Placeholder for Future Speakeasy SDK Sections -->
