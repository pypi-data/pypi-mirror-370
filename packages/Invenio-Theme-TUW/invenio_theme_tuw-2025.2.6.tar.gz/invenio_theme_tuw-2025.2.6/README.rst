..
    Copyright (C) 2020 - 2024 TU Wien.

    Invenio-Theme-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

===================
 Invenio-Theme-TUW
===================

This module provides UI components to bring the TU Wien corporate design to InvenioRDM.
It also provides some extra functionality and new endpoints.


Features
--------

* TU Wien corporate design
* Extra pages with information related to the service at TU Wien
* Guarded record deposit & community creation pages
* Form to contact the owner of records
* Small bespoke admin pages geared towards use at TU Wien
* Greetings from the Easter Bunny
* Etc.


Installation
------------

After installing Invenio-Theme-TUW via `pip`, Invenio's assets have to be updated:

.. code-block:: console

   $ pip install invenio-theme-tuw
   $ invenio-cli assets build


Running tests
-------------

To execute the tests, the project has to be installed locally.
Then, the `run-tests.sh` script can be executed.

.. code-block:: console

   $ uv sync --all-extras
   $ source .venv/bin/activate
   $ ./run-tests.sh
   $ deactivate
