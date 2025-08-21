from dotenv import load_dotenv
load_dotenv()

import os
from  skalds.config._enum import LogLevelEnum, SkaldEnvEnum, SkaldModeEnum, SystemControllerModeEnum, DispatcherStrategyEnum
import uuid


def _bool(input):
    input = str(input)
    if input.lower() in ['true', '1', 'yes', 'y']:
        return True
    elif input.lower() in ['false', '0', 'no', 'n']:
        return False
    else:
        return False
    
class SystemConfig:
    SKALD_ID : str = os.getenv("SKALD_ID", f"skalds-{str(uuid.uuid4())[:5]}") 
    SKALD_ENV: SkaldEnvEnum = os.getenv("SKALD_ENV", SkaldEnvEnum.DEV)  # dev / production 
    SKALD_MODE: SkaldModeEnum = os.getenv("SKALD_MODE", SkaldModeEnum.NODE)  # edge / node
    LOG_LEVEL: LogLevelEnum = os.getenv("LOG_LEVEL", LogLevelEnum.INFO) # TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
    LOG_PATH: str = os.getenv("LOG_PATH", "logs")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "3 days")
    LOG_ROTATION_MB: str = os.getenv("LOG_ROTATION_MB", "10")
    LOG_SPLIT_WITH_WORKER_ID: bool = _bool(os.getenv("LOG_SPLIT_WITH_WORKER_ID", "false"))

    # TaskWorker YAML Config
    YAML_FILE: str = os.getenv("YAML_FILE", "")

    # Redis Config
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_SYNC_PERIOD: int = int(os.getenv("REDIS_SYNC_PERIOD", 3))
    REDIS_KEY_TTL: int = int(os.getenv("REDIS_KEY_TTL", 3600))

    # Kafka Config
    KAFKA_HOST: str = os.getenv("KAFKA_HOST", "")
    KAFKA_PORT: int = int(os.getenv("KAFKA_PORT", 9092))
    KAFKA_USERNAME: str = os.getenv("KAFKA_USERNAME", "")
    KAFKA_PASSWORD: str = os.getenv("KAFKA_PASSWORD", "")
    KAFKA_TOPIC_PARTITIONS: int = int(os.getenv("KAFKA_TOPIC_PARTITIONS", 6))
    KAFKA_REPLICATION_FACTOR: int = int(os.getenv("KAFKA_REPLICATION_FACTOR", 3))

    # Mongo Config
    MONGO_HOST: str = os.getenv("MONGO_HOST", "")
    DB_NAME: str = os.getenv("DB_NAME", "skalds")

    TASK_WORKER_RETRY: int = int(os.getenv("TASK_WORKER_RETRY", -1))

    # SystemController Configuration
    SYSTEM_CONTROLLER_MODE: SystemControllerModeEnum = os.getenv("SYSTEM_CONTROLLER_MODE", SystemControllerModeEnum.CONTROLLER)
    SYSTEM_CONTROLLER_HOST: str = os.getenv("SYSTEM_CONTROLLER_HOST", "0.0.0.0")
    SYSTEM_CONTROLLER_PORT: int = int(os.getenv("SYSTEM_CONTROLLER_PORT", 8000))

    # Monitor Configuration  
    MONITOR_SKALD_INTERVAL: int = int(os.getenv("MONITOR_SKALD_INTERVAL", 5))
    MONITOR_TASK_INTERVAL: int = int(os.getenv("MONITOR_TASK_INTERVAL", 3))
    MONITOR_HEARTBEAT_TIMEOUT: int = int(os.getenv("MONITOR_HEARTBEAT_TIMEOUT", 5))

    # Dispatcher Configuration
    DISPATCHER_INTERVAL: int = int(os.getenv("DISPATCHER_INTERVAL", 5))
    DISPATCHER_STRATEGY: DispatcherStrategyEnum = os.getenv("DISPATCHER_STRATEGY", DispatcherStrategyEnum.LEAST_TASKS)