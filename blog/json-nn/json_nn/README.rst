JSON-NN
=======

JSON parsing, powered by neural networks. What could go wrong?

Requires Tensorflow 1.0.0 or later. Please don't use this in production :)

`BLOG POST <http://anthony-zhang.me/blog/json-nn/>`__
=====================================================

The blog post contains information about design decisions, implementation details, and what all of the files in this directory are for. 

Inspiration: `FizzBuzz in Tensorflow <http://joelgrus.com/2016/05/23/fizz-buzz-in-tensorflow/>`__

Usage
-----

Quickstart: ``pip install json_nn``.

To install from source, run ``python setup.py install``.

.. code:: python

    from json_nn import JsonNN

    parser = JsonNN()
    print(parser.parse("""
    {
        "classes": [
            {
                "dates":{
                    "start_time": "11:30", "end_time": "12:50", "weekdays": "F",
                    "start_date": null, "end_date": null,
                    "is_tba": false, "is_cancelled": false, "is_closed": false
                },
                "location":{"building": "MC", "room": "3003"},
                "instructors": []
            }
        ]
    }
    """))

    # prints out the following:
    # {'classes': [{'location': {'room': '3003', 'building': 'MC'}, 'dates': {'is_cancelled': False, 'start_time': '11:30', 'start_date': None, 'is_tba': False, 'end_date': None, 'end_time': '12:50', 'weekdays': 'F', 'is_closed': False}, 'instructors': []}]}

License
-------

Copyright 2017 `Anthony Zhang (Uberi) <http://anthony-zhang.me/>`__. The source code for this library is available online at `GitHub <https://github.com/Uberi/json-nn>`__.

Tensorflow-JSON is made available under the 3-clause BSD license:

::

    Copyright (c) 2017, Anthony Zhang <azhang9@gmail.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
