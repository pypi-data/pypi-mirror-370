import logging

from delta_table_utils_2 import (
    write_delta_table,
    replace_delta_table,
    merge_delta_table,
    optimize_and_vacuum_table,
    optimize_and_zorder_table,
    optimize_zorder_and_vacuum_table
)

class MockSpark:
    def __init__(self):
        self.commands = []

    def sql(self, query: str):
        print(f"[Spark SQL] Executing: {query}")
        self.commands.append(query)

class MockDataFrame:
    def __init__(self, count_val=10):
        self._count_val = count_val
        self.write = self

    def format(self, fmt):
        return self

    def mode(self, mode):
        return self

    def option(self, key, value):
        return self

    def partitionBy(self, *cols):
        return self

    def saveAsTable(self, name):
        print(f"[DataFrame] Saved as table: {name}")
        return self

    def count(self):
        return self._count_val

class MockDeltaTable:
    @staticmethod
    def isDeltaTable(spark, path):
        return True

    @staticmethod
    def forPath(spark, path):
        return MockDeltaTable()

    def alias(self, name):
        return self

    def merge(self, source, condition):
        self.source = source
        self.condition = condition
        return self

    def whenMatchedUpdateAll(self):
        return self

    def whenNotMatchedInsertAll(self):
        return self

    def execute(self):
        print(f"[DeltaTable] Merge executed with condition: {self.condition}")


# Monkey patch delta.tables
import delta
delta.tables.DeltaTable = MockDeltaTable

logger = logging.getLogger("delta_test")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Run tests
def test_write_delta_table_overwrite():
    try:
        write_delta_table(
            spark=MockSpark(),
            df=MockDataFrame(),
            table_full_name="silver.test_overwrite",
            mode="overwrite",
            log=logger
        )
        print("✅ test_write_delta_table_overwrite passed")
    except Exception as e:
        print("❌ test_write_delta_table_overwrite failed:", e)

def test_write_delta_table_invalid_mode():
    try:
        write_delta_table(
            spark=MockSpark(),
            df=MockDataFrame(),
            table_full_name="silver.test_invalid",
            mode="invalid_mode",
            log=logger
        )
        print("❌ test_write_delta_table_invalid_mode failed: should have raised ValueError")
    except ValueError:
        print("✅ test_write_delta_table_invalid_mode passed")

def test_merge_without_keys_should_fail():
    try:
        write_delta_table(
            spark=MockSpark(),
            df=MockDataFrame(),
            table_full_name="silver.test_merge",
            mode="merge",
            log=logger
        )
        print("❌ test_merge_without_keys_should_fail failed: should have raised ValueError")
    except ValueError:
        print("✅ test_merge_without_keys_should_fail passed")

def test_merge_success():
    try:
        mock_spark = MockSpark()
        mock_df = MockDataFrame()
        merge_delta_table(
            spark=mock_spark,
            df=mock_df,
            table_full_name="silver.test_merge",
            target_full_path="/mnt/test/merge",
            merge_cols=("id",),
            log=logger
        )
        print("✅ test_merge_success passed")
    except Exception as e:
        print("❌ test_merge_success failed:", e)

def test_optimize_and_vacuum():
    try:
        optimize_and_vacuum_table(
            spark=MockSpark(),
            table_full_name="silver.optimize_test",
            log=logger
        )
        print("✅ test_optimize_and_vacuum passed")
    except Exception as e:
        print("❌ test_optimize_and_vacuum failed:", e)

def test_optimize_and_zorder():
    try:
        optimize_and_zorder_table(
            spark=MockSpark(),
            table_full_name="silver.optimize_zorder_test",
            zorder_cols=["id", "data"],
            log=logger
        )
        print("✅ test_optimize_and_zorder passed")
    except Exception as e:
        print("❌ test_optimize_and_zorder failed:", e)

def test_optimize_zorder_and_vacuum():
    try:
        optimize_zorder_and_vacuum_table(
            spark=MockSpark(),
            table_full_name="silver.optimize_zv_test",
            zorder_cols=["id"],
            vacuum_retention_hours=24,
            log=logger
        )
        print("✅ test_optimize_zorder_and_vacuum passed")
    except Exception as e:
        print("❌ test_optimize_zorder_and_vacuum failed:", e)

if __name__ == "__main__":
    test_write_delta_table_overwrite()
    test_write_delta_table_invalid_mode()
    test_merge_without_keys_should_fail()
    test_merge_success()
    test_optimize_and_vacuum()
    test_optimize_and_zorder()
    test_optimize_zorder_and_vacuum()
