from datetime import datetime
from io import StringIO
from typing import Any

def to_s3(
        site: str,
        type: str,
        day: datetime,
        source: str,
        csv_buffer: StringIO,
        bucket: Any) -> None:

    key = f"{site}/{type}/{day.year}/{day.strftime("%Y%m%d")}_{source}.csv"
    bucket.put_object(
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType='application/csv')
