3D Models
==========

Three-dimensional models can be embedded with the tag ``model3D``

.. code-block:: python

  from plixlab import Slide

  credits  = 'Blue Flower Animated" (https://skfb.ly/oDIqT) by morphy.vision is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).' 

  Slide().model3D('assets/model.glb').text(credits,y=0.1,fontsize=0.03).show()

.. import_example:: model

| where the binary format  `glb <glb>`_ is used.

