# lf_algorithm/__init__.py
import logging

# Add NullHandler to prevent "No handler could be found" warnings
# This is the only logging configuration the library should do
logging.getLogger(__name__).addHandler(logging.NullHandler())

from .framework_agent import FrameworkAgent
from .utils import write_lineage_log
from .utils.file_utils import dump_json_record, read_json_records, clear_json_file, get_file_stats
from .utils.tracers import LogTracer, log_trace_id
from .models.models import AgentResult
from .plugins.sql_lineage_agent.lineage_agent import SqlLineageAgent, create_sql_lineage_agent, get_plugin_info as get_sql_plugin_info
from .plugins.python_lineage_agent.lineage_agent import PythonLineageAgent, create_python_lineage_agent, get_plugin_info as get_python_plugin_info
from .plugins.airflow_lineage_agent.lineage_agent import AirflowLineageAgent, create_airflow_lineage_agent, get_plugin_info as get_airflow_plugin_info
from .plugins.java_lineage_agent.lineage_agent import JavaLineageAgent, create_java_lineage_agent, get_plugin_info as get_java_plugin_info
from .plugins.spark_lineage_agent.lineage_agent import SparkLineageAgent, create_spark_lineage_agent, get_plugin_info as get_spark_plugin_info

__version__ = "0.1.0"

__all__ = [
    'FrameworkAgent',
    'AgentResult',
    'write_lineage_log',
    'dump_json_record',
    'read_json_records',
    'clear_json_file',
    'get_file_stats',
    'LogTracer',
    'log_trace_id',
    'SqlLineageAgent',
    'create_sql_lineage_agent',
    'get_sql_plugin_info',
    'PythonLineageAgent',
    'create_python_lineage_agent',
    'get_python_plugin_info',
    'AirflowLineageAgent',
    'create_airflow_lineage_agent',
    'get_airflow_plugin_info',
    'JavaLineageAgent',
    'create_java_lineage_agent',
    'get_java_plugin_info',
    'SparkLineageAgent',
    'create_spark_lineage_agent',
    'get_spark_plugin_info'
] 