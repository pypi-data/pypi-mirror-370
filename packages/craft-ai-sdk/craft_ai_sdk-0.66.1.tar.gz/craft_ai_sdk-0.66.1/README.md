# Craft AI Python SDK

This Python SDK lets you interact with Craft AI MLOps Platform.

## Installation
This project relies on **Python 3.9+**. Once a supported version of Python is installed, you can install `craft-ai-sdk` from PyPI with:

```console
pip install craft-ai-sdk
```

## Basic usage
You can configure the SDK by instantiating the `CraftAiSdk` class in this way:

```python
from craft_ai_sdk import CraftAiSdk

CRAFT_AI_SDK_TOKEN =  # your access key obtained from your settings page
CRAFT_AI_ENVIRONMENT_URL =  # url to your environment

sdk = CraftAiSdk(sdk_token=CRAFT_AI_SDK_TOKEN, environment_url=CRAFT_AI_ENVIRONMENT_URL)
```

If using the SDK in interactive mode, some additional feedbacks will be printed. You can force disable or enable those logs by either
* Setting the `verbose_log` SDK parameter
* Or setting the `SDK_VERBOSE_LOG` env var
