import mlflow
import mlflow.spark
import mlflow.pyfunc
import site


# import nlp


def read_pyspark_model():
    print("Loading model from {}/nlp".format(site.getsitepackages()[0]))
    return mlflow.spark.load_model("{}/nlp".format(site.getsitepackages()[0]))


def read_pyfunc_model():
    print("Loading model from {}/nlp".format(site.getsitepackages()[0]))
    return mlflow.pyfunc.load_model("{}/nlp".format(site.getsitepackages()[0]))
#
# print(read_model())
# # from pyspark.sql import SparkSession
#
# # spark = SparkSession.builder.getOrCreate()
# mlflow.spark.load_model("/Users/ravi.teja/Work/nltkTransformer/nlp/")
# from platform import python_version
#
# print(python_version())
