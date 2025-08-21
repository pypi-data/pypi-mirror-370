The tech_mapper_main.json file provides mappings between a source technology, a target type (SQL, SPARKSQL, PYSPARK) and a base configuration file.

This file is used not only internally by dbxconv, but also by bladerunner, in order to pass proper parameters to dbxconv when invoked from Lakebridge.

Lakebridge itself gets the list of supported source techs (with a user-friendly name) from a config stored in lsp/config.yml. In Lakebridge lingo, they are named dialects.

As such, it is important to ensure that the tech_mapper_main.json and the lsp/config.yml files are kept in sync.
This is achieved by tests in bladerunner/tests/unit/test_transpiler.py. The CI will fail if the files are not in sync.
In order to fix discrepancies, you should:
 - adjust the list of dialects in lsp/config.yml
 - adjust the friendly/internal name in bladebridge/src/databricks/labs/bladebridge/helpers.py
