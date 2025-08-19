# Project Life Cycles in Open Source Software

This repository is intended for work related to analyzing the open source ecosystem. The code helps analyze commit streams for content and its statistics. The number of developers and growth levels in open source projects are modeled and the code solves the dynamic (differential) equations that describe the evolution of innovation and developers over time.

Adapting models previously applied to product life cycles, this project models developer engagement through the project life cycle for open-source projects. The code enables users to gather and curate the required information from GitHub repositories and then fit an ordinary differential equation to commits data from GitHub in order to project lifetime developer engagement trajectories. In addition, endogenous growth theory is adapted to model growth dynamics in open-source software engineering, while incorporating the interactions between growth levels and developer activity over time using an additional differential equation for project growth. These solutions calibrate well to many open-source projects. The model generates an estimate of lifetime developer engagement and growth, which supports estimating a lifetime production value of open-source projects. These models may be used to drive open-source strategy and value open-source projects for tech firms.

A long paper titled ["Project Life Cycles in Open Source Software"](https://github.com/srdas/oss-lifecycle/blob/main/docs/OS_Innovation.pdf) (available in the [`docs`](https://github.com/srdas/oss-lifecycle/blob/main/docs/) folder) develops dynamic models of developer engagement and innovation that leads to growth in open source projects. The short version of the paper that accompanies this repository is here: [JOSS](https://github.com/srdas/oss-lifecycle/blob/main/paper.pdf).

A detailed bibliography for open source project analysis that complements the paper is provided as a resource in the [`docs`](https://github.com/srdas/oss-lifecycle/blob/main/docs/) folder in the [OpenSource.bib](https://github.com/srdas/oss-lifecycle/blob/main/docs/OpenSource.bib) file, which is in `bibTeX` format.

The [`data`](https://github.com/srdas/oss-lifecycle/tree/main/data) folder includes sample CSV files with commit and contributor information, while the [`oss_lifecycle`](https://github.com/srdas/oss-lifecycle/tree/main/oss_lifecycle) folder contains Python scripts for processing and analyzing this data. The [`images`](https://github.com/srdas/oss-lifecycle/tree/main/images) folder contains sample images generated for several open-source projects showing the developer engagement over time and the growth in the codebase.

## Getting started

To install this package:

```
$ pip install oss-lifecycle
```

Then start Python:

```
python
```

There are just three steps to use this package to analyze any GitHub repository:

**Step 1**: Gather the commit history for any `<owner>/<repo>`, we will use `jupyterlab/jupyter-ai` as an example. This can take some time if the repo is very large.

```python
>>> from oss_lifecycle import github_gather
>>> github_gather.collect("jupyterlab/jupyter-ai")
```

The extracted and processed data will be in the `data/` sub folder if you need to use it for any other analyses.

**Step 2**: Fit the commit data to the model for developer engagement.

```python
from oss_lifecycle import fit_bass
fit_bass.devs("jupyterlab/jupyter-ai")
```

When you run this two figures will pop up one after the other. You may view them and close them to proceed. These figures are saved in the `images/` folder.

**Step 3**: Fit the growth model to commit data and the developer model data.

```python
from oss_lifecycle import fit_innovation
fit_innovation.growth("jupyterlab/jupyter-ai")
```

This time, four figures will appear one after the other and you proceed by closing each one. These figures are also saved in the `images/` folder.

From the figures you can assess both developer engagement and growth of GitHub repositories. See the paper ["Project Life Cycles in Open Source Software"](https://github.com/srdas/oss-lifecycle/blob/main/docs/OS_Innovation.pdf) for application to many popular repositories.

The remaining discussion in this README delves more into the source code, and alternate ways to run the code including using a GUI, as well as some extra useful scripts.

## Using the code from source

To use the code in this repository clone it

```
$ git clone https://github.com/srdas/oss-lifecycle.git
```

Now install all required packages:

```
$ cd oss-lifecycle
$ pip install -r requirements.txt
```

Then follow the [usage instructions](#usage) below to run various analyses.

For GUI usage, follow these [instructions](#usage-through-a-front-end-gui).

## Distribution

To create the distribution file using `uv` run the following from the top level of the repository:

```
uv build
```

You can distribute the `.tar.gz` or `.whl` files from the `dist` folder.

Unzip the tar file into any folder

```
tar -xzvf oss_lifecycle-0.1.0.tar.gz
```

This will create a folder `oss_lifecycle-0.1.0`. Change directory to this folder. Then run the following to see the front end:

```
uv run oss_lifecycle/server.py
```

See GUI usage [below](#usage-through-a-front-end-gui).

The details of the files are discussed next.

## Source Code

The [`oss_lifecycle`](https://github.com/srdas/oss-lifecycle/tree/main/oss_lifecycle) folder contains Python scripts for collecting, processing, and analyzing commit data of any GitHub repository. To download the commit data for any repo and create the three data files noted above, run [`github_gather.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/github_gather.py). This code takes some time to run as older projects have tens of thousands of commits. To gather the commit data for multiple projects in one job, edit in the projects you want to download in [`collector_script.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/collector_script.py) and then run it. To count the number of code tokens in a repo, use [`count_tokens.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/count_tokens.py).

The next steps are to fit developer engagement to the data and also fit the growth in the project (activity) in two steps:

1. To fit the differential equation to model the developer activity over time, run the code in [`fit_bass.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/fit_bass.py).
2. The module [`fit_innovation.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/fit_innovation.py) fits both the developer/contributor engagement over time as well as the cumulative innovation in the open source project as measured by lines of code changed. Various sample plots are stored in the [`images`](https://github.com/srdas/oss-lifecycle/tree/main/images) folder.

If a monthly report is needed run [`activity_report.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/activity_report.py), which generates monthly reports based on the commit data. The modifications to the codebase are summarized for the month using a LLM. This can help in preparing a monthly report for internal of external reporting, for example, a project that may need to report to the Linux Foundation. This reporting feature is useful to delve into the details of commits and it uses a LLM (Claude-3.5) to summarize the commits. Several statistics about a project from PyPi are collected using the code in [stats.py](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/stats.py).

## Data Files

The [`data`](https://github.com/srdas/oss-lifecycle/tree/main/data) folder contains CSV files with detailed commit information for various projects. These files are created automatically when running [`github_gather.py`](https://github.com/srdas/oss-lifecycle/blob/main/oss_lifecycle/github_gather.py). These files form the basis for further analysis using the code in this repository.

### Examples of file contents

1. `<owner>-<repo>-commits_w_desc.csv`:
   Each CSV file of this type includes columns such as commit hash, author, email, date, commit message, with line additions and deletions.

```csv
commit_hash,author,email,date,message,additions,deletions,files_changed
51a1e5a064623c55060721fcff5b7ead39a88296,Andrew Chang,aychang995@gmail.com,2023-11-14 17:23:13+02:00,"Ensure initials appear in collaborative mode (#443)",10,6,1
88e676581c5545d237dcd379c9cb3a74ddcbb8af,david qiu,david@qiu.dev,2024-02-06 11:15:03-08:00,bump completer pkg resolution to ^4.1.0 (#621),160,171,2
```

2. `<owner>-<repo>-commits.csv`: slightly slimmer version of the previous file type.

```csv
commit_id,author,date,lines_added,lines_removed
72fd708761f1598f1a8ce9b693529b81fd8ca252,Nitish Satyavolu,2025-01-16 18:10:41-08:00,483,1
```

3. `<owner>-<repo>-monthly.csv`: Monthly aggregated data on developer activity and number of lines changed.

```csv
,date,contributors,total_changes
0,2009-07-31 00:00:00+00:00,1,0
1,2009-08-31 00:00:00+00:00,1,21663
```

The files in the `data` folder are examples and need not be retained. As time progresses they will need to be regenerated to capture the latest commits. The same is true for files in the `images` folder, since they are based on the collected data.

## Usage

Given the large amounts of data that may be processed (dependent on repository size), some of the scripts below will take time to run.

**Gathering commit data from GitHub**

To collect commit data for any project run from the _top level_ folder:

```
python -m oss_lifecycle.github_gather <owner>/<repo>
```

An example of `<owner>/<repo>` is `jupyterlab/jupyter-ai`

To collect a list of repositories, use the `collector_script.py` module. First edit it to add in the repos you want to download.

You will run

```
python -m oss_lifecycle.collector_script
```

**Activity Report**

To generate an activity report for any month, run the following commands:

1. First gather the data required, collect the repo data by running from the root folder:

```
python -m oss_lifecycle.github_gather <owner>/<repo>
```

Then, run the activity report:

```
python -m oss_lifecycle.activity_report <owner>/<repo> YYYY-MM
```

**Fit the developer activity over time**

This code solves the differential equation for developer engagement and calibrates it to the collected commits data.

Run this from the command line and close each graph as it appears. Graphs will be saved in the `images` folder:

```
python -m oss_lifecycle.fit_bass <owner>/<repo>
```

**Fit the cumulative growth in the project**

This code solves the differential equation for project growth and calibrates it to the collected commits data.

Run this from the command line and close each graph as it appears. Graphs will be saved in the `images` folder:

```
python -m oss_lifecycle.fit_innovation <owner>/<repo>
```

The generates several plots depicting activity in the chosen repository. Close each plot after viewing it to let the program run to proceed.

## Usage through a front end _GUI_

Install dependencies: `pip install -r requirements.txt`

1. Start the Flask development server from the root of the `oss-lifecycle` folder:

```bash
python -m oss_lifecycle.server
```

2. Open a web browser and navigate to `http://localhost:5000`

Try it with a small repository first as large ones take time to download and process all the commits. For example, enter the Repository Owner as `jupyterlab` and the Repository Name as `jupyter-ai`.

## Using `pandoc` to convert Markdown files to PDF:

```
pandoc paper.md --bibliography=paper.bib --citeproc -o paper.pdf
```

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](https://github.com/srdas/oss-lifecycle/blob/main/LICENSE) file for details.

## Contact

For any questions or inquiries, please contact the project maintainers:

- Sanjiv Das (srdas@scu.edu)
- Brian Granger (bgellison@gmail.com)
