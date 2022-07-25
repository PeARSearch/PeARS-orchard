# Run a test server.
import zipfile
import os

if  os.path.exists('app/static/spaces/english.dm')==False:
    with zipfile.ZipFile('app/static/spaces/english.dm.zip', 'r') as zip_ref:
        zip_ref.extractall('app/static/spaces/')

class DeployedFly:
    def __init__(self):
        self.pn_size = None
        self.kc_size = None
        self.wta = None
        self.projections = None
        self.top_words = None
        self.hyperparameters = None

from app import app
app.run(host='0.0.0.0', port=8080, debug=True)
