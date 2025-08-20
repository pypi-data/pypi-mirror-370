## batch_img

Batch processing (**resize, rotate, add border**) image files (**HEIC, JPG, PNG**) by
utilizing **[Pillow / PIL](https://github.com/python-pillow/Pillow)** library.
Resize, rotate, or add border to a single image file or all image files in a folder.
Tested on macOS.

### Installation

#### One Time Setup

One time installation of the `uv` tool to prepare for **All** future Python tools installation.
Install `uv` tool by its standalone installers:

```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Install the `batch_img` tool

Install the `batch_img` tool from PyPI:

```
uv pip install --upgrade batch_img
```

### Usage

#### Sample command lines:

```
✗ batch_img --version
0.0.8

✗ batch_img rotate --angle 90 ~/Downloads/IMG_0070.HEIC
...
✅ Processed the image file(s)
```

### Help

#### Top level commands help:

```
✗ batch_img --help
Usage: batch_img [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show this tool's version.
  --help     Show this message and exit.

Commands:
  border  Add internal border to image file(s), not expand the size.
  resize  Resize image file(s).
  rotate  Rotate image file(s).
```

#### The `border` sub-command CLI options:

```
✗ batch_img border --help
Usage: batch_img border [OPTIONS] SRC_PATH

  Add internal border to image file(s), not expand the size.

Options:
  -bw, --border_width INTEGER RANGE
                                  Add border to image file(s) with the
                                  border_width. 0 - no border.  [default: 5;
                                  0<=x<=30]
  -bc, --border_color TEXT        Add border to image file(s) with the
                                  border_color string.  [default: gray]
  -o, --output TEXT               Output file path. If not specified, replace
                                  the input file.  [default: ""]
  --help                          Show this message and exit.
```

#### The `resize` sub-command CLI options:

```
✗ batch_img resize --help
Usage: batch_img resize [OPTIONS] SRC_PATH

  Resize image file(s).

Options:
  -l, --length INTEGER RANGE  Resize image file(s) on original aspect ratio to
                              the length. 0 - no resize.  [default: 0; x>=0]
  -o, --output TEXT           Output file path. If not specified, replace the
                              input file.  [default: ""]
  --help                      Show this message and exit.
```

#### The `rotate` sub-command CLI options:

```
✗ batch_img rotate --help
Usage: batch_img rotate [OPTIONS] SRC_PATH

  Rotate image file(s).

Options:
  -a, --angle [0|90|180|270]  Rotate image file(s) to the clockwise angle. 0 -
                              no rotate.  [default: 0]
  -o, --output TEXT           Output file path. If not specified, replace the
                              input file.  [default: ""]
  --help                      Show this message and exit.
```
