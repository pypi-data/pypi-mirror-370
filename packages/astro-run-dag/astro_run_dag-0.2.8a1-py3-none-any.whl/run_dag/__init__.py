import logging

airflow_logger = logging.getLogger("airflow")
airflow_logger.setLevel(logging.CRITICAL)
airflow_logger.propagate = False
