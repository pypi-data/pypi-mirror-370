######
ut_arr
######

********
Overview
********

.. start short_desc

**Utilities to manage Arrays**

.. end short_desc

************
Installation
************

.. start installation

Package ``ut_array`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_arr

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ut_arr

.. end installation

***************
Package logging
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Files of Package ``ut_arr`` could be classified into the follwing file types
(c.f.: **Appendix**: `Python Terminology`):

#. **Special files**

   a. *py.typed*

#. **Special modules**

   a. *__init__.py* 
   #. *__version__.py*

#. **Modules**

   #. **Modules for dictionaries**

      a. *dic.py*

   #. **Modules for dictionaries of arrays**

      a. *doaod.py*
      #. *doa.py*

   #. **Modules for dictionaries of callables**

      a. *doc.py**

   #. **Modules for dictionaries of dataframes**

      a. *dopddf.py*


Package Modules
===============

Overview
--------

The Modules of Package ``ut_arr`` could be classified into the follwing module types:

#. *Modules for arrays*
#. *Modules for arrays of arrays*
#. *Modules for arrays of basic objects*

******************
Modules for arrays
******************

The Module type ``Modules for arrays`` contains only the module ``arr.py``.


Module: arr.py
==============

The Module ``arr.py`` contains only the static class ``Arr``.

Class: Arr
----------

The Class ``Arr`` contains the following methods:

Arr Methods
^^^^^^^^^^^

  .. Arr-methods-label:
  .. table:: *Arr methods*

   +-----------------------+---------------------------------------------------+
   |Name                   |Short description                                  |
   +=======================+===================================================+
   |append                 |Append item to the array                           |
   +-----------------------+---------------------------------------------------+
   |append_unique          |Append item to the array if the item is not in the |
   |                       |array.                                             |
   +-----------------------+---------------------------------------------------+
   |apply_function         |Apply function with the keyword arguments to all   |
   |                       |non empty array elements.                          |
   +-----------------------+---------------------------------------------------+
   |apply_replace          |Replace source by target to all array elements.    |
   +-----------------------+---------------------------------------------------+
   |apply_str              |Apply function str to all non empty array elements.|
   +-----------------------+---------------------------------------------------+
   |encode                 |Join array elements with blank separator and encode|
   |                       |result string.                                     |
   +-----------------------+---------------------------------------------------+
   |ex_intersection        |Intersection of first array with second array.     |
   +-----------------------+---------------------------------------------------+
   |extend                 |Extend first array with second array.              |
   +-----------------------+---------------------------------------------------+
   |get_key_value          |Get next array item value without line feed for the|
   |                       |given index or the given default value if the item |
   |                       |value is identical to the given value without line |
   |                       |feeds.                                             |
   +-----------------------+---------------------------------------------------+
   |get_item               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text_spli          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |intersection           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_empty               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_not_empty           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |join_not_none          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |length                 |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |merge                  |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_from_keys_values|Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_zip             |Join elements of array of dicts.                   |
   +-----------------------+---------------------------------------------------+
   |sh_item                |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_if             |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_lower          |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_str            |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item0               |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_item0_if            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_subarray            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |to_dic                 |Show arr. of arrays created from arr. of dict.     |
   |                       |by using any key- and all value-arrays             |
   +-----------------------+---------------------------------------------------+
   |yield_items            |Convert array of dictionaries to array of          |
   |                       |arrays controlled by key- and value-switch.        |
   +-----------------------+---------------------------------------------------+

***************************
Modules for array of arrays
***************************

The Module type ``Modules for array of arrays`` contains only the module ``aoa.py``.

Module: aoa.py
==============

The Module ``aoa.py`` contains only the static class ``AoA``.

aoa.py Class: AoA
------------------

The static Class ``AoA`` contains the subsequent methods.

AoA Methods
^^^^^^^^^^^

  .. AoA-Methods-label:
  .. table:: *AoA Methods*

   +-----------------+-----------------------------------------+
   |Name             |Short description                        |
   +=================+=========================================+
   |concatinate      |Concatinate all arrays of array of arrays|
   +-----------------+-----------------------------------------+
   |csv_writerows    |Write array of arrays to csv file        |
   +-----------------+-----------------------------------------+
   |nvl              |Replace empty array of arrays            |
   +-----------------+-----------------------------------------+
   |to_aod           |Convert array of arrays to array of      |
   |                 |dictionaries using an array of keys      |
   +-----------------+-----------------------------------------+
   |to_arr_from_2cols|Convert array of arrays to array using   |
   |                 |a 2-dimensional index array              |
   +-----------------+-----------------------------------------+
   |to_doa_from_2cols|Convert array of arrays to dictionary of |
   |                 |arrays using a 2-dimensionl index array  |
   +-----------------+-----------------------------------------+
   |to_dic_from_2cols|Convert array of arrays to dictionary by |
   |                 |using a 2-dimensional index array        |
   +-----------------+-----------------------------------------+

AoA Method: concatinate
^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Concatinate all arrays of array of arrays.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-concatinate-label:
  .. table:: *Parameter of: AoA Method: concatinate*

   +-------+-----+-------+---------------+
   |Name   |Type |Default|Description    |
   +=======+=====+=======+===============+
   |aoa    |TyAoA|       |Array of arrays|
   +-------+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-concatinate-label:
  .. table:: *Return Value of: AoA Method: concatinate*

   +-------+-----+-----------+
   |Name   |Type |Description|
   +=======+=====+===========+
   |arr_new|TyArr|new array  |
   +-------+-----+-----------+

AoA Method: csv_writerows
^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Write Array of Arrays to Csv file defined by the path string 
using the function "writerows" of module "csv".

Parameter
"""""""""

  .. Parameter-of-AoA-Method-csv_writerows-label:
  .. table:: *Parameter of: AoA Method: csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |aoa   |TyAoA |Array of arrays |
   +------+------+----------------+
   |path  |TyPath|Path string     |
   +------+------+----------------+
   |kwargs|TyDic |Keyword aruments|
   +------+------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-AoA-writerows-label:
  .. table:: *Return Value of: AoA Method: csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |      |None  |                |
   +------+------+----------------+

AoA Method: nvl
^^^^^^^^^^^^^^^

Description
"""""""""""

Return the empty array if the Array of Arrays is None.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-nvl-label:
  .. table:: *Parameter of: AoA Method nvl*

   +-------+-----+-------+-------------------+
   |Name   |Type |Default|Description        |
   +=======+=====+=======+===================+
   |aoa    |TyAoA|       |Array of arrays    |
   +-------+-----+-------+-------------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-method-AoA.nvl-label:
  .. table:: *Return Value of: AoA Method: nvl*

   +-------+-----+-------------------+
   |Name   |Type |Description        |
   +=======+=====+===================+
   |aoa_new|TyAoA|new Array of arrays|
   +-------+-----+-------------------+

AoA Method: to_aod
^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to array of Dictionaries.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_aod-label:
  .. table:: *Parameter of: AoA Method: to_aod*

   +----+-----+-------+---------------+
   |Name|Type |Default|Description    |
   +====+=====+=======+===============+
   |aoa |TyAoA|       |Array of arrays|
   +----+-----+-------+---------------+
   |keys|TyArr|       |Array of keys  |
   +----+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_aod-label:
  .. table:: *Return Value of: AoA Method: to_aod*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |aod |TyAoD|array of dictionaries|
   +----+-----+---------------------+

AoA Method: to_arr_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert Array of Arrays to unique array with distinct elements by
selecting 2 columns of each Array as elements of the new array using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_arr_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_arr_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_arr_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_arr_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |arr |TyArr|Array              |
   +----+-----+-------------------+

AoA Method: to_doa_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary of unique arrays (array with distinct elements)

#. Select 2 columns of each array as key-, value-candidates of the new dictionary
   using a 2-dimensional index-array. 

#. If the new key exists then 
   the new value extends the key value as unique array, 
   
# otherwise
   the new value is assigned as unique array to the key.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_doa_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_doa_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_doa_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_doa_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |doa |TyDoA|Dictionry of arrays|
   +----+-----+-------------------+

AoA Method: to_dic_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary by selecting 2 columns of each array as
key-, value-candidates of the new dictionary if the key is not none using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_dic_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_dic_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_dic_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_dic_from_2col**

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |dic |TyDic|Dictionary |
   +----+-----+-----------+

****************************
Modules for array of objects
****************************

  .. Modules-for-array-of-dictionaries-label:
  .. table:: **Modules-for-array-of-dictionaries**

   +------+----------------+
   |Name  |Description     |
   +======+================+
   |aoo.py|Array of objects|
   +------+----------------+

Module: aoo.py
==============

The Module ``aoo.py`` contains the single static class ``AoO``;

aoo.py Class: AoO
-----------------

Methods
^^^^^^^

  .. AoO-Methods-label:
  .. table:: *AoO Methods*

   +---------+------------------------+
   |Name     |short Description       |
   +=========+========================+
   |to_unique|Concatinate array arrays|
   +---------+------------------------+

AoO Method: to_unique
^^^^^^^^^^^^^^^^^^^^^
   
Deduplicate array of objects

Parameter
"""""""""

  .. Parameter-of-AoO-Method-to_unique-label:
  .. table:: *Parameter of: AoO Method: to_unique*

   +----+-----+----------------+
   |Name|Type |Description     |
   +====+=====+================+
   |aoo |TyAoO|Array of objects|
   +----+-----+----------------+
   
Return Value
""""""""""""

  .. Return-Value-of-AoO-Method-to_unique-label:
  .. table:: *Return Value of: AoO Method: to_unique*

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|New array of objects|
   +-------+-----+--------------------+
   
**************
Module: aos.py
**************

Classes
=======

The Module ``aos.py`` contains the single static class ``AoS``;

Class: AoS
----------

AoS Methods
^^^^^^^^^^^

  .. AoS-Methods-label:
  .. table:: *AoS Methods*

   +-------------------------+------------------------------------------+
   |Name                     |short Description                         |
   +=========================+==========================================+
   |nvl                      |Replace empty array of strings            |
   +-------------------------+------------------------------------------+
   |sh_a_date                |Convert array of strings to array of dates|
   +-------------------------+------------------------------------------+
   |to_lower                 |Convert array of strings to array of      |
   |                         |lowered strings.                          |
   +-------------------------+------------------------------------------+
   |to_unique                |Deduplicate array of arrays               |
   +-------------------------+------------------------------------------+
   |to_unique_lower          |Convert array of strings to deduplicted   |
   |                         |array of lowered strings.                 |
   +-------------------------+------------------------------------------+
   |to_unique_lower_invariant|Convert array of arrays to array of arrays|
   +-------------------------+------------------------------------------+

Method: AoS.to_unique
^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-AoS-method-to_unique-label:
  .. table:: *Parameter of: AoS Method: to_unique*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoo |TyAoO|       |array of objects|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return Value-of-AoS-Method-to_unique-label:
  .. table:: *Return Value of: AoS Method: to_unique*

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|new array of objects|
   +-------+-----+--------------------+

########
Appendix
########

.. include::/docs/Logging.rst

#################
Table of Contents
#################

.. contents:: **Table of Content**
