# EPoDx Dashboards

This repository contains scripts that download learner data from
[EPoDx](https://www.epodx.org) to inform training analytics and blended
instruction. Specifically, the script `code/pull_learner_engagement.py` is used
to archive weekly reports of users' engagement with units on EPoDx and the
script `code/update_dashboard.py` is used to programmatically pull learner data
from the EPoDx API and feed it to Google Sheets that conduct cleaning and
analysis. To get started, follow the steps in the [Installation](##Installation) section below.

## Installation

1. Clone epodx-dashboards repository

    1. Open a terminal (Mac) or a terminal emulator with git such as the full
    version of [Cmder](http://cmder.net) (Windows). If you have not installed
    git on your Mac, type `git --version`, and then follow the instructions to
    install the command line developer tools.
    2. Confirm that you are in your home directory by entering the following
    command: `pwd`
        * On Mac, the output should be `/Users/your_username`.
        * On Windows, the output should be `C:\Users\your_username`.
    3. In your terminal or terminal emulator, enter the following command to
    clone this repository over https: 
    `git clone https://github.com/hks-epod/epodx-dashboards.git`

2. Move files containing connection tokens from Dropbox to cloned repository
    
    1. Ensure that you have access to the following folder: `Dropbox (CID)/EPoDx/Data Dashboard/Management/secrets`
    2. Either download or copy `client_secret.json` and `secrets.py` and move
    both files to `epodx-dashboards/code`.

3. Clone separate epodx repository maintained by OpenCraft

    1. In the same terminal or terminal emulator you used for 1.iii., enter the
    following command: `git clone https://github.com/hks-epod/epodx.git`. This
    repository contains configuration files necessary for connecting to the
    EPoDx API.
    2. Restrict the permissions of the private key files in the epodx
    repository by entering the following command: `chmod 600 epodx/*.pem`

4. Create Python environment
    
    1. Open a browser window (e.g. Chrome, Firefox, or Safari), and download
    the Anaconda distribution of Python 3. ([Link for Mac](https://www.anaconda.com/download/#macos) / [Link for Windows](https://www.anaconda.com/download/#windows)). Follow the 
    [installation instructions](https://docs.anaconda.com/anaconda/install/).
    There is no need to install VS Code. For Mac users, pay careful attention
    at step 5 of the Anaconda installation instructions since some users have
    experienced the default installation location being set to Macintosh HD
    rather than your home folder. If this is the case for you, follow step 6 in
    the Anaconda installation instructions to change the installation location.
    2. Once Anaconda has been installed, reopen your terminal or terminal
    emulator and create a new conda environment that includes all the
    dependencies necessary to run the scripts in this repository by entering
    the following command: `conda env create --file epodx-dashboards/env.txt`.
    It may take a few minutes for this command to finish running.
    3. Activate the conda environment by entering the following command:
    `source activate epodx-dashboards`

### Archive learner engagement reports

This script should be run every week on Friday. To run the script, follow the
steps below.

1. Prerequisites:
    1. Follow the installation instructions above.
    2. Ensure that you have synced `Dropbox (CID)/Training Assessment and Research/BCURE Learner Engagement Reports` and that your `Dropbox (CID)`
    folder is located in your home directory.
2. Open a terminal (Mac) or terminal emulator such as [Cmder](http://cmder.net)
(Windows).
3. Change the directory to the folder where you cloned the
`epodx-dashaboards` repository by entering the following command:
    * Mac: `cd ~/epodx-dashboards`
    * Windows: `cd "C:\Users\your_username\epodx-dashboards"` (Replacing
    `your_username` with your own user name, e.g. `Michael`)
4. Activate the epodx-dashboards conda environment by entering the following
command: `source activate epodx-dashboards`
5. Run the script by entering the following command: `python code/pull_learner_engagement.py`

### Update dashboards

This script is run as needed to support blended instruction. Note that this
script can only fully automate the process of updating the dashboards if more
than 24 hours has passed since cohort assignment because the version of the
student profile information that is accessible via the API is only updated
every 24 hours. To run the script, follow the steps below.

1. Prerequisite: Follow the installation instructions above.
2. Open a terminal (Mac) or terminal emulator such as [Cmder](http://cmder.net)
(Windows).
3. Change the directory to the folder where you cloned the
`epodx-dashaboards` repository by entering the following command:
    * Mac: `cd ~/epodx-dashboards`
    * Windows: `cd "C:\Users\your_username\epodx-dashboards"` (Replacing
    `your_username` with your own user name, e.g. `Michael`)
4. Activate the epodx-dashboards conda environment by entering the following
command: `source activate epodx-dashboards`
5. (First time only) Get credentials for the Google Sheets API by entering the
following command and following the prompts in the pop-up browser window:
`python code/get_credentials.py`
6. Update line 223 of code/update_dashboard.py to specify the dashboards you
wish to update (in terms of unit, partner, and data selection.)
7. Run the script by entering the following command: 
`python code/update_dashboard.py`

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
