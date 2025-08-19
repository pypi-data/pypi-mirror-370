# PyTempico

library and examples to use Tausand Tempico TP1000 devices with Python

Written in Python3, pyTempico relies on the following modules:

- hidapi
- pyserial

Library version:       1.3.0<br/>
Current release date:  08/18/2025 (mm/dd/yyyy)<br/>
Original release date: 02/12/2024<br/>
Supported models:      TP1004.

## About Tausand Tempico TP1000

This is a family of time-to-digital converters, ideal to measure time differences between electrical pulses in particle detection, microscopy, and quantum optics experiments.

To learn more about them, visit our website www.tausand.com

To obtain a Tausand's Tempico time-to-digital converter, visit our [online shop](http://www.tausand.com/shop) or contact us at sales@tausand.com

## Installation

`pyTempico` can be installed using `pip` as: 

```
pip install pyTempico
```

Or from GitHub

```
pip install git+https://github.com/Tausand-dev/PyTempico.git
```

## Examples and documentation

For details on how to run this library, read the PDF documentation located at `docs/build/latex/pytempico.pdf`, or navigate the HTML version located at `docs/build/html/index.html`.

## For developers

Clone the GitHub repository and then follow the next steps:

### Creating a virtual environment

Run the following code to create a virtual environment called `.venv`

```
python -m venv .venv
```

#### Activate

- On Unix systems:
  
  ```
  source .venv/bin/activate
  ```

- On Windows:
  
  ```
  .venv\Scripts\activate
  ```

#### Deactivate

```
deactivate
```

### Installing packages

After the virtual environment has been activated, install required packages by using:

```
python -m pip install -r requirements.txt
```

### Editing version number

When a new version is created, the new numbering should be updated in the following files:

- pyTempico/\_\_init__.py 
- README.md

### Building docs

Go to the `docs` folder and run

```
make <command>
```

Where `<command>` is one of the following:

- `latexpdf`
- `html`

To run the `latexpdf` command you will need a working installation of Latex.

### Generating distribution archives

After the virtual environment has been activated, and the packages has been installed, run the command

```
python -m build
```

Once completed, this should generate two files in the `\dist` directory: a `.tar.gz` and a `.whl` file. These files may be published in the TestPyPI or the PyPI repositories.
