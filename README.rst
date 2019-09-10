csmr-workflow
=======

.. image:: https://travis-ci.com/igorMIA/csmr-workflow.svg?token=quvECzSEsxpZZFKzztxV&branch=master
    :target: https://travis-ci.com/igorMIA/csmr-workflow

csmr-workflow project


Running
--------------

Using Makefile
^^^^^^^^^^^^^^^^^^^^^

*  to start project run::

    $ make start

*  to stop project run::

    $ make stop

*  to run tests run (if you want run specific test run **make run_tests args=tests.selenium.test_auth)**::

    $ make run_tests

* to add fixtures::

    $ make add_fixtures

* to run selenium tests explicit **required firefox 42** (if you want run specific test run **make run_selenium args=tests.selenium.test_auth)**::

    $ make run_selenium
