"""Tests for pytest markers (epic, story, title)."""

import pytest

from sdk_pytest_checkmate import add_data_report, soft_assert, step


class TestMarkers:
    """Test pytest markers functionality."""

    @pytest.mark.title("Custom test title")
    def test_title_marker(self):
        """Test that title marker works."""
        with step("Test title marker"):
            soft_assert(True, "Title marker test")

    @pytest.mark.epic("Test Epic")
    def test_epic_marker(self):
        """Test that epic marker works."""
        with step("Test epic marker"):
            soft_assert(True, "Epic marker test")

    @pytest.mark.story("Test Story")
    def test_story_marker(self):
        """Test that story marker works."""
        with step("Test story marker"):
            soft_assert(True, "Story marker test")

    @pytest.mark.epic("User Management")
    @pytest.mark.story("User Registration")
    @pytest.mark.title("User can register with valid data")
    def test_all_markers_combined(self):
        """Test combining all marker types."""
        with step("Setup user data"):
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }
            add_data_report(user_data, "User Registration Data")

        with step("Validate user data"):
            soft_assert(
                len(user_data["username"]) > 3, "Username should be long enough"
            )
            soft_assert("@" in user_data["email"], "Email should contain @")
            soft_assert(len(user_data["password"]) >= 8, "Password should be strong")

        with step("Register user"):
            # Simulate registration
            registration_result = {
                "success": True,
                "user_id": 12345,
                "message": "User registered successfully",
            }
            add_data_report(registration_result, "Registration Result")
            soft_assert(registration_result["success"], "Registration should succeed")

    @pytest.mark.epic("E-commerce")
    @pytest.mark.story("Shopping Cart")
    def test_shopping_cart_epic_story(self):
        """Test with e-commerce epic and shopping cart story."""
        with step("Add item to cart"):
            item = {"id": 1, "name": "Product 1", "price": 29.99}
            add_data_report(item, "Cart Item")
            soft_assert(item["price"] > 0, "Price should be positive")

        with step("Verify cart contents"):
            cart = {"items": [item], "total": 29.99}
            add_data_report(cart, "Cart Contents")
            soft_assert(len(cart["items"]) == 1, "Cart should have one item")

    @pytest.mark.epic("API Testing")
    @pytest.mark.story("Authentication API")
    @pytest.mark.title("API returns valid JWT token on successful login")
    def test_api_authentication_flow(self):
        """Test API authentication with all markers."""
        with step("Prepare login credentials"):
            credentials = {"username": "api_user", "password": "api_pass"}
            add_data_report(credentials, "Login Credentials")

        with step("Send login request"):
            # Simulate API response
            response = {
                "status_code": 200,
                "token": "jwt.token.here",
                "expires_in": 3600,
            }
            add_data_report(response, "Login Response")
            soft_assert(response["status_code"] == 200, "Should return 200 OK")
            soft_assert("token" in response, "Should include JWT token")

        with step("Validate token"):
            token = response["token"]
            soft_assert(len(token) > 10, "Token should be substantial length")
            soft_assert("." in token, "JWT should contain dots")

    # Test without any markers
    def test_no_markers(self):
        """Test without any special markers."""
        with step("Simple test step"):
            soft_assert(True, "This should pass")
            add_data_report({"no_markers": True}, "No Markers Test")

    @pytest.mark.epic("Data Processing")
    def test_only_epic_marker(self):
        """Test with only epic marker."""
        with step("Process data"):
            data = [1, 2, 3, 4, 5]
            processed = [x * 2 for x in data]
            add_data_report(
                {"original": data, "processed": processed}, "Data Processing"
            )
            soft_assert(len(processed) == len(data), "Processed length should match")

    @pytest.mark.story("Data Validation")
    def test_only_story_marker(self):
        """Test with only story marker (no epic)."""
        with step("Validate data format"):
            data = {"format": "json", "valid": True}
            add_data_report(data, "Validation Data")
            soft_assert(data["valid"], "Data should be valid")

    @pytest.mark.title("Very descriptive test title with multiple words")
    def test_long_title_marker(self):
        """Test with a longer, more descriptive title."""
        with step("Test long title handling"):
            soft_assert(True, "Long title test")

    @pytest.mark.epic("Performance Testing")
    @pytest.mark.story("Load Testing")
    @pytest.mark.title("System handles 100 concurrent users")
    def test_performance_scenario(self):
        """Test representing a performance testing scenario."""
        with step("Setup load test"):
            config = {"concurrent_users": 100, "duration": "5m", "ramp_up": "30s"}
            add_data_report(config, "Load Test Config")

        with step("Execute load test"):
            results = {
                "avg_response_time": 250,
                "max_response_time": 1200,
                "error_rate": 0.02,
                "throughput": 450,
            }
            add_data_report(results, "Load Test Results")

            soft_assert(
                results["avg_response_time"] < 500,
                "Avg response time should be under 500ms",
            )
            soft_assert(results["error_rate"] < 0.05, "Error rate should be under 5%")
            soft_assert(
                results["throughput"] > 400, "Throughput should be over 400 req/s"
            )
