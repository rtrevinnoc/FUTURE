=============
API Endpoints
=============

All public FUTURE instances expose a set of dedicated routes that allow to automate the extraction of information.
Each one of these simulate as if a user (in this case an application) entered a query through the user interface, but instead reply with JSON.

Output
======

The most important routes in a FUTURE instance are the **output** endpoints, because they allow to extract information from the server easily.
These are used to obtain URL's or images from the index, or perhaps to get a list of all registered peers in a given instance.

/_answer
--------

.. note:: The parameters for this route are:

This is the main method to get
+-------+---------+--------+------+
| Input |         | Output |      |
+=======+=========+========+======+
| Name  | Type    | Name   | Type |
+-------+---------+--------+------+
| query | String  |        |      |
+-------+---------+--------+------+
| page  | Integer |        |      |
+-------+---------+--------+------+
|       |         |        |      |
+-------+---------+--------+------+
