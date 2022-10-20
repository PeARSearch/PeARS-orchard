# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

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
app.run(host='localhost', port=8080, debug=True)
