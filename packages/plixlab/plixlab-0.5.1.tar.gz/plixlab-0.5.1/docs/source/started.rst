PlixLab Quickstart
==================

A minimal single-slide presentation can be created with two lines of code

.. code-block:: python

  from plixlab import Slide
  
  Slide().text('Welcome to Plix!').show()


.. import_example:: welcome

| For presentation mode, click the square button. To add a picture to the current slide, use the ``img`` tag

.. code-block:: python

  from plixlab import Slide
  

  Slide().text('Welcome to Plix!')
         .img('assets/logo.png',y=0.1,w=0.2).show()


.. import_example:: logo

| Plix features several interactive data-oriented components. Here is an example for embedding plotly data

.. code-block:: python

  from plixlab import Slide
  import plotly.express as px

  df = px.data.iris()

  fig = px.scatter(df, x="sepal_width", \
                     y="sepal_length", \
                     color="species")

  Slide().plotly(fig).show()


.. import_example:: plotly

| Lastly, to compose multiple slides you can use the ``Presentation`` class

.. code-block:: python

  from plixlab import Slide,Presentation
  import plotly.express as px

  s1 = Slide().text('Welcome to Plix!')

  df = px.data.iris()

  fig = px.scatter(df, x="sepal_width", \
                     y="sepal_length", \
                     color="species")

  s2 = Slide().plotly(fig)

  Presentation([s1,s2]).show()


.. import_example:: multislide

| For grid mode, click the top left button.
