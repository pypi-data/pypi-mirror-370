# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_planktivore_media.py
# Description: Extracts data from CFE image meta data
import re
from datetime import datetime, timezone
from typing import Optional

import pytz

import pandas as pd
from pathlib import Path

from mbari_aidata.logger import info
from mbari_aidata.plugins.extractors.media_types import MediaType


def extract_media(media_path: Path, max_images: Optional[int] = None) -> pd.DataFrame:
    """Extracts Planktivore image meta data
    Examples:
        low_mag_cam-1713221040057971-92665779216-379-021-1178-1882-36-36_rawcolor.png
        high_mag_cam-1713221004871098-57486995160-7-002-992-512-32-28_rawcolor.png
        LRAH12_20240415T224601.945383Z_PTVR02LM_1598_128_2108_1476_0_112_452_0_rawcolor
        LRAH12_20240415T224357.652299Z_PTVR02HM_335_1_14_298_0_64_64_0_rawcolor.png
    """

    # Create a dataframe to store the combined data in the media_path column in sorted order
    images_df = pd.DataFrame()

    allowed_extensions = [".png", ".jpg"]
    images_df["media_path"] = [str(file) for file in media_path.rglob("*") if file.suffix.lower() in allowed_extensions]
    images_df.sort_values(by="media_path")
    if 0 < max_images < len(images_df):
        images_df = images_df.iloc[:max_images]

    pattern1 = re.compile(r'\d{8}T\d{6}\.\d+Z')
    pattern2 = re.compile(r'(high_mag_cam|low_mag_cam)-(\d{16})')

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    info(f"Found {len(images_df)} unique images")
    for index, row in images_df.iterrows():
        image_name = row["media_path"]
        matches = re.findall(pattern1, image_name)
        if matches:
            datetime_str = matches[0]
            dt = datetime.strptime(datetime_str, "%Y%m%dT%H%M%S.%fZ")
            dt_utc = pytz.utc.localize(dt)
            iso_datetime[index] = dt_utc

        matches = re.findall(pattern2, image_name)
        if matches:
            us_timestamp = int(matches[0][1])
            seconds = us_timestamp // 1_000_000
            microseconds = us_timestamp % 1_000_000
            dt_utc = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(microsecond=microseconds)
            iso_datetime[index] = dt_utc

    images_df["iso_datetime"] = iso_datetime
    images_df["media_type"] =  MediaType.IMAGE
    return images_df
