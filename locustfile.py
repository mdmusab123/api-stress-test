import random
import string
import logging
from locust import HttpUser, task, between, events, tag

# -----------------------------------------------------------------
# LOCUST EVENT HOOKS (Advanced Logging)
# -----------------------------------------------------------------
@events.request.add_listener
def log_request_failures(request_type, name, response_time, response_length, exception, context, **kwargs):
    """
    Fires after every request. If there's an exception, it logs detailed 
    information to the console. Great for debugging server crashes.
    """
    if exception:
        logging.error(f"Request Failed: {request_type} {name} - Time: {response_time}ms - Error: {exception}")

# -----------------------------------------------------------------
# LOCUST WEB UI CONFIGURATION
# -----------------------------------------------------------------
@events.init_command_line_parser.add_listener
def _(parser):
    """
    Adds custom input fields to the Locust Web UI for advanced configuration.
    """
    # Authentication
    parser.add_argument("--api-key", type=str, env_var="API_KEY", default="", 
                        help="Secret API Key (X-API-KEY)", is_secret=True)
    
    # Endpoints
    parser.add_argument("--endpoint-primary", type=str, default="/api/v1/primary-post", help="Path for heavy POST")
    parser.add_argument("--endpoint-secondary", type=str, default="/api/v1/secondary-get", help="Path for GET list")
    parser.add_argument("--endpoint-tertiary", type=str, default="/api/v1/tertiary-post", help="Path for infrequent POST")
    
    # Advanced Settings
    parser.add_argument("--min-wait", type=float, default=1.0, help="Minimum wait time between tasks (seconds)")
    parser.add_argument("--max-wait", type=float, default=3.0, help="Maximum wait time between tasks (seconds)")
    parser.add_argument("--payload-size", choices=["small", "medium", "large"], default="small", 
                        help="Simulate different data payload sizes")

# -----------------------------------------------------------------
# LOAD TEST USER BEHAVIOR
# -----------------------------------------------------------------
class SaaSLoadTester(HttpUser):
    """
    Advanced API Load Testing Class.
    Includes dynamic pacing, payload generation, and tagged tasks.
    """
    
    def wait_time(self):
        """
        Dynamically calculates wait time based on user inputs from the Web UI.
        Overrides the standard `wait_time = between(1, 3)` static assignment.
        """
        min_w = self.environment.parsed_options.min_wait
        max_w = self.environment.parsed_options.max_wait
        return random.uniform(min_w, max_w)

    def on_start(self):
        """
        Lifecycle hook: Runs once per simulated user when they spawn.
        """
        api_key = self.environment.parsed_options.api_key
        
        # Set up a persistent session with required headers
        self.client.headers.update({
            "X-API-KEY": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Locust-Advanced-LoadTester/1.0"
        })

    def _generate_dynamic_payload(self):
        """
        Helper method to generate payloads of varying sizes based on UI config.
        Tests how the server handles parsing larger JSON objects.
        """
        size = self.environment.parsed_options.payload_size
        base_payload = {
            "search_key": f"test_{random.randint(1, 100000)}",
            "timestamp": random.randint(1600000000, 1700000000)
        }

        if size == "medium":
            # Add ~1KB of random text
            base_payload["metadata"] = ''.join(random.choices(string.ascii_letters, k=1024))
        elif size == "large":
            # Add ~10KB of random text
            base_payload["metadata"] = ''.join(random.choices(string.ascii_letters, k=10240))
            base_payload["bulk_items"] = [random.randint(1, 100) for _ in range(500)]

        return base_payload

    @tag('core', 'post', 'write')
    @task(5)
    def test_primary_post_endpoint(self):
        """
        Simulates heavy POST traffic.
        Tags: core, post, write
        Weight: 5
        """
        endpoint = self.environment.parsed_options.endpoint_primary
        payload = self._generate_dynamic_payload()

        with self.client.post(endpoint, json=payload, catch_response=True, name="Primary POST") as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 404:
                response.success()  # 404 is a valid response for random IDs, not a server crash
            elif response.status_code == 401:
                response.failure(f"Unauthorized (401). Check API Key.")
            elif response.status_code == 422:
                response.failure(f"Validation Error (422). Payload rejected.")
            elif response.elapsed.total_seconds() > 10.0:
                # Custom failure: Consider anything taking longer than 10 seconds a failure
                response.failure("Timeout SLA Breached (>10s)")
            else:
                response.failure(f"Unexpected Error: {response.status_code}")

    @tag('core', 'get', 'read')
    @task(3)
    def test_secondary_get_endpoint(self):
        """
        Simulates moderate GET traffic.
        Tags: core, get, read
        Weight: 3
        """
        endpoint = self.environment.parsed_options.endpoint_secondary
        
        # Add random query params to bypass CDN/Edge caching
        cache_buster = f"?cb={random.randint(1, 9999999)}"
        
        with self.client.get(endpoint + cache_buster, catch_response=True, name="Secondary GET") as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized")
            else:
                response.failure(f"Unexpected Error: {response.status_code}")

    @tag('edge', 'post')
    @task(1)
    def test_tertiary_post_endpoint(self):
        """
        Simulates infrequent, complex actions.
        Tags: edge, post
        Weight: 1
        """
        endpoint = self.environment.parsed_options.endpoint_tertiary
        payload = {
            "title": f"Automated Request #{random.randint(1000, 9999)}",
            "description": "Load testing payload data.",
            "type": random.choice(["type_a", "type_b", "type_c"]),
            "priority": random.choice([1, 2, 3, 4, 5])
        }

        with self.client.post(endpoint, json=payload, catch_response=True, name="Tertiary POST") as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Submission Failed: {response.status_code}")

# --- Instructions for GitHub Readme ---
# 1. Install Locust: `pip install locust`
# 2. Run the UI script: `locust -f locustfile.py`
# 3. Open http://localhost:8089 in your browser.
# 
# Advanced CLI Commands:
# Run only GET requests: locust -f locustfile.py --tags read
# Run with massive payloads: locust -f locustfile.py --payload-size large