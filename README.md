# EPoDx Dashboards

This repository contains scripts that download learner data from
[EPoDx](https://www.epodx.org) to inform blended instruction and training
analytics.

## Setup

### Cloning

* Open a terminal on Mac or a terminal emulator such as [Cmder](http://cmder.net) on Windows
* Clone over https: `git clone https://github.com/mefryar/epodx-dashboards.git`

### Environment

* Install the Anaconda distribution of Python 3. ([Mac](https://www.anaconda.com/download/#macos) / [Windows](https://www.anaconda.com/download/#windows))
* Once Anaconda has been installed, open a terminal or emulator and change to
directory to folder where you cloned this repo (e.g. `cd ~/epodx-dashboards`)
* Create a new conda environment: `conda env create --file env.txt`
* Activate the conda environment: `source activate epodx-dashboards`

### Secrets

* From Dropbox (CID)/EPoDx/Data Dashboard/Management/secrets, copy
client_secret.json and secrets.py to the code subfolder of your local version
of this repository (e.g. ~/epodx-dashboards/code).

### Archive learner engagement reports

* Ensure that you have synced Dropbox (CID)/Training Assessment and
Research/BCURE Learner Engagement Reports and that your Dropbox (CID) folder is
located in your home directory.
* Ensure your terminal working directory is your local version of this folder 
(e.g. `cd ~/epodx-dashboards`)
* Ensure that you have activated the epodx-dashboards conda environment (`source activate epodx-dashboards`)
* Run the script: `python code/pull_learner_engagement.py`

### Update dashboards

* Ensure your terminal working directory is your local version of this folder (e.g. `cd ~/epodx-dashboards`)
* Ensure that you have activated the epodx-dashboards conda environment (`source activate epodx-dashboards`)
* First time only, get credentials: `python code/get_credentials.py`
* Update line 223 of code/update_dashboard.py to specify the dashboards you
wish to update (in terms of unit, partner, and data selection.)
* Run the script: `python code/update_dashboard.py`

## License

This project is licensed under the MIT License - see the
[LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

* Many thanks to the teams at EPoD, HKS SLATE, and Open Craft.
* Special thanks to Angela Ambroz and Eric Dodge for their help getting me up
to speed technically, to Jill Vogel for helping me understand the EPoDx API,
and to Adil Saeed, Charlotte Tuminelli, Dan Levy, Emily Myers, Ghania
Suhail, Kimberly Renk, Neeraj Trivedi, Raahema Siddiqui, Sujoy
Bhattacharyya, Theodore Svoronos, and the BCURE ToT alumni for their
encouragement and feedback on the overall learner data dashboard project.
* The EPoDx units were initially developed as part of the Building Capacity to
Use Research Evidence (BCURE) program, funded by UK Aid from the UK government.
