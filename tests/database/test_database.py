import unittest
import tempfile
import shutil
from slurmdocs.database import SlurmClusterDatabase
import pytest
from pathlib import Path
import pandas as pd


@pytest.fixture
def slurm_db():
    # Create a database in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = temp_dir + '/slurm_db'
        slurm_db = SlurmClusterDatabase(db_name='slurm_db', db_path=db_path)
        yield slurm_db


def test_create_delete(slurm_db):
    # Check if the database directory is created
    slurm_db.create()

    assert (slurm_db.db_path / 'node').exists()
    slurm_db.delete()


def test_is_empty_empty_db(slurm_db):
    # Initially, the database should be empty
    assert slurm_db.is_empty()


def test_insert_and_query_cpu_data(slurm_db):
    # Create a database
    slurm_db.create()

    # Sample Files to be inserted
    file_path = Path(__file__).parent / 'sample_test_data'

    # Insert CPU data
    for file in (file_path / 'cpu_data').glob('*.txt'):
        with open(file, 'r') as f:
            cpu_data = {'key': 'cpu', 'filename': file.name, 'data': f.read()}
            slurm_db.insert(cpu_data)

        # Query the inserted CPU data
        queried_data = slurm_db.query({'key': 'cpu', 'filename': file.name})

        assert isinstance(queried_data, pd.Series)

    assert len(slurm_db) == 6  # 6 CPU data files

    # Add node data
    with open(file_path / 'node_data' / 'node_info.txt', 'r') as f:
        node_data = {'key': 'node', 'filename': 'nodes.txt', 'data': f.read()}
        slurm_db.insert(node_data)

    # Query the inserted node data
    queried_data = slurm_db.query(node_data)

    assert isinstance(queried_data, pd.DataFrame)
    assert len(slurm_db) == 7  # 1 node data file
    assert len(queried_data) == 81  # 81 nodes

    # Check coverage
    coverage = slurm_db.coverage()

    assert coverage == pytest.approx(6 * 100 / 81, 0.1)
    # Remove database
    slurm_db.delete()
