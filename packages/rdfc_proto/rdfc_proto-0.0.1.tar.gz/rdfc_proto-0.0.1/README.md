# Python protobuf bindings for RDF-Connect

## Development

The [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) guide was used to set up this project.
As build backend, the default [Hatchling](https://hatch.pypa.io/latest/) is used, for which the `pyproject.toml` file is configured.
That file tells build frontend tools like [pip](https://pip.pypa.io/en/stable/) which backend to use.
This project uses [uv](https://docs.astral.sh/uv/) as package manager.

First, make sure you have [Hatch installed](https://hatch.pypa.io/latest/install/):

```shell
pip install hatch
# OR
brew install hatch
# OR another method of your choice
```

Then, create a virtual environment and spawn a shell. This will automatically install the project dependencies defined in `pyproject.toml`:

```shell
hatch env create
hatch shell
```

Next, generate the gRPC interfaces and code for Python from the proto files by running the following command:

```shell
hatch run proto
```

Next to generating the code, this command also fixes the import statements in the generated files to ensure they are relative imports.
This is necessary because the generated code is placed in a subdirectory (`src/rdfc_proto/generated`) and the imports need to be adjusted accordingly.
The `fix_proto_imports.py` script is responsible for this adjustment.

All the generated code will be placed in the `src/rdfc_proto/generated` directory, which is where the Python package expects to find the generated files.
You can safely delete the `src/rdfc_proto/generated` directory and re-run the command to regenerate the code if needed.

You can build the project with:

```shell
hatch build
```

Lastly, you can publish the package to PyPI with:

```shell
hatch publish
```
