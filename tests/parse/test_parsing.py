import pytest
import os
import pandas as pd


from slurmdocs.parse.parser import Parser
from slurmdocs.parse import Ilscpu, Iscontrol


def test_lscpu():
    # Instantiate the parser
    parser = Parser(
        iparser=Ilscpu(),
    )

    # Save the output of lscpu to a file
    out = os.popen('lscpu').read()
    with open('lscpu.txt', 'w') as f:
        f.write(out)

    # Parse the file
    parsed = parser('lscpu.txt')

    # Remove the file
    os.remove('lscpu.txt')

    # Checks
    assert 'Architecture' in parsed.index.to_list()
    assert 'CPU(s)' in parsed.index.to_list()
    assert 'Thread(s) per core' in parsed.index.to_list()
    assert 'Core(s) per socket' in parsed.index.to_list()
    assert 'Socket(s)' in parsed.index.to_list()
    assert 'NUMA node(s)' in parsed.index.to_list()
    assert 'Vendor ID' in parsed.index.to_list()
    assert isinstance(parsed, pd.Series)


def test_scontrol_show_node():
    # Instantiate the parser
    parser = Parser(
        iparser=Iscontrol(preprocess=True),
    )

    # Get the output of scontrol show node
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'test_data/scontrol.out'
    )

    # Parse the file
    parsed = parser(filepath)

    # Checks
    assert isinstance(parsed, pd.DataFrame)
    assert 'NodeName' in parsed.columns.to_list()
    assert 'CoresPerSocket' in parsed.columns.to_list()
    assert 'NodeAddr' in parsed.columns.to_list()
    assert 'Sockets' in parsed.columns.to_list()

    return
