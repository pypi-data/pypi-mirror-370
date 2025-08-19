# OpenAI Driver Debugging

## HTTP Debugging via Environment Variable

To debug HTTP requests and responses for the OpenAI driver, set the environment variable `OPENAI_DEBUG_HTTP=1` before running your application. This will print the full HTTP request and response bodies to the console for troubleshooting purposes.

**Example (PowerShell):**

```
$env:OPENAI_DEBUG_HTTP=1
python your_app.py
```

**Example (bash):**

```
OPENAI_DEBUG_HTTP=1 python your_app.py
```

This feature is implemented in `janito/drivers/openai/driver.py` and works by wrapping the OpenAI client HTTP transport with a debug logger when the environment variable is set.
