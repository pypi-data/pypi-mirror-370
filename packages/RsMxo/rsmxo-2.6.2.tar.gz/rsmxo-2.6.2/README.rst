==================================
 RsMxo
==================================

.. image:: https://img.shields.io/pypi/v/RsMxo.svg
   :target: https://pypi.org/project/ RsMxo/

.. image:: https://readthedocs.org/projects/sphinx/badge/?version=master
   :target: https://RsMxo.readthedocs.io/

.. image:: https://img.shields.io/pypi/l/RsMxo.svg
   :target: https://pypi.python.org/pypi/RsMxo/

.. image:: https://img.shields.io/pypi/pyversions/pybadges.svg
   :target: https://img.shields.io/pypi/pyversions/pybadges.svg

.. image:: https://img.shields.io/pypi/dm/RsMxo.svg
   :target: https://pypi.python.org/pypi/RsMxo/

Rohde & Schwarz MXO Seriers Digital Oscilloscopes Driver RsMxo instrument driver.

Basic Hello-World code:

.. code-block:: python

    from RsMxo import *

    instr = RsMxo('TCPIP::192.168.56.101::hislip0', reset=True)
    idn = instr.query_str('*IDN?')
    print('Hello, I am: ' + idn)

Supported instruments: MXO44,MXO58,MXO58C

The package is hosted here: https://pypi.org/project/RsMxo/

Documentation: https://RsMxo.readthedocs.io/

Examples: https://github.com/Rohde-Schwarz/Examples/


Version history
----------------

	Latest release notes summary: Small interface improvements and bug fixes

	Version 2.6.2
		- Small interface improvements and bug fixes.

	Version 2.6.1
		- Fixed bug, where arguments or return values were wrongly scalar instead of lists.

	Version 2.6.0
		- First released version
