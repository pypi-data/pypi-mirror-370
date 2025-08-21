# Railtown AI Logging Python Package

A Python logging handler that integrates with Railtown AI for error tracking and monitoring, similar to Sentry's approach.

## Setup

1. Sign up for [Railtown AI - Conductr](https://conductr.ai)
2. Create a project, navigate to the Project Configuration page, and copy your API key
3. In your app:

   1. Install the Railtown AI SDK: `pip install railtownai`
   2. Initialize Railtown AI with your API key: `railtownai.init('YOUR_RAILTOWN_API_KEY')`
   3. Use Python's native logging - all logs will automatically be sent to Railtown AI

## Basic Usage

```python
import logging
import railtownai

# Initialize Railtown AI
railtownai.init('YOUR_RAILTOWN_API_KEY')

# Use Python's native logging - all logs are sent to Railtown AI
logging.info("User logged in", extra={"user_id": 123, "action": "login"})
logging.warning("High memory usage detected", extra={"memory_usage": "85%"})
logging.error("Database connection failed", extra={"db_host": "localhost"})

# Log exceptions with full stack traces
try:
    result = 1 / 0
except Exception:
    logging.exception("Division by zero error")
```

## Breadcrumbs

Railtown AI supports breadcrumbs - contextual information that gets attached to log events. This is useful for tracking user actions or system state leading up to an error.

```python
import logging
import railtownai

railtownai.init('YOUR_RAILTOWN_API_KEY')

# Add breadcrumbs throughout your application
railtownai.add_breadcrumb("User clicked login button", category="ui")
railtownai.add_breadcrumb("Validating user credentials", category="auth")
railtownai.add_breadcrumb("Database query executed", category="database",
                         data={"query": "SELECT * FROM users", "duration_ms": 45})

# When an error occurs, all breadcrumbs are automatically attached
try:
    # Some operation that might fail
    result = risky_operation()
except Exception:
    logging.exception("Operation failed")  # This will include all the breadcrumbs above
```

## Advanced Usage

### Custom Logging Configuration

```python
import logging
import railtownai

# Initialize Railtown AI
railtownai.init('YOUR_RAILTOWN_API_KEY')

# Configure your own logger
logger = logging.getLogger('myapp')
logger.setLevel(logging.DEBUG)

# Add console handler for local development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Railtown handler is automatically added to root logger
logger.info("Application started")
logger.error("Something went wrong", extra={"component": "payment_processor"})
```

### Logging RailTracks Agent Runs

In your RailTracks application, when you create a Runner, you will need to pass in the
v2.x Railtown AI Python Logger so that it can collect the Run ID of the Agent, as well as,
upload the Agent Run data to Conductr Platform so you can see the logs there.

```python
import logging
import railtownai # Railtown AI's Logging Handler
import railtracks as rt

railtownai.init("YOUR_API_KEY")

# RailTracks Framework will automatically log messages and exceptions assuming you're using the native Python logging lib
result = await rt.call(TextAnalyzer, rt.llm.MessageHistory([rt.llm.UserMessage("Hello world! This is a test of the RailTracks framework.")]))

```

### Uploading Agent Run Data

The Railtown AI Logger provides a method to upload agent run data directly to Azure Blob Storage using presigned SAS URLs. This is useful for storing structured data about agent executions.

#### Single Payload Upload

```python
import railtownai

railtownai.init("YOUR_API_KEY")

# Prepare agent run data
agent_run_data = {
    "name": "my_agent_run",
    "nodes": [{"identifier": "node1", "node_type": "planner"}],
    "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
    "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
}

# Upload single payload
success = railtownai.upload_agent_run(agent_run_data)

if success:
    print("✅ Agent run data uploaded successfully!")
else:
    print("❌ Failed to upload agent run data")
```

#### Batch Payload Upload

For performance reasons, you can upload multiple agent run payloads in a single call. Each payload will get its own fresh SAS URL and be uploaded individually.

```python
# Prepare multiple agent run data payloads
agent_run_data_array = [
    {
        "name": "agent_run_1",
        "nodes": [{"identifier": "node1", "node_type": "planner"}],
        "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
        "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
    },
    {
        "name": "agent_run_2",
        "nodes": [{"identifier": "node2", "node_type": "executor"}],
        "steps": [{"step": 2, "time": 1234567891, "identifier": "step2"}],
        "edges": [{"source": "node2", "target": "node3", "identifier": "edge2", "details": {}}],
    },
]

# Upload array of payloads
success = railtownai.upload_agent_run(agent_run_data_array)

if success:
    print("✅ All agent run data payloads uploaded successfully!")
else:
    print("❌ Failed to upload one or more agent run data payloads")
```

**Important Notes:**

- Each payload must contain `nodes`, `steps`, and `edges` arrays with at least one element each
- The method returns `True` only if ALL uploads succeed, `False` if ANY upload fails
- Each payload gets its own fresh SAS URL from the Platform API
- The method maintains backward compatibility with single payload uploads

## Migration from v1.0 to v2.0

The Railtown AI Python Logger is now a logging handler for Python's Logging Framework.

### v2.0 API

```python
import logging
import railtownai

railtownai.init('YOUR_API_KEY')
logging.error("Error message")
logging.exception("Exception occurred")
```

### Key Features:

- Use Python's native `logging.info()`, `logging.error()`, `logging.exception()`
- All logs automatically include breadcrumbs
- Better integration with Python's logging ecosystem
- Support for structured logging with `extra` parameter

## Configuration

The Railtown handler automatically:

- Sets the root logger level to INFO (if it was higher)
- Adds itself to the root logger
- Handles API key validation
- Manages breadcrumbs across all loggers

## Contributing

See the [contributing guide](./CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows you to:

- Use the software for any purpose
- Modify the software
- Distribute the software
- Use it commercially
- Use it privately
- Sublicense it

The only requirement is that the original copyright notice and license must be included in all copies or substantial portions of the software.

For the full license text, please see the [LICENSE](LICENSE) file.
