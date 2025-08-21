Hot reload
===========

When you show a presentation, any change to the document is automatically applied to the live presentation while the local server is running. Hot reload is always enabled to provide a seamless development experience.

.. code-block:: python

   from plixlab import Slide

   # Hot reload is automatically enabled
   Slide.text('Example Hot Reload').show()

The hot reload system uses Server-Sent Events (SSE) to notify the browser when changes occur, then opens a WebSocket connection to receive updated presentation data. This ensures responsive updates without inefficient polling.
