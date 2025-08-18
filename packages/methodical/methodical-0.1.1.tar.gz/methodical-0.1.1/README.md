# Table of Contents
- 1 [methodical](#methodical)
	- 1.1 [Features](#features)
	- 1.2 [Installation](#installation)
		- 1.2.1 [Local Installation](#local-installation)
	- 1.3 [Usage](#usage)
	- 1.4 [Contributing](#contributing)
		- 1.4.1 [Git Hooks](#git-hooks)
	- 1.5 [License](#license)
  
# methodical
A simple command-line tool that scans Markdown files for headlines and assembles them into a clean,
nested *table of contents*.

## Features
📑 Parse Markdown files and detect headings (#, ##, ###, …)

🗂 Generate a structured Table of Contents

🔗 Insert anchor links to headings

⚡ Fast and lightweight — no external dependencies besides Python

🛠 Easy to integrate into your workflow (e.g., pre-commit hook)

## Installation

### Local Installation

```bash
git clone https://github.com/lalinguette/methodical.git
cd methodical
pip install -e .
```

## Usage

```bash
methodical PATH/TO/FILE.md
```

This will add a ToC to the top of your file and print the Markdown ToC to stdout

Example
```markdown
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    - [Command line](#command-line)
    - [Python API](#python-api)
```

You can redirect the output into a file:
```bash
methodical example_files/example.md > TOC.md
```

## Contributing

### Git Hooks
This project uses pre-commit to enforce style and run tests:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

Now formatting and tests will run automatically before you commit or push.

## License
This project is licensed under the MIT License.