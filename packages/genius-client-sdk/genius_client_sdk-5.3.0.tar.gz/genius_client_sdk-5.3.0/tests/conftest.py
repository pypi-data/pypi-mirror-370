import os


SDK_MEMORY_LIMIT = (
    os.getenv("SDK_MEMORY_LIMIT") or 1024 * 14
)  # 14 GB (current limit on remote agent)
SDK_REQUEST_TIMEOUT = os.getenv("SDK_REQUEST_TIMEOUT") or 20 * 60  # seconds
TEST_LOOP_COUNT = os.getenv("TEST_LOOP_COUNT") or 50  # repeat tests
