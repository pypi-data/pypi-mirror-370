# genu - UUID Generator

`genu` is a command-line tool for generating UUIDs of different versions.

## Installation

You can install `genu` from PyPI by running the following command:

```sh
pip install genu
```

If you want support for UUIDv7, you can install it with the `uuid7` option:

```sh
pip install genu[uuid7]
```

## Usage

To generate UUIDs, use the following command:

```sh
genu -u 4 -c 5
```

This will generate 5 UUIDs of version 4.

If you want to generate UUIDs of version 3 or 5, you must provide a namespace:

```sh
genu -u 3 --namespace example.com
```

If no options are specified, `genu` will generate a version 4 UUID by default:

```sh
genu
```

## Options

- `-u`, `--uuid-version`: Specifies the version of the UUID (1, 3, 4, 5, 7).
- `-c`, `--count`: Specifies the number of UUIDs to generate (default is 1).
- `--namespace`: Namespace URL for UUID version 3 or 5.
- `-v`, `--version`: Shows the version of the program.

## Contribute

If you want to contribute to this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.