Running PlixLab from Notebooks
==============================

If you run ``PlixLab`` in a Jupyter Notebook, you can display your presentation inline using an ``iframe``:

.. code-block:: python

   from plixlab import Slide, Presentation
   from IPython.display import HTML
   import html

   def show(slide):
       html_content = slide.get_html()
       return HTML(f"""
       <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0;">
           <iframe srcdoc='{html.escape(html_content)}'
                   style="position: absolute; top: 0; left: 0; 
                          width: 100%; height: 100%; border: none;">
           </iframe>
       </div>
       """)

   s = Slide().text(
       'I am in a Notebook',
       x=0.5, y=0.6, fontsize=0.1, color='orange'
   )

   show(s)

    