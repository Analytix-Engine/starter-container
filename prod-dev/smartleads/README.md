# Analytix Engine SmartLeads

## Introduction

Introducing our Analytix Engine SmartLeads.

------------------------------------------------------------------------

## Development Environment Setup

### Prerequisites

- Install [Visual Studio Code](https://code.visualstudio.com/)
- For Windows, you will need Git installed
- Anaconda
- Setup [SSH Key](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)

### Setup

#### 1. Clone the repository

Using the `git clone <url-to-repo>` command clone the repository in your project folder. e.g. for windows `C:\Users\green\Documents\GitHub\` or for mac `/Users/green/Documents/GitHub/`

#### 2. Create the Anaconda Environment

Open Anaconda Prompt. Execute this command:

```bash
conda create -y -n SmartLeads python=3.8
```

#### 3. Activate the Anaconda environment

```bash
conda activate SmartLeads
```

#### 4. Change to the project directory

Using the command prompt, change directory into the folder you
are working from. For example:

```bash
# Windows
cd "C:\Users\green\Documents\GitHub\SmartLeads"

or 
# Mac
cd "/Users/green/Documents/GitHub/SmartLeads"
```

#### 5. Install requirements

```bash
pip install pip-tools
pip-compile --upgrade src/requirements.in
pip-compile --upgrade dev-requirements.in
pip-sync dev-requirements.txt src/requirements.txt
pip install -e ./src/
```

> **Note**
> The dependencies of a package can change depending on the Python environment in which it is installed. Here we define an environment as a combination of the Operating System (Win, MacOS) and Deployment target (Prod, Dev). When developing the project be sure to use your specific environment dependencies and also to keep them in-sync between different environments.

#### 6. Retrieve license file

Create a ticket on ClickUp [here](https://app.clickup.com/9005067521/v/l/6-900501590052-1) to request the license file for the project. Once you have the license file, place it in the `src/SmartLeads/license.json`

#### 7. Install the pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

#### 8. Run the project tests

```bash
pytest
```

#### 9. Open the project in VSCode

```bash
code .
```

#### 10. Select python interpreter

- VS Code should display a pop-up notification requesting that you select the newly create python virtual environment.

OR

- Open the command palette (&#8984;+Shift+P)
- Type `Python: Select Interpreter`
- Select the recommended environment

#### 11. Run Streamlit

```bash
streamlit run src/SmartLeads/streamlit_app/app.py
```

#### 12. Run the desktop application (MacOS)

```bash
conda install python.app
pythonw src/SmartLeads/SmartLeads.py
```

#### 13. Run the desktop application (Windows)

```bash
python src/SmartLeads/SmartLeads.py
```

------------------------------------------------------------------------

## Software Development Life Cycle

We follow a form of trunk based development using short-lived feature branches.
For further details please see [here](https://trunkbaseddevelopment.com/short-lived-feature-branches/).

When making changes to this project the following steps must be followed:

0. Create new branch on origin repository based on `main` with all build checks passing.

1. All style and static analysis checks must pass.

2. Add new unittests to test new code.

3. All unittests must pass with code coverage checks passing.

4. Add new integrations for new functionality.

5. All integration tests must pass.

6. Add new end to end tests for new components (if appropriate).

7. All end to end tests must pass (if appropriate).

8. Create a Pull Request and assign reviewers.

9. Attend to Pull Request comments and repeat any above steps if required.

10. Merge Pull Request.

------------------------------------------------------------------------

## Release Process

We follow the `release from trunk` development practice where any PR that is merged into the `main` branch will trigger a release process that automatically creates a PR with a `git tag v-Major.Minor.Patch.Build` and `CHANGELOG` updates. Any open release PRs will automatically be updated with new merges into `main`. Once this release PR is merged the build system will create package artefacts and upload them to the company artefact registry. In addition, a Github Release will also be published with the `CHANGELOG`.

The release versioning follows the [Semantic Versioning](https://semver.org/) guidelines.

------------------------------------------------------------------------

## Fixing Bugs

We practice a form `roll-forward` deployment. Since we use `continuous integration` and `continuous delivery` we would rather fix a bug and then release again. We also store all of our previous project artefacts in a registry. This means that we also still have the option to `rollback` to a specific artefact.

------------------------------------------------------------------------

## Project dependencies

To generate or update the dependency requirements for your project you will need to
generate the `production` and `development` dependencies for each supported operating
system (e.g. Windows and MacOS).

To ensure that there are reproducible builds and pipeline runs we use `lock-files` which
pin the exact versions of the project package dependecnies that are required. This means
that the src/requirements.ini and dev-requirements.ini are abstract project dependency
version ranges to enable flexibility during development while the `lock-files` are
concreate pinned versions.

To do this run the following commands in order:

1. Run `pip-compile --upgrade src/requirements.in` to generate the `production` dependencies in `src/requirements.txt`.

2. Run `pip-compile --upgrade dev-requirements.in` to generate the `development` dependencies in `dev-requirements.txt`.

3. Run `pip-sync src/requirements.txt dev-requirements.txt` to install for development work.

------------------------------------------------------------------------
