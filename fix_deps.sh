#!/usr/bin/env bash
source venv/bin/activate
pip uninstall -y motor pymongo
pip install "pymongo==4.7.2" "motor==3.4.0"
