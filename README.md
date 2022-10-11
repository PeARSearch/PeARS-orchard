# Orchard PeARS, with a fruit fly

**This branch is for the development of the new version of PeARS Orchard, with an underlying fruit fly model.**

## What and why

PeARS (version Orchard) is a search engine that you can install and run locally from your browser. It allows you to 'index' pages (i.e. to produce a computer-readable representation of the pages' content, essential to the search process), and to search pages that you or your friends have indexed. Search happens entirely on your machine, meaning that no one knows what you are searching for and when.

The fruit fly version of Orchard includes a nifty indexing system based on the olfactory system of the actual fruit fly, (*Drosophila melanogaster*)which has already been used in [other computer science applications](https://science.sciencemag.org/content/358/6364/793.abstract) and is recognised for its simplicity and high efficiency.

**We gratefully acknowledge financial support from [NLnet](https://nlnet.nl/) under the [NGI Zero programme](https://nlnet.nl/NGI0/). **


### How does this fit with peer-to-peer PeARS?

The fully-fledged PeARS system (Peer-to-peer Agent for Reciprocated Search) is supposed to be completely distributed. You can imagine it as an 'automated' version of Phase 1, where you don't have to go and hunt for pods yourself. Your PeARS install will automatically find them on other users' systems and connect to them. We are still working on this phase of the project.


## Installation and Setup


##### 1. Clone this repo on your machine:

    git clone https://github.com/PeARSearch/PeARS-orchard.git


##### 2. **Optional step** Setup a virtualenv in your directory.

If you haven't yet set up virtualenv on your machine, please install it via pip:

    sudo apt-get update

    sudo apt-get install python3-setuptools

    sudo apt-get install python3-pip

    sudo pip3 install virtualenv

Then run:

    virtualenv -p python3 env && source env/bin/activate

Then change into the PeARS-orchard directory:

    cd PeARS-orchard

##### 3. Install the build dependencies:

    pip3 install -r requirements.txt

##### 4. **Optional step** Install further languages


If you want to search and index in several languages at the same time, you can add multilingual support to your English install. To do this:

    python3 install_language lc

where you should replace lc with a language code of your choice. You can check our organization to see which languages are currently available. The models for each language are saved in a repository of the form *PeARS-public-pods-lc* where again, 'lc' stands for a given language code. For instance, check out the French repo here: [https://github.com/PeARSearch/PeARS-public-pods-fr](https://github.com/PeARSearch/PeARS-public-pods-fr).

##### 5. Run your pear!

In the root of the repo, run:

    python3 run.py



## Usage

Now, go to your browser at *localhost:8080*. You should see the search page for PeARS. You don't have any pages indexed yet, so go to the F.A.Q. page (link at the top of the page) and follow the short instructions to get you going!

