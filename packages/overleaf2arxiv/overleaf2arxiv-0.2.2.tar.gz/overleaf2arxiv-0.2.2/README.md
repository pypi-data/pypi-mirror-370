# Overleaf2Arxiv

Academics often write papers in [Overleaf](https://www.overleaf.com), and publish them to [arXiv](https://arxiv.org), but the steps to do so requires a little manual labor.
For example, arXiv requires a `main.bbl` file, which must be manually downloaded from Overleaf and packaged into the zip file.

Overleaf2Arxiv is a simple CLI that aims to make this easier.
Given the Overleaf project ID, it will automatically package it for upload to arXiv, including the `main.bbl` file.

> [!NOTE]
> MacOS and Linux are the primary supported platforms.

## Installation + Setup

To install, run

```bash
pip install overleaf2arxiv
```

Additionally, ensure that you are logged into [Overleaf](https://www.overleaf.com) on your default browser.
The cookies on this browser will be used to authenticate with Overleaf, possibly asking for your keychain password in the process.

Finally, install `pdflatex` on your machine and ensure it's available on the system path.
- On Linux, consider [TeX Live](https://www.tug.org/texlive/)
- On Mac, consider one of:
    - [TeX Live](https://www.tug.org/texlive/)
    - BasicTeX (smaller installation), install with `brew install basictex`

## Usage

Using this script is easy!

To automatically download the project from Overleaf and package it, simply run

```bash
overleaf2arxiv -p <project_id> project.zip
```

where `<project_id>` is the Overleaf project ID (visible in the URL). This may ask for a password while authenticating with Overleaf to download your project.

You can avoid authenticating with Overleaf by downloading the project zip manually, and then running:

```bash
overleaf2arxiv -f <path_to_downloaded_project.zip> project.zip
```

If your source is located in some subfolder of your Overleaf project, use `--subfolder` to specify that.

Finally, just upload `project.zip` to arXiv!
