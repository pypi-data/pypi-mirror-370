
import argparse
import json
import os
from pyspark.sql import SparkSession
from anonyspark.masking import (
    mask_email_udf, mask_name_udf, mask_date_udf,
    mask_ssn_udf, mask_itin_udf, mask_phone_udf
)

def apply_masking(df, schema):
    """
    Apply masking UDFs based on schema definitions.
    """
    for column, dtype in schema.items():
        if dtype == "email":
            df = df.withColumn(f"masked_{column}", mask_email_udf(df[column]))
        elif dtype == "name":
            df = df.withColumn(f"masked_{column}", mask_name_udf(df[column]))
        elif dtype == "dob":
            df = df.withColumn(f"masked_{column}", mask_date_udf(df[column]))
        elif dtype == "ssn":
            df = df.withColumn(f"masked_{column}", mask_ssn_udf(df[column]))
        elif dtype == "itin":
            df = df.withColumn(f"masked_{column}", mask_itin_udf(df[column]))
        elif dtype == "phone":
            df = df.withColumn(f"masked_{column}", mask_phone_udf(df[column]))
    return df

def main():
    parser = argparse.ArgumentParser(description="AnonySpark CLI for masking sensitive data.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Directory to save masked output')
    parser.add_argument('--schema', type=str, required=True, help='Path to masking schema JSON file')
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Start Spark
    spark = SparkSession.builder.master("local[*]").appName("AnonysparkCLI").getOrCreate()

    # Load data and schema
    df = spark.read.csv(args.input, header=True)
    with open(args.schema, 'r') as f:
        schema = json.load(f)

    # Apply masking
    masked_df = apply_masking(df, schema)

    # Save to output directory
    masked_df.write.mode("overwrite").csv(args.output, header=True)

    print(f"Masked file written to: {args.output}")

if __name__ == "__main__":
    main()
