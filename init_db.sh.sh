#!/bin/bash
flask db init || true
flask db migrate -m "init"
flask db upgrade
