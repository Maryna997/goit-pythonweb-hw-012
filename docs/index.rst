Contacts API Documentation
==========================

This documentation provides an overview of the Contacts API, its modules, and usage.

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   repositories/contact_repository
   repositories/user_repository
   clients/cloudinary_client
   clients/fast_api_mail_client
   clients/redis_client
   schemas/auth
   schemas/contacts
   schemas/users

Schemas
=======

Authentication Schemas
----------------------
.. automodule:: schemas.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contact Schemas
---------------
.. automodule:: schemas.contacts
   :members:
   :undoc-members:
   :show-inheritance:

User Schemas
------------
.. automodule:: schemas.users
   :members:
   :undoc-members:
   :show-inheritance:

Repositories
============

Contact Repository
------------------
.. automodule:: repositories.contact_repository
   :members:
   :undoc-members:
   :show-inheritance:

User Repository
---------------
.. automodule:: repositories.user_repository
   :members:
   :undoc-members:
   :show-inheritance:

Clients
=======

Cloudinary Client
-----------------
.. automodule:: clients.cloudinary_client
   :members:
   :undoc-members:
   :show-inheritance:

FastAPI Mail Client
-------------------
.. automodule:: clients.fast_api_mail_client
   :members:
   :undoc-members:
   :show-inheritance:

Redis Cache Client
------------------
.. automodule:: clients.redis_client
   :members:
   :undoc-members:
   :show-inheritance:

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
