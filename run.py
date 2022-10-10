# Run a test server.

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
