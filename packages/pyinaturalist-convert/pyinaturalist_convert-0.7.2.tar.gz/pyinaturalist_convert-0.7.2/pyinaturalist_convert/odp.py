"""Download and convert observation, taxon, photo, and user metadata from
`inaturalist-open-data <https://github.com/inaturalist/inaturalist-open-data>`_.

**Extra dependencies**: ``boto3``

**Example**: Download everything and load into a SQLite database::

    >>> from pyinaturalist_convert import load_odp_tables
    >>> load_odp_tables()

**Main function:**

.. autosummary::
    :nosignatures:

    load_odp_tables

**Helper functions:**

.. autosummary::
    :nosignatures:

    download_odp_metadata
    load_odp_taxa
    load_odp_photos
    load_odp_users
"""

from pathlib import Path
from typing import Optional

from .constants import (
    DATA_DIR,
    DB_PATH,
    ODP_ARCHIVE_NAME,
    ODP_BUCKET_NAME,
    ODP_METADATA_KEY,
    ODP_OBS_CSV,
    ODP_PHOTO_CSV,
    ODP_TAXON_CSV,
    ODP_USER_CSV,
    PathOrStr,
)
from .db import create_tables
from .download import CSVProgress, check_download, download_s3_file, untar_progress
from .sqlite import load_table, vacuum_analyze

OBS_COLUMN_MAP = {
    'latitude': 'latitude',
    'longitude': 'longitude',
    'observation_uuid': 'uuid',
    'observed_on': 'observed_on',
    'observer_id': 'user_id',
    'positional_accuracy': 'positional_accuracy',
    'quality_grade': 'quality_grade',
    'taxon_id': 'taxon_id',
}
TAXON_COLUMN_MAP = {'taxon_id': 'id', 'ancestry': 'ancestor_ids', 'rank': 'rank', 'name': 'name'}
PHOTO_COLUMN_MAP = {
    'photo_id': 'id',
    'observation_uuid': 'observation_uuid',
    'observer_id': 'user_id',
    'license': 'license',
}
USER_COLUMN_MAP = {'observer_id': 'id', 'login': 'login', 'name': 'name'}


def load_odp_tables(dest_dir: PathOrStr = DATA_DIR, db_path: PathOrStr = DB_PATH):
    """Download iNaturalist Open Data metadata and load into a SQLite database"""
    download_odp_metadata(dest_dir)
    csv_dir = Path(dest_dir) / 'inaturalist-open-data'
    csv_files = [csv_dir / f'{f}.csv' for f in ['observations', 'photos', 'taxa', 'observers']]
    progress = CSVProgress(*csv_files)
    with progress:
        load_odp_observations(csv_dir / 'observations.csv', db_path, progress)
        load_odp_photos(csv_dir / 'photos.csv', db_path, progress)
        load_odp_taxa(csv_dir / 'taxa.csv', db_path, progress)
        load_odp_users(csv_dir / 'observers.csv', db_path, progress)
    vacuum_analyze(['observation', 'photo', 'taxon', 'user'], db_path, show_spinner=True)


def download_odp_metadata(dest_dir: PathOrStr = DATA_DIR):
    """Download and extract the iNaturalist Open Data metadata archive. Reuses local data if it
    already exists and is up to date.

    Args:
        dest_dir: Optional directory to download to
    """
    dest_dir = Path(dest_dir).expanduser()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / ODP_ARCHIVE_NAME

    # Skip download if we're already up to date
    if check_download(dest_file, bucket=ODP_BUCKET_NAME, key=ODP_METADATA_KEY, release_interval=31):
        return

    # Otherwise, download and extract files
    download_s3_file(ODP_BUCKET_NAME, ODP_METADATA_KEY, dest_file)
    untar_progress(dest_file, dest_dir / 'inaturalist-open-data')


def load_odp_observations(
    csv_path: PathOrStr = ODP_OBS_CSV,
    db_path: PathOrStr = DB_PATH,
    progress: Optional[CSVProgress] = None,
):
    """Create or update an observation SQLite table from the Open Data archive"""
    create_tables(db_path)
    progress = progress or CSVProgress(csv_path)
    with progress:
        load_table(
            csv_path, db_path, 'observation', OBS_COLUMN_MAP, delimiter='\t', progress=progress
        )


def load_odp_photos(
    csv_path: PathOrStr = ODP_PHOTO_CSV,
    db_path: PathOrStr = DB_PATH,
    progress: Optional[CSVProgress] = None,
):
    """Create or update a photo metadata SQLite table from the Open Data archive."""
    create_tables(db_path)
    progress = progress or CSVProgress(csv_path)
    with progress:
        load_table(csv_path, db_path, 'photo', PHOTO_COLUMN_MAP, delimiter='\t', progress=progress)


def load_odp_taxa(
    csv_path: PathOrStr = ODP_TAXON_CSV,
    db_path: PathOrStr = DB_PATH,
    progress: Optional[CSVProgress] = None,
):
    """Create or update a taxonomy SQLite table from the Open Data archive"""
    create_tables(db_path)
    progress = progress or CSVProgress(csv_path)
    with progress:
        load_table(csv_path, db_path, 'taxon', TAXON_COLUMN_MAP, delimiter='\t', progress=progress)


def load_odp_users(
    csv_path: PathOrStr = ODP_USER_CSV,
    db_path: PathOrStr = DB_PATH,
    progress: Optional[CSVProgress] = None,
):
    """Create or update a user SQLite table from the Open Data archive"""
    create_tables(db_path)
    progress = progress or CSVProgress(csv_path)
    with progress:
        load_table(csv_path, db_path, 'user', USER_COLUMN_MAP, delimiter='\t', progress=progress)
