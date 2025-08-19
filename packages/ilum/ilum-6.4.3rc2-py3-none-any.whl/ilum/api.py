from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class IlumJob(ABC):
    """
    ilum interactive job interface representing one result calculation
    """

    @abstractmethod
    def run(self, spark: SparkSession, config: dict) -> str:
        """
        run method used to interact with long living spark job
        :param spark configured spark session to be shared between single calculations
        :param config configuration to be applied for a single calculation
        :return string representation of produced result (user should care about serialization), or None if missing
        """
        pass
