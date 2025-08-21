"""
Test file demonstrating the new Railtown AI logging handler functionality.
"""

import logging

import railtownai


def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")

    # Initialize Railtown AI (use a dummy key for testing)
    railtownai.init("dummy_key_for_testing")

    # Test different log levels
    logging.info("This is an info message")
    logging.warning("This is a warning message")
    logging.error("This is an error message")

    # Test logging with extra data
    logging.info("User action", extra={"user_id": 123, "action": "login"})
    logging.error("Database error", extra={"db_host": "localhost", "error_code": 500})


def test_breadcrumbs():
    """Test breadcrumb functionality."""
    print("Testing breadcrumbs...")

    # Clear any existing breadcrumbs
    railtownai.clear_breadcrumbs()

    # Add some breadcrumbs
    railtownai.add_breadcrumb("User clicked login button", category="ui")
    railtownai.add_breadcrumb("Validating credentials", category="auth")
    railtownai.add_breadcrumb(
        "Database query executed", category="database", data={"query": "SELECT * FROM users", "duration_ms": 45}
    )

    # Log an error - it should include the breadcrumbs
    logging.error("Login failed", extra={"reason": "invalid_credentials"})

    # Add more breadcrumbs
    railtownai.add_breadcrumb("Retrying login", category="auth")
    railtownai.add_breadcrumb("Second attempt failed", category="auth")

    # Log another error
    logging.error("Second login attempt failed")

    # Check breadcrumbs
    breadcrumbs = railtownai.get_breadcrumbs()
    print(f"Current breadcrumbs: {len(breadcrumbs)}")
    for i, crumb in enumerate(breadcrumbs):
        print(f"  {i + 1}. {crumb['message']} ({crumb['category']})")


def test_exception_logging():
    """Test exception logging with stack traces."""
    print("Testing exception logging...")

    def risky_function():
        """A function that might raise an exception."""
        return 1 / 0

    try:
        risky_function()
    except Exception:
        logging.exception("Exception in risky_function")


def test_custom_logger():
    """Test using a custom logger."""
    print("Testing custom logger...")

    # Create a custom logger
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    # Add a console handler for local output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Use the custom logger
    logger.info("Application started")
    logger.error("Something went wrong", extra={"component": "payment_processor"})


def test_breadcrumb_management():
    """Test breadcrumb management functions."""
    print("Testing breadcrumb management...")

    # Clear breadcrumbs
    railtownai.clear_breadcrumbs()

    # Add breadcrumbs with different levels
    railtownai.add_breadcrumb("User action", level="info", category="user")
    railtownai.add_breadcrumb("System warning", level="warning", category="system")
    railtownai.add_breadcrumb("Error occurred", level="error", category="error")

    # Get breadcrumbs
    breadcrumbs = railtownai.get_breadcrumbs()
    print(f"Breadcrumbs before clearing: {len(breadcrumbs)}")

    # Clear breadcrumbs
    railtownai.clear_breadcrumbs()
    breadcrumbs = railtownai.get_breadcrumbs()
    print(f"Breadcrumbs after clearing: {len(breadcrumbs)}")


if __name__ == "__main__":
    print("Railtown AI Logging Handler Test")
    print("=" * 40)

    # Note: These tests will fail to send to Railtown AI due to the dummy API key,
    # but they demonstrate the functionality and won't crash the application.

    test_basic_logging()
    print()

    test_breadcrumbs()
    print()

    test_exception_logging()
    print()

    test_custom_logger()
    print()

    test_breadcrumb_management()
    print()

    print("All tests completed!")
