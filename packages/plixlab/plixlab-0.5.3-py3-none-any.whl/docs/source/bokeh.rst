Bokeh
========

Interactive plots from `Bokeh <bokeh_web>`_ can be embedded with ``bokeh`` 

.. code-block:: python

 from plixlab import Slide
 from bokeh.plotting import figure, show

 x = [1, 2, 3, 4, 5]
 y = [6, 7, 2, 4, 5]

 p = figure(
    x_axis_label='x',
    y_axis_label='y'
 )

 p.line(x, y, legend_label="Temp.", line_width=2)

 Slide().bokeh(p).show()

.. import_example:: bokeh

.. _bokeh_web: https://docs.bokeh.org/en/3.0.0/index.html
