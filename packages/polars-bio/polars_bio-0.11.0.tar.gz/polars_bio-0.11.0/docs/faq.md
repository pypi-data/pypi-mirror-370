1. What versions of Polars are supported?

    Short answer: Polars <= **1.17.1** is supported.

    Longer answer: Since Polars has recently  [upgraded py03 to 0.23.x](https://github.com/pola-rs/polars/pull/20111) any many other dependencies still rely on 0.22.x, we are currently limited to Polars <= 1.17.1. We are working on upgrading to the latest version of Polars.

2. What to do if I get  `Illegal instruction (core dumped)` when using polars-bio?
This error is likely due to the fact that the ABI of the polars-bio wheel package does not match the ABI of the Python interpreter.
To fix this, you can build the wheel package from source. See [Quickstart](quickstart.md) for more information.
```bash
#/var/log/syslog

polars-bio-intel kernel: [ 1611.175045] traps: python[8844] trap invalid opcode ip:709d3ec253cc sp:7ffcc28754e8 error:0 in polars_bio.abi3.so[709d36533000+9aab000]
```

3. How to build the documentation?
   To build the documentation, you need to install the `polars-bio` package and then run the following command in the root directory of the repository:
```bash
MKDOCS_EXPORTER_PDF=false JUPYTER_PLATFORM_DIRS=1 mkdocs serve  -w polars_bio
```

4. How to build the source code and install in the current virtual environment?
```bash
RUSTFLAGS="-Ctarget-cpu=native" maturin develop --release  -m Cargo.toml
```

5. How to run the integration tests?
   To run the integration tests, you need to have the `azure-cli`, `docker`, and `pytest` installed. Then, you can run the following commands:
```bash
cd it
source bin/start.sh
JUPYTER_PLATFORM_DIRS=1 pytest it_object_storage_io.py -o log_cli=true --log-cli-level=INFO
source bin/stop.sh
```
Check the `README` in `it` directory for more information.