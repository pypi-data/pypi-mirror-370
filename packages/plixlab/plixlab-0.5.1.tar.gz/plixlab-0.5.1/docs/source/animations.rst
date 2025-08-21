Animations
================================

You can specify the order of appearing of an individual component with the option ``animation``

.. code-block:: python

   from plixlab import Slide

   Slide().text('Text #1',y=0.7).\
           text('Text #2',y=0.5,animation= 1).\
           text('Text #3',y=0.3,animation= 2).show()


You can check the animations by clicking on the full-screen button.

.. import_example:: animation

   

| If no ``animation`` is provided, the components will always be displayed. To see the animation you have to enter full-screen mode. For a more generic animation, i.e. when components appear and disappear, specify ``animation`` as a binary vector

.. code-block:: python

   Slide().text('Text #1',y=0.7).\
           text('Text #2',y=0.5,animation=[1,0,1]).\
           text('Text #3',y=0.3,animation=2).show()









