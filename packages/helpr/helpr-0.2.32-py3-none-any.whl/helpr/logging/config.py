import structlog

class LoggingConfig:


    processors=[
                structlog.processors.TimeStamper(fmt="iso",key="timestamp"),
                structlog.processors.format_exc_info,
                structlog.stdlib.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
    ]
    context_class=dict
    logger_factory=structlog.stdlib.LoggerFactory()