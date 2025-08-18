__all__ = [
    "mask_email_udf", "mask_name_udf", "mask_date_udf",
    "mask_ssn_udf", "mask_itin_udf", "mask_phone_udf"
]

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import re
from datetime import datetime

# Masking functions
def mask_email(value):
    if value and "@" in value:
        user, domain = value.split("@")
        return "***@" + domain
    return None

def mask_name(value):
    if value:
        return value[0] + "***"
    return None

def mask_date(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("***-**-%d")
    except:
        return None

def mask_ssn(value):
    if value and re.match(r"\d{3}-\d{2}-\d{4}", value):
        return "***-**-" + value[-4:]
    return None

def mask_itin(value):
    if value and re.match(r"9\d{2}-7\d-\d{4}", value):
        return "***-**-" + value[-4:]
    return None

def mask_phone(value):
    if value and re.match(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", value):
        return "***-***-" + value[-4:]
    return None

# UDFs for Spark
mask_email_udf = udf(mask_email, StringType())
mask_name_udf = udf(mask_name, StringType())
mask_date_udf = udf(mask_date, StringType())
mask_ssn_udf = udf(mask_ssn, StringType())
mask_itin_udf = udf(mask_itin, StringType())
mask_phone_udf = udf(mask_phone, StringType())

