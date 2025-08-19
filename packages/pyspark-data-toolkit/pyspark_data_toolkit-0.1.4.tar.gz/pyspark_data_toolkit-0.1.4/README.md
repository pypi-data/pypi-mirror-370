# pyspark-data-toolkit — Utilities Library for PySpark & Delta Lake

[![PyPI version](https://img.shields.io/pypi/v/pyspark-data-toolkit.svg)](https://pypi.org/project/pyspark-data-toolkit/)
[![Python](https://img.shields.io/pypi/pyversions/pyspark-data-toolkit.svg)](https://pypi.org/project/pyspark-data-toolkit/)
[![License](https://img.shields.io/github/license/thaissateodoro/pyspark-data-toolkit)](https://github.com/thaissateodoro/pyspark-data-toolkit/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/thaissateodoro/pyspark-data-toolkit/tests.yml?branch=main)](https://github.com/thaissateodoro/pyspark-data-toolkit/actions)

A **production-ready utility library** to accelerate Data Engineering workflows with **PySpark** and **Delta Lake**.

Stop rewriting boilerplate code. `pyspark-data-toolkit` delivers robust, modular functions for **schema management**, **audit trails**, **string normalization**, **profiling**, **union operations**, **windowing**, and **Delta Lake management** — all with **logging support** and **data governance best practices** built-in.

---

## 📦 Installation

```bash
pip install pyspark-data-toolkit
```

For local development:

```bash
git clone https://github.com/<your-org>/pyspark-data-toolkit.git
cd pyspark-data-toolkit
pip install -e ".[dev]"
```

---

## ✨ Key Features

- 📦 **Modular design** — Import only what you need (audit, schema, delta, json, profiling, etc.)
- ⚡ **Production-grade** — Exception handling and structured logging
- 🧪 **Profiling & validation** — Null analysis, stats, outliers, schema diffs
- 🧼 **Normalization utilities** — Clean strings and standardize column names
- 🔄 **Schema enforcement** — Apply, validate, and cast schemas safely
- 🧱 **Delta Lake utilities** — Merge, replace, optimize, vacuum, z-order
- 🪟 **Window-based deduplication** — Keep the latest records per key
- 📊 **Audit metadata** — Control columns, row hashes, batch IDs
- 🔗 **JSON manipulation** — Nested structure extraction, flattening
- 🧠 **Diff utilities** — Compare DataFrames and tag changes

---

## 📋 Modules Overview

| Module                | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| `audit_utils`         | Add control/audit columns and validate ingestion metadata.       |
| `dataframe_utils`     | Common transformations for DataFrames.                           |
| `datetime_utils`      | Date/time parsing, formatting, and timezone conversion.          |
| `delta_table_utils`   | Delta Lake management: merges, optimizations, partitions.        |
| `diff_utils`          | Compare DataFrames and schemas, summarize differences.           |
| `json_utils`          | Extract and flatten JSON/nested structures in columns.           |
| `normalization_utils` | Normalize strings and column names, safe numeric conversion.     |
| `profiling_utils`     | Null analysis, stats, outliers, cardinality, skew, correlations. |
| `schema_utils`        | Apply, validate, and cast schemas from specs.                    |
| `union_utils`         | Schema-aligned DataFrame unions or JSON merges.                  |
| `window_utils`        | Latest-record selection and deduplication by window.             |

---

## 🚀 Quick Start Example

```python
from pyspark.sql import SparkSession, Row
from pyspark_data_toolkit.audit_utils import add_control_columns
from pyspark_data_toolkit.profiling_utils import profile_nulls

spark = SparkSession.builder.getOrCreate()

df = spark.createDataFrame([
    Row(id=1, value="A"),
    Row(id=2, value=None)
])

# Add control columns (e.g., ingestion timestamp, batch ID)
df = add_control_columns(df)

# Profile null values
null_report = profile_nulls(df)
print(null_report)
```

---

## 📖 Module Usage Examples

> 💡 Below are **short, illustrative snippets**. Full pipelines and advanced use cases are available in [`EXAMPLES.md`](https://github.com/thaissateodoro/pyspark-data-toolkit/EXAMPLES.md).cd 

### **Audit**
```python
from pyspark_data_toolkit.audit_utils import *
df = add_control_columns(df, add_hash=True, version='v2')
df = check_row_duplicates(df)
df = add_audit_trail_columns(df)
```

### **Delta Lake**
```python
from pyspark_data_toolkit.delta_table_utils import write_delta_table, merge_delta_table
write_delta_table(spark, df, "db.table", "/path", arq_format="delta", mode="overwrite", partition_cols=("part",))
merge_delta_table(spark, df_updates, "db.table", "/path", merge_cols=("id",))
```

### **Profiling**
```python
from pyspark_data_toolkit.profiling_utils import profile_nulls, profile_numeric_stats
nulls = profile_nulls(df)
stats = profile_numeric_stats(df)
```

### **Normalization**
```python
from pyspark_data_toolkit.normalization_utils import normalize_strings, normalize_column_names
df = normalize_strings(df, columns=["name"])
df = normalize_column_names(df)
```

### **Union**
```python
from pyspark_data_toolkit.union_utils import union_all_with_schema
df_union = union_all_with_schema([df1, df2])
```

### **Window**
```python
from pyspark_data_toolkit.window_utils import drop_duplicates_keep_latest
df_latest = drop_duplicates_keep_latest(df, keys=["id"], order_col="timestamp")
```

---

## 🏆 Best Practices

- **Be modular** — Import only the needed functions for clarity and performance.
- **Profile early** — Run profiling after ingestion to catch anomalies quickly.
- **Validate schemas** — Apply and validate schemas before transformations.
- **Governance first** — Use audit utilities to ensure traceability.
- **Delta Lake safety** — When overwriting, always set `replace_where` to avoid unwanted partition drops.

---

## 🔧 Dependencies

- Python >= 3.8
- PySpark >= 3.0
- Delta Lake (optional, required only for Delta modules)

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
make test
```

---

## 📝 Changelog

### v0.1.0
- Initial release
- Schema management utilities
- Profiling (nulls, stats, outliers, diffs)
- Normalization functions
- Delta Lake operations (merge, optimize, vacuum)
- JSON extraction and flattening

---

## 🤝 Contributing

Contributions are welcome!  

1. Fork the project  
2. Create your feature branch (`git checkout -b feature/pyspark-data-toolkit`)  
3. Commit your changes (`git commit -m 'Add new feature'`)  
4. Push to your branch (`git push origin feature/pyspark-data-toolkit`)  
5. Open a Pull Request  

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
