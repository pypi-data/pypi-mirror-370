import pytest
from rich import print as rprint

from wujing.ir.ir import IR


@pytest.fixture(scope="session")
def test_file():
    yield "../../../testdata/xian_railway.xlsx"


@pytest.mark.skip()
def test_ir(test_file):
    ir = IR(file_name=test_file)
    tb_sample = ir.query("select * from data limit 10").sample(frac=1, random_state=42).reset_index(drop=True)
    rprint(tb_sample)
    ir.close()


@pytest.mark.parametrize("sample_size", [None, 3])
def test_sample_size(test_file, sample_size):
    ir = IR(file_name=test_file, sample_size=sample_size)
    tb_sample = ir.query("select * from data limit 10").sample(frac=1, random_state=42).reset_index(drop=True)
    rprint(tb_sample)
    ir.close()


@pytest.mark.skip()
def test_ir_with_duckdb(test_file):
    ir = IR(file_name=test_file, engine="duckdb")
    result = ir.query("SELECT COUNT(*) as count FROM data")
    rprint(f"Row count: {result['count'].iloc[0]}")

    schema = ir.get_schema()
    rprint(schema)

    ir.close()


@pytest.mark.skip()
def test_ir_with_sqlite(test_file):
    """Test IR with SQLite engine"""
    ir = IR(file_name=test_file, engine="sqlite")

    result = ir.query("SELECT COUNT(*) as count FROM data")
    rprint(f"Row count: {result['count'].iloc[0]}")

    schema = ir.get_schema()
    rprint(schema)

    ir.close()
