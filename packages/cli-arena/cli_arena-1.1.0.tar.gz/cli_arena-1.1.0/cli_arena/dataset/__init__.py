from .dataset import Dataset
try:
    from .dataset_metadata import DatasetMetadata  # if exists locally
except Exception:
    class DatasetMetadata:  # minimal shim if not present
        pass

__all__ = ["Dataset", "DatasetMetadata"]
