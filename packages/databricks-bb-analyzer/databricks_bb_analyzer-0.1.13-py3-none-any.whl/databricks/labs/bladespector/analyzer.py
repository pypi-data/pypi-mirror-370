import logging
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

logger = logging.getLogger(__name__)

_PLATFORM_TO_SOURCE_TECHNOLOGY = {
    "ABInitio": "ABINITIO",
    "ADF": "ADF",
    "Alteryx": "ALTERYX",
    "Athena": "SQL",
    "BigQuery": "SQL",
    "BODS" : "BODS",
    "Cloudera (Impala)": "SQL",
    "Datastage": "DATASTAGE",
    "Greenplum": "SQL",
    "Hive": "SQL",
    "IBM DB2": "SQL",
    "Informatica - Big Data Edition": "INFADEV",
    "Informatica Cloud": "INFACLOUD",
    "Informatica - PC": "INFA",
    "Netezza": "SQL",
    "Oozie": "OOZIE",
    "Oracle": "SQL",
    "Oracle Data Integrator": "ODI",
    "PentahoDI": "PENTAHO",
    "PIG": "PIG",
    "Presto": "SQL",
    "PySpark": "PYSPARK",
    "Redshift": "SQL",
    "SAPHANA - CalcViews": "HANA",
    "SAS": "SAS",
    "Snowflake": "SQL",
    "MS SQL Server": "SQL",
    "SPSS": "SPSS",
    "SQOOP": "SQOOP",
    "SSIS": "SSIS",
    "SSRS": "SSRS",
    "Synapse": "SQL",
    "Talend": "TALEND",
    "Teradata": "SQL",
    "Vertica": "SQL",
}


class Analyzer:

    @classmethod
    def supported_source_technologies(cls) -> list[str]:
        return list(_PLATFORM_TO_SOURCE_TECHNOLOGY.keys())

    @classmethod
    def analyze(cls, directory: Path, result: Path, platform: str, is_debug: bool = False):
        technology = _PLATFORM_TO_SOURCE_TECHNOLOGY.get(platform, None)
        if not technology:
            raise ValueError(f"Unsupported platform: {platform}")
        analyzer = Analyzer()
        analyzer._run_binary(directory, result, technology, is_debug)

    def __init__(self):
        self._binary = self._locate_binary()

    def _run_binary(self, directory: Path, result: Path, technology: str, is_debug):
        try:
            args = [
                str(self._binary),
                "-d",
                f"{directory}",
                "-r",
                f"{result}",
                "-t",
                technology
            ]
            if is_debug:
                args.append("-v")

            env = deepcopy(os.environ)
            env["UTF8_NOT_SUPPORTED"] = str(1)

            logger.debug(f"Running command: {' '.join(args)}")

            # Use context manager for subprocess.Popen
            # TODO: Handle stdout and stderr properly (async/threads) to avoid pipe buffer blocking.
            with subprocess.Popen(
                args,
                env=env,
                stdout=None,
                stderr=None,
                text=True,
                bufsize=1,
                universal_newlines=True
            ) as process:
                process.wait()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, args)

            return None
        # it is good practice to catch broad exceptions raised by launching a child process
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Analysis failed", exc_info=e)
            raise RuntimeError("Analysis failed") from e

    def _locate_binary(self) -> Path:
        if 'darwin' in sys.platform:
            tool = "MacOS/analyzer"
        elif 'win' in sys.platform:
            tool = "Windows/analyzer.exe"
        elif 'linux' in sys.platform:
            tool = "Linux/analyzer"
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        file_nm = Path(__file__).parent / "Analyzer" / tool
        logger.debug(f"Using underlying analyzer: ${file_nm}")
        return file_nm
