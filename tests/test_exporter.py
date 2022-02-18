import pytest

from iris_exporter.exporter.atlas import AtlasExporter
from iris_exporter.exporter.csv import CSVExporter
from iris_exporter.test import bucket, database_credentials, storage_credentials


@pytest.mark.parametrize("cls", (AtlasExporter, CSVExporter))
def test_exporter(cls):
    exporter = cls(database_credentials, storage_credentials, bucket)
    exporter.delete("test_nsdi_example", "")
    assert not exporter.exists("test_nsdi_example", "")
    exporter.export("test_nsdi_example", "")
    assert exporter.exists("test_nsdi_example", "")
