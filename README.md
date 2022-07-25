# Orchard PeARS, with a fruit fly

**This branch is for the development of the new version of PeARS Orchard, with an underlying fruit fly model.**

## What and why

PeARS (version Orchard) is a search engine that you can install and run locally from your browser. It allows you to 'index' pages (i.e. to produce a computer-readable representation of the pages' content, essential to the search process), and to search pages that you or your friends have indexed. Search happens entirely on your machine, meaning that no one knows what you are searching for and when.

One feature of PeARS Orchard is the ability to convert a small index into a greyish, unassuming picture, called a 'snow pod'. Snow pods are the mini-weapons of the indexing revolution. They can easily be shared with others by email, on social media, or through any other means, so you can be your very own search engine, for yourself and your friends


### How does this fit with peer-to-peer PeARS?

The fully-fledged PeARS system (Peer-to-peer Agent for Reciprocated Search) is supposed to be completely distributed. You can imagine it as an 'automated' version of Phase 1, where you don't have to go and hunt for pods yourself. Your PeARS install will automatically find them on other users' systems and connect to them. We are still working on this phase of the project.


## Installation and Setup

NB: we have some instructions for Windows users [on the wiki](https://github.com/PeARSearch/PeARS-orchard/wiki/Windows-installation).

You can setup PeARS-Orchard from source or using docker

#### From Source

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

##### 4. Unpack the semantic space

Head over to the app/static/spaces directory and unzip english.dm.zip.

    cd app/static/spaces

    unzip english.dm.zip

##### 5. Run it!

In the root of the repo, run:

    python3 run.py


#### Using docker

> Note: Make sure you have [docker installed in your
system](https://docs.docker.com/get-docker/).

The latest Docker image for PeARS-Orchard can be found on Dockerhub
under the organization pearsproject. You can run it locally using the
command:

```
docker run -d -p 8080:8080 pearsproject/pears-orchard:latest
```

## Usage

Now, go to your browser at localhost:8080. You should see the search page for PeARS. You don't have any pages indexed yet, so go to the F.A.Q. page (link at the top of the page) and follow the short instructions to get you going!

