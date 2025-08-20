import re
from io import BytesIO, StringIO
from typing import Any

import pandas as pd
from chardet import UniversalDetector

from fa_common import BadRequestError
from fa_common.exceptions import AlreadyExistsError, NotFoundError, RuleValidationError
from fa_common.models import File
from fa_common.routes.files.models import FileDB
from fa_common.storage import get_storage_client

image_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff", "webp", "svg", "ico", "heic", "heif", "avif"]


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean.

    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)


def is_image(file: File):
    return not file.dir and (
        (file.content_type is not None and file.content_type.startswith("image")) or file.extension.lower() in image_extensions
    )


def extension_to_mimetype(ext: str) -> str:
    """Convert common file extensions to their corresponding MIME type."""
    ext = ext.lower()
    if ext == "csv":
        return "text/csv"
    if ext == "json":
        return "application/json"
    if ext == "feather":
        return "application/octet-stream"
    if ext == "xls" or ext == "xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if ext == "txt":
        return "text/plain"
    if ext == "pdf":
        return "application/pdf"
    if ext == "html":
        return "text/html"
    if ext == "svg":
        return "image/svg+xml"
    if ext == "png":
        return "image/png"
    if ext == "jpg" or ext == "jpeg":
        return "image/jpeg"
    if ext == "gif":
        return "image/gif"
    if ext == "bmp":
        return "image/bmp"
    if ext == "tiff":
        return "image/tiff"
    if ext == "tif":
        return "image/tiff"
    if ext == "webp":
        return "image/webp"
    if ext == "ico":
        return "image/x-icon"
    if ext == "heic":
        return "image/heic"
    if ext == "heif":
        return "image/heif"
    if ext == "avif":
        return "image/avif"
    if ext == "geojson":
        return "application/geo+json"
    return "application/octet-stream"


async def get_unique_filename(bucket_name: str, file_path: str | None, filename: str | None, allow_duplicates=False) -> str:
    if filename is None:
        raise ValueError("Filename cannot be None")
    if file_path is None:
        file_path = ""
    client = get_storage_client()
    if await client.file_exists(bucket_name, f"{file_path}/{filename}"):
        if not allow_duplicates:
            raise AlreadyExistsError(f"File {filename} already exists in the storage location {file_path}.")
        else:
            file_list = await client.list_files(bucket_name, f"{file_path}/".replace("//", "/"))
            file_names = [f.name for f in file_list]
            _filename, extension = filename.rsplit(".", 1)
            new_filename = filename
            i = 1
            while new_filename in file_names:
                new_filename = f"{_filename}({i}).{extension}"
                i += 1
        return new_filename
    return filename


async def get_bytes_from_file_ref(file_ref: File) -> BytesIO:
    if file_ref.bucket is None:
        raise ValueError("File reference is missing a bucket")

    if file_ref.id is None:
        raise ValueError("File reference is missing an id")

    client = get_storage_client()
    bytes_io = await client.get_file(file_ref.bucket, file_ref.id)
    if bytes_io is None:
        raise NotFoundError(f"File {file_ref.id} not found")

    return bytes_io


