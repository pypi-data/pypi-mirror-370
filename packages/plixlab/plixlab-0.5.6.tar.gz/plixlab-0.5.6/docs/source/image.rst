Images
========

Images are added with ``img``

.. code-block:: python

  from plixlab import Slide
 
  Slide().img('assets/image.png',x=0.5,y=0.5,w=0.65).show()

.. import_example:: image

| Where the coordinates ``x`` and ``y``, as wel as the width ``w`` are in normalized coordinates. Note that the figure's proportion will be maintained. Note that the image's location can also be a Web URL.



