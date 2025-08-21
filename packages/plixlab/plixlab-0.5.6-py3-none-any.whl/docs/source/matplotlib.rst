Matplotlib
==========



.. code-block:: python

  import numpy as np
  import matplotlib.pyplot as plt
  from plixlab import Slide

  # Create data points
  x = np.linspace(0, 2 * np.pi, 100)
  y = np.sin(x)

  # Plot the sine wave
  fig = plt.figure(figsize=(8, 4.5))
  plt.plot(x, y, label='Sine Wave')
  plt.title('Simple Sine Wave')
  plt.xlabel('x values')
  plt.ylabel('y values')

  Slide().matplotlib(fig).show()

.. import_example:: matplotlib

| Note that under the hood, a PNG figure is created.
