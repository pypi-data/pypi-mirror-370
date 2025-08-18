# tests/test_schema_masking.py

import sys
import os

sys.path.append("/content/anonyspark")

from pyspark.sql import SparkSession
from anonyspark.utils import apply_masking

def test_schema_masking():
    spark = SparkSession.builder.master("local[1]").appName("Test").getOrCreate()

    df = spark.createDataFrame([{
        "email": "john@example.com",
        "name": "John",
        "dob": "1991-08-14",
        "ssn": "123-45-6789",
        "itin": "912-73-1234",
        "phone": "123-456-7890"
    }])

    schema = {
        "email": "email",
        "name": "name",
        "dob": "dob",
        "ssn": "ssn",
        "itin": "itin",
        "phone": "phone"
    }

    masked_df = apply_masking(df, schema)
    result = masked_df.collect()[0].asDict()

    assert result["masked_email"] == "***@example.com"
    assert result["masked_name"] == "J***"
    assert result["masked_dob"] == "***-**-14"
    assert result["masked_ssn"] == "***-**-6789"
    assert result["masked_itin"] == "***-**-1234"
    assert result["masked_phone"] == "***-***-7890"
