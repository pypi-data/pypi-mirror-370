# loguru-dagster

**loguru-dagster** is a lightweight utility package that bridges [Loguru](https://github.com/Delgan/loguru) with [Dagster](https://dagster.io/).  
It enables **colorized, contextual logging** inside Dagster pipelines with a single decorator.

## 🚀 Installation

```bash
pip install loguru-dagster
```

This will automatically install the required `loguru` and `dagster` dependencies.

## 📦 Import Path

```python
from loguru_dagster import dagster_context_sink, with_loguru_logger
```

## 🧪 Usage Example

1. Loguru Direct Logging
You can use Loguru directly inside a Dagster asset:

```python
import dagster as dg
from loguru import logger

@dg.asset
def test_loguru_html_log():
    """Verify that all levels appear correctly in Dagster UI"""
    logger.debug("==Debug== Loguru is working in Dagster!")
    logger.info("==Info== Loguru is working in Dagster!")
    logger.warning("==Warning== Loguru is working in Dagster!")
    logger.error("==!!Error!!== Loguru is working in Dagster!")
    return {"status": "done"}

defs = dg.Definitions(
    assets=[test_loguru_html_log]
)
```

![Loguru Direct Logging](./images/test_loguru_html_log.png)

2.Bridge Loguru to context.log with Decorator
To convert context.log calls into Loguru logs, use the decorator @with_loguru_logger from loguru_dagster:

```python
import dagster as dg
from loguru_dagster import with_loguru_logger

@dg.asset
@with_loguru_logger
def my_contexlog_callig_loguru(context: dg.AssetExecutionContext) -> None:
    context.log.debug("This is a context.log.debug message from my_contexlog_callig_loguru")
    context.log.info("This is an context.log.info message from my_contexlog_callig_loguru")
    context.log.warning("This is a context.log.warning message from my_contexlog_callig_loguru")
    context.log.error("This is an context.log.error message from my_contexlog_callig_loguru")
    context.log.critical("This is a context.log.critical message from my_contexlog_callig_loguru")

defs = dg.Definitions(
    assets=[my_contexlog_callig_loguru]
)
```

![Loguru Context Log Bridge](./images/my_contexlog_callig_loguru.png)

## 🔗 Repository

[https://github.com/albertfast/loguru-dagster](https://github.com/albertfast/loguru-dagster)
