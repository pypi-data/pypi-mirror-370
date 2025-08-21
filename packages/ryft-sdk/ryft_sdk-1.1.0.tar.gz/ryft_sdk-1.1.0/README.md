# Ryft Python SDK

[![Python - Build & Test](https://github.com/RyftPay/ryft-python/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/RyftPay/ryft-python/actions/workflows/build-and-test.yml)
[![PyPI version](https://badge.fury.io/py/ryft-sdk.svg)](https://badge.fury.io/py/ryft-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The Ryft Python SDK allows you to quickly integrate our API into your Python-powered backend services.

## Installation

## Usage

The SDK must be configured with your account's secret key in the Ryft Dashboard. The SDK will automatically determine the environment based on the provided key. For example, `sk_sandbox...` will point to `sandbox`, while `sk_live...` will point to `production`.

### Importing the SDK

You can access the SDK and all of the methods and types by importing it as follows:

```python
from ryft_sdk import Ryft
```

### Initialising with a secret key

You can pass your secret key via the constructor in the `Ryft` package. For example:

```python
ryft = Ryft(secret_key="sk_live_123")
```

### Initialising with environment variables

You can set the following environment variable, and the SDK will automatically pick it up:

* `RYFT_SECRET_KEY`

> [!NOTE]
> Using env variables, you don't have to pass your secret key to the config. This is handled for you by the SDK

## Basic Example

```python
ryft = Ryft(secret_key="sk_live_123")

try:
  resp = await ryft.accounts.get('acc_123456789')
except RyftException as e:
  print(e)
```