async def get_data_frame_from_file(
    file,
    filename: str | None,
    header_row: int | None = 0,
    can_be_single_col: bool = False,
    separator: str | None = None,
    sheet: str | int | None = None,
    data_start_row: int | None = 1,
    data_end_row: int | None = None,
    encoding: str | None = "utf-8",
    transpose: bool = False,
    metadata_rows: dict[str, int] | None = None,
) -> tuple[pd.DataFrame, dict[str, list[Any]] | None]:
    """Converts an uploaded file to a data frame, detects the encoding and separator automatically."""
    if filename is None:
        raise BadRequestError("Filename is required to parse file")

    # First check if file extension is supported
    if not any(ext in filename.lower() for ext in [".feather", ".csv", ".txt", ".xlsx", ".xls"]):
        raise BadRequestError("File format not supported for table operations")

    try:
        df: pd.DataFrame | None = None
        if ".feather" in filename.lower():
            df = pd.read_feather(BytesIO(file.read()))
        elif ".csv" in filename.lower() or ".txt" in filename.lower():
            # detect correct encoding if not specified
            if encoding is None:
                detector = UniversalDetector()
                for line in file.readlines():
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
                file.seek(0)
                encoding = detector.result["encoding"]

            # For CSV files, first read without header to preserve all rows
            df = pd.read_csv(
                StringIO(file.read().decode(encoding)),
                sep=separator,
                header=None,  # Read without setting a header initially
                engine="pyarrow" if separator is not None else "python",
            )

            if df.shape[1] == 1 and not can_be_single_col:
                raise RuleValidationError(
                    "Only one column could be detected, this may indicate your CSV separators are not a "
                    + "standard format. Try converting your file to use ',' separators."
                )
        elif ".xlsx" in filename.lower() or ".xls" in filename.lower():
            # For Excel files, first read without header to preserve all rows
            df = pd.read_excel(file, sheet_name=sheet, header=None) if sheet is not None else pd.read_excel(file, header=None)

        # Apply data range if specified
        if df is not None:
            # Transpose if requested (swap rows and columns)
            if transpose:
                df = df.T

            metadata = None
            if metadata_rows is not None and len(metadata_rows) > 0:
                metadata = {}
                for key, value in metadata_rows.items():
                    # extract metadata rows prior to setting header row
                    metadata[key] = df.iloc[value].tolist()

            # Now handle the header row - after potential transpose
            if header_row is None:
                header_row = 0

            if header_row < len(df):
                # Use the specified row as column headers
                df.columns = df.iloc[header_row]
                # Remove the header row from the data
                df = df.drop(header_row)
                # Reset index after dropping the header row
                df = df.reset_index(drop=True)
                if data_start_row is not None and data_start_row > header_row:
                    data_start_row -= 1

            # Now handle data range slicing
            if data_start_row is not None or data_end_row is not None:
                start_idx = data_start_row if data_start_row is not None else 0
                df = df.iloc[start_idx:data_end_row] if data_end_row is not None else df.iloc[start_idx:]
                df = df.reset_index(drop=True)

            # Ensure column names are strings and handle any unnamed columns
            df.columns = df.columns.astype(str)
            df = sanitise_column_headers(df)

            return df, metadata
    except Exception as e:
        raise BadRequestError(f"Failed to parse file as a table: {e!s}") from e

    raise BadRequestError("Unsupported file format for table operations")


def sanitise_column_headers(df: pd.DataFrame, suffix: str = " #") -> pd.DataFrame:
    """
    Function to sanitise a dataframe column headers to remove leading and trailing spaces and ensure they
    have readable names.

    When two or more columns have the same name, each duplicated column will have a numericic suffix assigned.

    eg. The column names below:
    " Sample "  "Hole ID" ""  ""  "Au"  "Ag"  "Au"


    will result in:
    "Sample"  "Hole ID" "Unnamed #1"  "Unnamed #2"  "Au #1"  "Ag"  "Au #2"

    Args:
        df (pd.DataFrame): The original dataframe to be modified.
        suffix (str, optional): Suffix to be added between the original value and the count value.
            Defaults to " #".

    Returns:
        pd.DataFrame: The original dataframe with modified headers
    """
    df.columns = df.columns.str.strip()
    df.columns = df.columns.fillna("Unnamed")

    # this is a complicated way of ensuring that only the duplicated column names have numeric suffix assigned
    col_df = df.columns.to_frame().reset_index(drop=True)
    appendents = (suffix + col_df.groupby(0).cumcount().add(1).astype(str).replace("0", "")).replace(suffix, "")
    col_df.loc[col_df.duplicated(subset=[0], keep=False), 0] = col_df[0].astype(str) + appendents.astype(str)

    df.columns = col_df.iloc[:, 0]
    return df


async def get_file_db_for_storage_path(name: str, storage_path: str) -> FileDB | None:
    """Get a the file db record matching the exact provided name and storage path

    Args:
        name (str): The name of the file
        storage_path (str): The storage path (minus the bucket and name)

    Returns:
        FileDB: The file db record if found. Otherwise None
    """
    file_query: dict[str, Any] = {}

    file_query["fileRef.path"] = storage_path

    file_query["fileRef.name"] = name

    return await FileDB.find_one(file_query)


def safe_join_path(paths: list[str]) -> str:
    return "/".join([pth.strip("/") for pth in paths if pth not in [None, ""]]).replace("//", "/")
