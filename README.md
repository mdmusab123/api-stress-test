🚀 Advanced API Load Testing Suite (Locust)

Repository Description: An advanced, enterprise-ready Locust load testing suite designed to stress-test and benchmark APIs. It features zero-code UI configuration for endpoints and API keys, adjustable payload sizes to test bandwidth limits, dynamic wait times, and targeted task execution via command-line tags.

This repository provides a highly customizable load testing script built on top of Locust. It is designed to evaluate server performance, database bottlenecking, and API rate limits without needing to hardcode environment-specific variables.

✨ Key Features

Zero-Code UI Configuration: Set your target Host, secret API Keys, and target endpoints directly from the Locust Web UI.

Dynamic Wait Times: Simulate casual browsing or aggressive traffic spikes by adjusting min/max wait times on the fly.

Payload Sizing: Test your server's JSON parsing and bandwidth limits by toggling between small, medium, and large request payloads.

Task Tagging: Isolate and test specific infrastructure (e.g., only run GET requests to test read-replicas) using CLI tags.

Advanced Event Logging: Custom hooks capture detailed tracebacks for failed requests, making debugging server crashes in headless mode much easier.

🛠️ Prerequisites

Before you begin, ensure you have the following installed on your local machine:

Python 3.8 or higher

pip (Python package installer)

📦 Installation

Clone the repository:

git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/mdmusab123/api-stress-test)
cd api-stress-test


Install Locust:
It is recommended to use a virtual environment, but you can install Locust globally:

pip install locust


🚀 Usage Guide

Method 1: Interactive Web UI (Recommended)

The easiest way to run tests is via the built-in web interface.

Start the Locust server:

locust -f locustfile.py


Open your web browser and navigate to: http://localhost:8089

Fill out the configuration form:

Number of users: Total concurrent users to simulate.

Spawn rate: How many users to add per second.

Host: The base URL of your application (e.g., https://api.example.com).

Custom Parameters: Enter your secret API key, define your endpoints, and choose your payload size.

Click Start Swarming.

Method 2: Headless Mode (CLI / CI/CD pipeline)

For automated testing or running on remote servers without a GUI, use headless mode. You can pass all UI parameters via environment variables or CLI arguments.

locust -f locustfile.py \
  --headless \
  -u 500 \
  -r 50 \
  --run-time 5m \
  --host [https://api.example.com](https://api.example.com) \
  --api-key YOUR_SECRET_KEY \
  --payload-size large


🎛️ Advanced Configuration Breakdown

Endpoint Weights

By default, the script distributes traffic to simulate real-world usage:

Primary POST (@task(5)): Executes 5x more often. Represents core app interactions.

Secondary GET (@task(3)): Executes 3x more often. Represents data fetching/polling.

Tertiary POST (@task(1)): Executes rarely. Represents actions like bug reporting or profile updates.

Task Tagging

You can restrict the test to only run specific functions using the --tags argument.

Available tags in this script: core, edge, read, write, get, post.

Example: Run only GET requests to test database read performance:

locust -f locustfile.py --tags read


📊 Analyzing Results

While the test is running, Locust provides real-time statistics:

95%ile (ms): The most important metric. If this number spikes above 1000-2000ms, your server is beginning to bottleneck.

Failures: Look at the "Failures" tab to see if your server is returning 502 Bad Gateway (crashes), 504 Timeout (queue full), or standard business logic errors.

Note: The script is designed to treat expected business errors (like a 404 Not Found for a randomly generated user ID) as a successful server response so it doesn't skew your crash statistics.

⚠️ Disclaimer

Do NOT use this tool against servers you do not own or do not have explicit permission to test. High-concurrency load testing mimics the behavior of a Distributed Denial of Service (DDoS) attack and can take down production environments, incur high cloud-computing costs, and trigger automated security blocks.
