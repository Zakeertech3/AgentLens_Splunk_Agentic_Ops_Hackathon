from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentLensConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    splunk_hec_url: str = "http://localhost:8088/services/collector"
    splunk_hec_token: str = ""
    splunk_index: str = "agentlens"
    splunk_sourcetype: str = "agentlens:event"
    service_name: str = "agentlens"
    enabled: bool = True
    debug: bool = False


@lru_cache(maxsize=1)
def get_config() -> AgentLensConfig:
    return AgentLensConfig()
