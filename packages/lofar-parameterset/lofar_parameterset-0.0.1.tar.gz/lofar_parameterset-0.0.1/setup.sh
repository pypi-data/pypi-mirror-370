#! /usr/bin/env bash
#
# Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later
#

# Substitute BASH_SOURCE if unset this is required for simple shells
# such as the one found in docker or alpine docker images.
# `#! /usr/bin/env bash` does not actually ensure the sourcing is executed
# using BASH
if [ -z ${BASH_SOURCE} ]; then
  BASH_SOURCE=${(%):-%x}
fi

ABSOLUTE_PATH=$(realpath $(dirname ${BASH_SOURCE}))

# Create a virtual environment directory if it doesn't exist
VENV_DIR="${ABSOLUTE_PATH}/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
python -m pip install pre-commit
python -m pip install "tox>=4.21.0"

# Install git pre-commit pre-push hook if not already installed
if [ ! -f "${ABSOLUTE_PATH}/.git/hooks/pre-push" ]; then
  pre-commit install --hook-type pre-push
fi
