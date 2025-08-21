#!/bin/bash

$HOME/src/payloop/python-sdk/bin/clean.sh
$HOME/src/payloop/python-sdk/bin/build.sh
/bin/echo -n "Enter the PyPI token: "
read token
$HOME/.local/bin/uv publish --username __token__ --password $token
$HOME/src/payloop/python-sdk/bin/clean.sh
