Markdown
========

The tag ``text`` accepts Markdown syntax, e.g.

.. code-block:: python

  from plixlab import Slide
  
  Slide().text('<u> This </u> **text** is *really important*.',x=0.5,\
                 fontsize=0.1,color='orange').show()


.. import_example:: markdown


Equations can be added using ``Latex`` syntax, e.g.


.. code-block:: python

  from plix import Slide
  
  Slide().text(r'''$-C\frac{\partial T}{\partial t} - \nabla \cdot \left(\kappa \nabla T\\right) = Q$''').show()
   

.. import_example:: equation




