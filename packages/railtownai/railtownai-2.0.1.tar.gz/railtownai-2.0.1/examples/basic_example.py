#!/usr/bin/env python3
"""
Example usage of Railtown AI Python SDK with your API key

This example demonstrates how to use the Railtown logger with your specific API key.
Loads the API key from environment variables or .env file.
"""

import logging
import os
import random
import time

from dotenv import load_dotenv

import railtownai


def main():
    """Main example function with your Railtown API key."""

    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment variable
    api_key = os.getenv("RAILTOWN_API_KEY")

    if not api_key:
        print("Warning: RAILTOWN_API_KEY not found in environment variables.")
        print("Please set RAILTOWN_API_KEY in your .env file or environment variables.")
        print("Example .env file content:")
        print("RAILTOWN_API_KEY=your_actual_api_key_here")
        return

    # Initialize Railtown AI with your API key
    railtownai.init(api_key)

    print("Railtown AI Logging Example with Your API Key")
    print("=" * 50)

    # Example 1: Basic logging
    print("\n1. Basic Logging")
    print("-" * 20)

    run_id = "run_20241201_001"
    session_id = "session_abc123"

    logging.info("Application started successfully", extra={"run_id": run_id, "session_id": session_id})
    logging.warning(
        "High memory usage detected",
        extra={"memory_usage": "87%", "timestamp": time.time(), "run_id": run_id, "session_id": session_id},
    )
    logging.error(
        "Database connection timeout",
        extra={"db_host": "localhost", "error_code": 408, "run_id": run_id, "session_id": session_id},
    )

    # Example 2: Exception logging with stack traces
    print("\n2. Exception Logging")
    print("-" * 20)

    try:
        # Simulate a division by zero error
        result = 1 / 0  # noqa: F841
    except Exception:
        logging.exception("Division by zero error occurred during calculation")

    # Example 3: Breadcrumbs for user journey tracking
    print("\n3. User Journey with Breadcrumbs")
    print("-" * 20)

    # Clear any existing breadcrumbs
    railtownai.clear_breadcrumbs()

    # Simulate a user login flow
    railtownai.add_breadcrumb("User navigated to login page", category="ui", level="info")
    railtownai.add_breadcrumb("User entered email address", category="user_input", level="info")
    railtownai.add_breadcrumb("Validating user credentials", category="auth", level="info")
    railtownai.add_breadcrumb(
        "Database query executed",
        category="database",
        level="info",
        data={"query": "SELECT * FROM users WHERE email = ?", "duration_ms": 23},
    )

    # Simulate an authentication error
    try:
        raise ValueError("Invalid email or password")
    except Exception:
        logging.exception(
            "Authentication failed",
            extra={"user_email": "test@example.com", "attempt_count": 1, "run_id": run_id, "session_id": session_id},
        )

    # Example 4: E-commerce flow simulation
    print("\n4. E-commerce Flow Simulation")
    print("-" * 20)

    # Clear breadcrumbs for new flow
    railtownai.clear_breadcrumbs()

    # Simulate shopping cart operations
    railtownai.add_breadcrumb("User added item to cart", category="cart", data={"item_id": "prod_123", "quantity": 2})
    railtownai.add_breadcrumb("User applied discount code", category="cart", data={"discount_code": "SAVE20"})
    railtownai.add_breadcrumb(
        "Payment processing started", category="payment", data={"amount": 149.99, "currency": "USD"}
    )

    # Simulate payment processing
    logger = logging.getLogger("ecommerce.payment")
    logger.info(
        "Payment processed successfully",
        extra={
            "transaction_id": "txn_789",
            "payment_method": "credit_card",
            "run_id": run_id,
            "session_id": session_id,
        },
    )

    # Example 5: Error simulation with context
    print("\n5. Error Simulation with Context")
    print("-" * 20)

    railtownai.clear_breadcrumbs()

    # Add context breadcrumbs
    railtownai.add_breadcrumb("API request started", category="api", data={"endpoint": "/api/users", "method": "POST"})
    railtownai.add_breadcrumb("Database connection established", category="database")
    railtownai.add_breadcrumb("User validation passed", category="validation")

    # Simulate a complex error
    try:
        # Simulate a file processing error
        with open("nonexistent_file.txt") as f:
            content = f.read()  # noqa: F841
    except FileNotFoundError:
        logging.error(
            "File processing failed",
            extra={
                "file_path": "nonexistent_file.txt",
                "operation": "read",
                "user_id": "user_456",
                "run_id": run_id,
                "session_id": session_id,
            },
        )

    # Example 6: Performance monitoring
    print("\n6. Performance Monitoring")
    print("-" * 20)

    railtownai.clear_breadcrumbs()

    # Simulate a slow operation
    start_time = time.time()
    railtownai.add_breadcrumb("Database query started", category="performance")

    # Simulate some work
    time.sleep(0.1)

    duration = (time.time() - start_time) * 1000  # Convert to milliseconds
    railtownai.add_breadcrumb(
        "Database query completed",
        category="performance",
        data={"duration_ms": round(duration, 2), "rows_returned": 150},
    )

    if duration > 50:  # If query took more than 50ms
        logging.warning(
            "Slow database query detected",
            extra={
                "duration_ms": round(duration, 2),
                "threshold_ms": 50,
                "query_type": "SELECT",
                "run_id": run_id,
                "session_id": session_id,
            },
        )

    # Example 7: Random error simulation
    print("\n7. Random Error Simulation")
    print("-" * 20)

    railtownai.clear_breadcrumbs()

    # Simulate different types of errors randomly
    error_types = [
        ("ValueError", "Invalid input parameter"),
        ("ConnectionError", "Network connection lost"),
        ("TimeoutError", "Request timed out"),
        ("PermissionError", "Access denied"),
        ("KeyError", "Missing configuration key"),
    ]

    for i in range(3):
        railtownai.add_breadcrumb(f"Processing request {i + 1}", category="request")

        # 30% chance of error
        if random.random() < 0.3:
            error_type, error_msg = random.choice(error_types)
            try:
                raise Exception(f"{error_type}: {error_msg}")
            except Exception:
                logging.exception(
                    f"Error in request {i + 1}",
                    extra={
                        "request_id": f"req_{i + 1}",
                        "error_type": error_type,
                        "run_id": run_id,
                        "session_id": session_id,
                    },
                )
        else:
            logging.info(
                f"Request {i + 1} completed successfully",
                extra={"request_id": f"req_{i + 1}", "run_id": run_id, "session_id": session_id},
            )

    # Example 8: Simple logging.info with extra attribute
    print("\n8. Simple Logging with Extra Attribute")
    print("-" * 20)

    railtownai.clear_breadcrumbs()

    # Simple info logging with extra data
    logging.info(
        "User profile updated",
        extra={
            "user_id": "user_123",
            "profile_field": "email",
            "old_value": "old@example.com",
            "new_value": "new@example.com",
            "run_id": run_id,
            "session_id": session_id,
        },
    )

    # Another simple example with different extra data
    logging.info(
        "API endpoint called",
        extra={
            "endpoint": "/api/users/profile",
            "method": "PUT",
            "response_time_ms": 45,
            "status_code": 200,
            "run_id": run_id,
            "session_id": session_id,
        },
    )

    print("\nExample completed! Check your Railtown dashboard for the logs.")


if __name__ == "__main__":
    main()
