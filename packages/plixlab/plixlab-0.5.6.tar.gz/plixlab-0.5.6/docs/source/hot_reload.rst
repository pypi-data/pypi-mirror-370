Hot reload
===========

``PlixLab`` features ``hot_reload``, where you can see live changes as you edit the source files of your presentations. To enable this feature, use the option ``hot_reload=True``, e.g.

.. code-block:: python

   from plixlab import Slide

   # Hot reload is automatically enabled
   Slide.text('Example Hot Reload').show(hot_reload=True)

