from pyspark.sql.functions import col

def apply_masking(df, schema):
    """
    Apply masking UDFs to specified columns based on schema.
    Schema = { "original_col": "mask_type" }
    """
    from .masking import (
        mask_email_udf, mask_name_udf, mask_date_udf,
        mask_ssn_udf, mask_itin_udf, mask_phone_udf
    )

    masking_map = {
        "email": mask_email_udf,
        "name": mask_name_udf,
        "dob": mask_date_udf,
        "ssn": mask_ssn_udf,
        "itin": mask_itin_udf,
        "phone": mask_phone_udf,
    }

    for col_name, mask_type in schema.items():
        if mask_type in masking_map:
            df = df.withColumn(f"masked_{col_name}", masking_map[mask_type](col(col_name)))
    return df
