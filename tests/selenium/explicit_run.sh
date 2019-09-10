#!/usr/bin/env bash

python3 -m virtualenv venv
source venv/bin/activate

unameOut="$(uname -s)"

if [ -z $1 ]
then
    TEST_PATH=tests/selenium
else
    TEST_PATH=$1
fi

case "${unameOut}" in
    Linux*)     export PATH=$PATH:tests/selenium/geckodriver/linux;;
    Darwin*)    export PATH=$PATH:tests/selenium/geckodriver/mac;;
esac
export $(grep -v '^#' environment/test_local | xargs)
pip install -r requirements/test.txt
python manage.py test "${TEST_PATH}" --noinput
