#!/bin/bash

script_dir=$(dirname "$0")
rsync -av --exclude .git $script_dir/ "$1@learn-chinese.cloudapp.net:/var/sites/learn-chinese"

