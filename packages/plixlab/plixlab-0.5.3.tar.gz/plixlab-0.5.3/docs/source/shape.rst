Shapes
========

It is possible to embed simple shapes. Currently, only arrows and squares are supported.

.. code-block:: python

  from plixlab import Slide

  Slide().shape('arrow',x=0.2,y=0.45,w=0.2,orientation=45,color=[1,0.015,0]).\
                shape('square',x=0.6,y=0.5,w=0.2,aspect_ratio=0.25).show()
  
.. import_example:: shape

All the shapes take the coordinates ``x``, ``y``, the width ``w`` (in fractional coordinates), the anti-clockwise ``orientation`` in degrees, and the ``color`` option in normalized RGB values. The ``square`` shape also takes ``aspect_ratio``.
