# pyDataCube
## Running the experiments
Commit 1c84c423dc439e842a5906a86235c3e7439f0c7e was used for the experiments.
The timer object that measured the time spent in the database was injected into pandas' `read_sql` method (and its auxiliary methods) in `io/sql.py`.
The modified `sql.py` file is included in the base of this repository as `pandas_sql.py`.
This modified `sql.py` was, together with the version associated with the above commit hash, used for gaining the experiments results in the journal paper
