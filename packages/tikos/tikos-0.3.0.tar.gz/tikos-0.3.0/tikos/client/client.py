import json
from typing import Any, List, Tuple

import requests

from tikos.config import VER, BASE_URL_API

def clientConnectorDescription():
    print(f"Tikos Platform Client Connector {VER}")