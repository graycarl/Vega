import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError
from src.models.server_config import ServerConfig
from src.models.request_log import RequestLog
from src.models.usage_stats import UsageStats, BucketType

def test_server_config_valid():
    config = ServerConfig(
        name="OpenAI",
        url="https://api.openai.com/v1",
        api_key="sk-xxx",
        models=["gpt-4"],
        rpm_limit=100,
        tpm_limit=10000
    )
    assert config.name == "OpenAI"
    assert str(config.url) == "https://api.openai.com/v1"
    assert config.is_active is True

def test_server_config_invalid_url():
    with pytest.raises(ValidationError):
        ServerConfig(
            name="Test",
            url="http://insecure.com",
            api_key="key",
            models=["gpt-4"],
            rpm_limit=10,
            tpm_limit=100
        )

def test_server_config_limits():
    # Both 0 is invalid
    with pytest.raises(ValidationError):
        ServerConfig(
            name="Test",
            url="https://api.test.com",
            api_key="key",
            models=["gpt-4"],
            rpm_limit=0,
            tpm_limit=0
        )

def test_request_log_tokens():
    log = RequestLog(
        server_id=uuid4(),
        app_name="app1",
        model="gpt-4",
        prompt_tokens=10,
        completion_tokens=20,
        status_code=200,
        latency_ms=100
    )
    log.calculate_total_tokens()
    assert log.total_tokens == 30

def test_usage_stats_defaults():
    stats = UsageStats(
        server_id=uuid4(),
        app_name="app1",
        time_bucket="2025-11-23T10",
        bucket_type=BucketType.HOUR
    )
    assert stats.total_requests == 0
    assert stats.total_tokens == 0
