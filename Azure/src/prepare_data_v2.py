import os
import argparse
import logging
import mlflow
from io import StringIO
import pandas as pd
from azureml.fsspec import AzureMachineLearningFileSystem

# from tqdm.autonotebook import tqdm


def read_parqut_from_azure(path, partition=None):
    # create the filesystem

    # append csv files in folder to a list
    dflist = []
    if partition is not None:
        path = path + partition
    # At the time I developed this code I couldn't find any SDK V2 version to do this
    fs = AzureMachineLearningFileSystem(path)
    for path in fs.ls():
        with fs.open(path) as f:
            dflist.append(pd.read_parquet(f))

    # # concatenate data frames
    df = pd.concat(dflist)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shipment", type=str, help="path to input shipment data")
    parser.add_argument("--promotion", type=str, help="path to input promotion data")
    parser.add_argument("--holidays", type=str, help="path to input holidays data")
    parser.add_argument("--product_hierarchy", type=str)
    parser.add_argument("--category", type=int)

    parser.add_argument("--generation_week", type=str, help="generation_week as string")
    parser.add_argument(
        "--period",
        type=str,
        help="period granularity is week and month",
        required=False,
        default="W",
    )
    parser.add_argument("--train_data", type=str, help="path to train data")
    parser.add_argument("--pred_data", type=str, help="path to pred/test data")

    args = parser.parse_args()
    mlflow.start_run()
    mlflow.log_text(args.shipment, "text_logs")
    # define the URI - update <> placeholders

    # df = read_parqut_from_azure(args.shipment, "Item.[L6]=227")
    # mlflow.log_metric("file shape", df.shape[0])

    mlflow.end_run()


if __name__ == "__main__":
    main()
