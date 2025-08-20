dkist-service-configuration
===========================

|codecov|

A configuration for the `loguru <https://github.com/Delgan/loguru>`_ logger and base configuration object using `pydantic <https://docs.pydantic.dev/1.10/usage/settings/>`_ base settings.

It is important that it be the first import to run so the standard logging basicConfig method has an effect.

Features
--------

* Stderr output
* Intercepted logging from client libraries
* Disabled better exceptions for log levels above debug to mitigate secret leaking
* Configuration logging with secrets redacted
* DKIST Mesh Service configuration parsing

Installation
------------

.. code:: bash

   pip install dkist-service-configuration


Examples
--------

**config.py**

.. code:: python

    from dkist_service_configuration.logging import logger
    from dkist_service_configuration import MeshServiceConfigurationBase
    logger.debug('hello world)
    class NewConfiguration(MeshServiceConfigurationBase):
        username: str = "me"
        password: str = "pass"
    new_configuration = NewConfiguration()
    new_configuration.log_configurations()

The code above will register the existing loggers, retrieve mesh configuration
and custom configuration from the environment and log it while redacting the
password.

.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist_service_configuration/graph/badge.svg?token=5XPJ33224M
 :target: https://codecov.io/bb/dkistdc/dkist_service_configuration
