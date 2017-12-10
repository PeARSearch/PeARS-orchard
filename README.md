# Orchard PeARS
----
## What and why

Orchard PeARS is a decentralised version of the Web search engine PeARS (Peer-to-peer Agent for Reciprocated Search). 

You can install the software and build yourself a Web index that is privately searchable on your machine by connecting to themed 'pods' provided by the community. 

Orchard PeARS is to be accompanied by the 'Orchard' repo [coming very soon], which contains code to set up your own pod. We encourage you to start a pod on topics you're passionate about, and share/index the best websites on the topic.


### How does it fit with peer-to-peer PeARS?

Orchard PeARS should be seen as Phase 1 of the PeARS project: the decentralised version is a first step that will help us build a fully distributed model. In particular, building a user base in the decentralised setup will allow us to provide a pool of indexed pages to the final distributed network.

### Why 'orchard'?

The fully distributed version of PeARS will be made of many individual users with the availability to connect to each other. In the decentralised version, we are pooling the Web indexing work in small community-based farms (the pods).

----
## Usage

Clone this repo on your machine:

    git clone -b development https://github.com/PeARSearch/orchard-pears.git

Install the build dependencies:

    pip3 install -r requirements.txt

Head over to the app/static/spaces directory and unzip english.dm.zip.

In the root of the repo, run:

    python3 run.py

Now, go to your browser at localhost:8080. You should see the search page for PeARS. You don't have any pages indexed yet, so to give you a headstart, click on 'Indexer' at the top of the page, and go to the 'Index from pod' section. Tick the box next to Pod0 and click 'Go'. This will index the content of Pod0, a general-purpose, English-language pod. Once this is done, head to 'Search' again and try PeARS!


