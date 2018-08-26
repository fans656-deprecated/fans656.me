import os
import sys
import json
import itertools
import subprocess
from datetime import datetime
from collections import defaultdict

import requests
from f6 import each

import conf

r = requests.post(
    conf.neo4j_db,
    auth=(conf.neo4j_user, conf.neo4j_password),
    headers={'Content-Type': 'application/json'},
    data = {
        'query': 'match (n) return count(n)'
    }
)
print json.loads(r.text)
