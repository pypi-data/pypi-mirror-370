Plotly
========

Interactive plots from `Plotly <plotly_web>`_ can be embedded with ``plotly`` 

.. code-block:: python

  from plixlab import Slide
  import plotly.express as px

  df = px.data.iris()

  fig = px.scatter(df, x="sepal_width", \
                     y="sepal_length", \
                     color="species")

  Slide().plotly(fig).show()

.. import_example:: plotly

.. _plotly_web: https://plotly.com/
