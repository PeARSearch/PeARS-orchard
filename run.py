# Run a test server.
import os


# Fruit fly class
class DeployedFly():
    def __init__(self):
        self.kc_size = None
        self.wta = None
        self.projection = None
        self.val_scores = []

class PodMatrix():
    def __init__(self):
        self.m = None          #Pod hashes
        self.subscribed = None #Row indices of subscribed pods, empty at init
        self.metacats = []     #Names of metacategories, shared by all installs

from app import app
app.run(host='0.0.0.0', port=8080, debug=True)
