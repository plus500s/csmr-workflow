#!/usr/bin/env bash


python3 -m virtualenv venv
source venv/bin/activate
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     export PATH=$PATH:tests/selenium/geckodriver/linux;;
    Darwin*)    export PATH=$PATH:tests/selenium/geckodriver/mac;;
esac
export $(grep -v '^#' environment/test_local | xargs)
pip install -r requirements/test.txt
python manage.py test tests/selenium/ --noinput
