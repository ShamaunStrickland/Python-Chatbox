import mlflow
import mlflow.spark
import mlflow.pyfunc
from os import listdir


def read_pyspark_model(path):
    print(listdir("."))
    return mlflow.spark.load_model(".")
