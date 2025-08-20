import argparse
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        description="loguru-dagster: Bridge between Loguru and Dagster for enhanced logging capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"loguru-dagster {__version__}"
    )

    parser.add_argument(
        "--example",
        action="store_true",
        help="Print an example usage of loguru-dagster"
    )

    args = parser.parse_args()

    if args.example:
        print_example()
    else:
        parser.print_help()

def print_example():
    example = '''
# Example usage of loguru-dagster
#################################
1. Loguru Direct Logging
You can use Loguru directly inside a Dagster asset:
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

#################################
2.Bridge Loguru to context.log with Decorator
To convert context.log calls into Loguru logs, use the decorator @with_loguru_logger from loguru_dagster:

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
#########################################
'''
    print(example)

if __name__ == "__main__":
    main()
