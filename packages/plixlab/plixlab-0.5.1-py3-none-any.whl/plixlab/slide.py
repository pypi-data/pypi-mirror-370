"""
PlixLab Slide Module

This module contains the Slide class for creating individual presentation slides.
"""

import io
from typing import Any, Dict, List, Union, TYPE_CHECKING
import numpy as np
import plotly.io as pio
from plotly.graph_objs import Figure as plotly_figure
from .utils import get_style, process_plotly, process_bokeh
from .shape import run as shape
from . import Bibliography
from bokeh.embed import json_item
from .presentation import Presentation
from bokeh.plotting import figure as bokeh_figure
from matplotlib.figure import Figure as matplotlib_figure


class Slide:
    """
    Individual slide for presentations with various content types.

    A Slide can contain multiple components like text, images, plots, videos,
    3D models, and interactive elements. Each component can have custom animations.

    """


    def __init__(self, background: str = "#303030") -> None:

        self._content: List[Dict[str, Any]] = []
        self._style: Dict[str, str] = {"backgroundColor": background}
        self._animation: List[Dict[str, Any]] = []


    def _get(self, slide_ID: str) -> Dict[str, Any]:
        """
        Generate slide data with the specified ID.

        Args:
            slide_ID: Unique identifier for this slide, provided by the Presentation class.

        Returns:
            Dictionary containing slide data with children, style, animation, and title
        """

        animation = self._process_animations()

        children = {slide_ID + "_" + str(k): tmp for k, tmp in enumerate(self._content)}

        data = {
            "children":  children,
            "style":     self._style,
            "animation": animation

        }

        return {slide_ID: data}
    

    def _add_animation(self, **argv: Any) -> None:
        """
        Add animation sequence to the current component.

        Args:
            **argv: Animation parameters including:
                - animation (list/int): Animation sequence definition
        """

        animation = argv.setdefault("animation", [1])
        self._animation.append(animation)

    def _process_animations(self) -> List[Dict[str, bool]]:
        """
        Process animation sequences for this slide.

        Converts animation definitions into event sequences that control
        component visibility during slide transitions.

        Returns:
            list: List of animation events for each click/transition
        """

        # Convert animation numbers to lists
        tmp = []
        for x in self._animation:
            if not isinstance(x, list):
                # Convert number to animation sequence
                a = []
                if isinstance(x, int):
                    for i in range(x):
                        a.append(0)
                    a.append(1)
                else:
                    # Handle non-integer, non-list case
                    a.append(1)
                tmp.append(a)
            else:
                tmp.append(x)

        # Expand animations to same length
        tmp2 = [len(i) for i in tmp]
        if len(tmp2) > 0:
            n_events = max(tmp2)
            for k, i in enumerate(tmp):
                for j in range(n_events - len(i)):
                    # tmp[k] is guaranteed to be a list at this point
                    assert isinstance(tmp[k], list)
                    tmp[k].append(1)

        # Create animation events
        animation = np.array(tmp).T

        slide_events = []
        for idx, click in enumerate(animation):
            event = {}
            for c, status in enumerate(click):
                C_id = f"{c}"
                value = not (bool(status))
                event.update({C_id: value})
            slide_events.append(event)

        return slide_events

    def cite(self, 
             key:       Union[str, List[str]],
             bibfile:   str = 'biblio.bib', 
             fontsize:  float = 0.03, 
             color:     str = "white",
             animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add citation(s) to the slide. Multiple citations are stacked vertically.

        :param key: Citation key(s) to format and display
        :param bibfile: Path to the bibliography file. Defaults to 'biblio.bib'.
        :param fontsize: Font size for citations. Defaults to 0.03.
        :param color: Font color for citations. Defaults to 'white'.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click (e.g., [1, 0, 1] shows the component on the first and third clicks). An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """

        if not isinstance(key, list):
            keys = [key]
        else:
            keys = key

        for i, key in enumerate(keys):
            text = Bibliography.format(key,bibfile)

            print(f"{i * 4 + 1}%")
          
            style = {"color":color,"position": "absolute", "left": "1%", "bottom": f"{i * 4 + 1}%"}
            
            tmp = {
                "type":     "Markdown",
                "text":     text,
                "fontsize": fontsize,
                "style":    style,
            }

            self._content.append(tmp)
            self._animation.append(animation)

        return self

    def text(self, 
             text:      str, 
             x:         float = 0.5,
             y:         float = 0.5,
             w:         Union[float,str] = 'auto',
             fontsize:  float= 0.05,
             halign:    str = "center",
             valign:    str = "center",
             animation: Union[List[bool], int] = [1],
             color:     str = "white") -> 'Slide':
        """
        Add text content to the slide.

        Adds markdown-formatted text with customizable styling and positioning.

        :param text: Text content (supports markdown formatting)
        :param x: Horizontal position (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (fraction of slide). Defaults to None, which makes it auto.
        :param fontsize: Font size as fraction of screen. Defaults to 0.05.
        :param halign: Horizontal alignment ('left', 'center', 'right'). Defaults to 'center'.
        :param valign: Vertical alignment ('top', 'center', 'bottom'). Defaults to 'center'.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :param color: Text color. Defaults to 'white'.
        :return: The slide object (self), allowing method chaining.
        """
 
        style =  {'color':    color,
                  'whiteSpace': 'nowrap',
                  'fontSize': fontsize}
     
        
        style.update(get_style(x,y,w,'auto',halign,valign))

        component = {
            "type"    : "Markdown",
            'display' : "flex",
            "text"    : text,
            "fontsize": fontsize,
            "style"   : style
        }

        self._content.append(component)
        self._animation.append(animation)
        return self

    def model3D(self, filename: str, 
                 x: float = 0.5,
                 y: float = 0.5, 
                 w: float = 0.8, 
                 h: float = 0.8, 
                 animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a 3D model to the slide.

        :param filename: Path to the 3D model file
        :param x: Horizontal position of the center of the model (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the model (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param h: Height (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """

       
        with open(filename, "rb") as f:
            url = f.read()

        style = get_style(x, y, w, h, "center", "center")    

        component = {
            "type":      "model3D",
            "className": "interactable componentA",
            "src":        url,
            "style":      style,
        }

        self._content.append(component)
        self._animation.append(animation)
        return self

    def img(self, url: str, x: 
            float = 0.5, 
            y: float = 0.5,
            w: float = 0.8,
            h: Union[float,str] = 'auto', 
            animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add an image to the slide.

        Supports both local file paths and URLs. Local files are read and embedded.

        :param url: Path to local image file or URL to remote image
        :param x: Horizontal position of the center of the image (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the image (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param h: Height (0-1, relative to slide). Defaults to 'auto', which keeps proportions based on width.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        
        Note:
            If the URL starts with "http", it is treated as a remote image. Otherwise, it is read as a local file.
        """
            

        if url[:4] != "http":
            with open(url, "rb") as f:
                url_content: Union[bytes, str] = f.read()
        else:
            url_content = url

        style = get_style(x, y, w, h, "center", "center")
 
        component = {"type": "Img",
                     "src":   url_content,
                     "style": style}

        self._content.append(component)
        self._animation.append(animation)
        return self

    def shape(self, 
              shapeID: str,
              orientation: float = 0,
              color: Union[str, List[float]] = "#FFFFFF",
              aspect_ratio: float = 1,
              x: float = 0.5,
              y: float = 0.5,
              w: float = 0.2,
              animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a generated shape to the slide.

        :param shapeID: Identifier for the shape type to generate ('arrow' or 'square').
        :param orientation: Rotation angle in degrees. Defaults to 0.
        :param color: Shape color as hex string (e.g., "#FF0000") or RGB tuple (0-1 range). Defaults to #FFFFFF (white).
        :param aspect_ratio: For 'square' shapes, height/width ratio. Defaults to 0.5.
        :param x: Horizontal position of the center of the shape (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the shape (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width of the shape as a fraction of slide width. Defaults to 0.2.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """
        style = get_style(x, y, w, 'auto', "center", "center")

        image = shape(shapeID,color=color, 
                      orientation=orientation,
                      aspect_ratio=aspect_ratio)

        component = {"type":  "Img",
                     "src":   image,
                     "style": style}

        self._content.append(component)
        self._animation.append(animation)
        return self
    


    def youtube(self, videoID: str, 
                x: float = 0.5,
                y: float = 0.5,
                w: float = 0.4,
                animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a YouTube video to the slide.

        :param videoID: YouTube video ID (the part after 'v=' in YouTube URLs)
        :param x: Horizontal position of the center of the video (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the video (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.4.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """
        h = w/0.5625  # Default aspect ratio for YouTube videos (16:9)
       
        style = get_style(x, y, w, h, "center", "center")

        url = f"https://www.youtube.com/embed/{videoID}?controls=0&rel=0"

        component = {
                      "type"    : "Iframe",
                     "className": "interactable",
                           "src": url,
                         "style": style,
        }
        self._content.append(component)
        self._animation.append(animation)
        return self

    def matplotlib(self,
                   fig: matplotlib_figure, 
                   x: float = 0.5,
                   y: float = 0.5,
                   w: float = 0.8,
                   h: Union[float, str] = 'auto',
                   animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a matplotlib figure to the slide.

        :param fig: Matplotlib figure object
        :param x: Horizontal position of the center of the figure (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the figure (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param h: Height (0-1, relative to slide or 'auto'). Defaults to 'auto', which keeps proportions based on width.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """

        style = get_style(x, y, w, h, "center", "center")
                   
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        buf.seek(0)
        url = buf.getvalue()
        buf.close()

        component= {"type": "Img",
                    "src":   url, 
                    "style": style}


        self._content.append(component)
        self._animation.append(animation)
        return self


    def bokeh(self, graph: bokeh_figure, 
                    x: float = 0.5,
                    y: float = 0.5,
                    w: float = 0.8,
                    animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a Bokeh plot to the slide.

        :param graph: Bokeh plot object
        :param x: Horizontal position of the center of the plot (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the plot (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """
        process_bokeh(graph)
        
        
        style = get_style(x,y,w,w, halign="center", valign="center")
    
        item  = json_item(graph)

        component = {"type": "Bokeh", 
                     "graph": item, 
                     "style": style}

        self._content.append(component)
        self._animation.append(animation)
        return self

    def plotly(self, fig: plotly_figure, 
                x: float = 0.5,
                y: float = 0.5,
                w: float = 0.8,
                animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a Plotly graph to the slide.

        :param fig: Plotly figure object or path to JSON file (string)
        :param x: Horizontal position of the center of the plot (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the plot (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """
       
        
        if isinstance(fig, str):
            fig = pio.read_json(fig + ".json")

        style = get_style(x,y,w,w,'center','center')
        fig = process_plotly(fig)
        fig_json = fig.to_json()

        component = { "type":   "Plotly",
                     "figure":  fig_json,
                      "style":  style}


        self._content.append(component)
        self._animation.append(animation)
        return self

    def molecule(self, structure: str,
                    x: float = 0.5,
                    y: float = 0.5,
                    w: float = 0.8,
                    animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Add a molecular structure visualization to the slide.

        :param structure: Molecular structure from the PDB database
        :param x: Horizontal position of the center of the structure (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the center of the structure (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """
        
        style = get_style(x, y, w, w, "center", "center")

        component = {
            "type":           "molecule",
            "style":           style,
            "structure":       structure,
            "backgroundColor": self._style["backgroundColor"],
        }

        self._content.append(component)
        self._animation.append(animation)
        return self

    def python(self,x: float = 0.5,
                y: float = 0.5,
                w: float = 0.8,
                h: float = 0.8, 
                animation: Union[List[bool], int] = [1
              ]) -> 'Slide':
        """
        Add an interactive Python REPL to the slide.

        :param x: Horizontal position of the REPL (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the REPL (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param h: Height (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """

        style = get_style(x, y, w, h, "center", "center")
        url = (
            "https://jupyterlite.readthedocs.io/en/stable/_static/repl/"
            "index.html?kernel=python&theme=JupyterLab Dark&toolbar=1"
        )

        component = {"type": "Iframe", 
                     "src":  url, 
                     "style": style}

        self._content.append(component)
        self._animation.append(animation)
        return self

    def embed(self, url: str,
              x: float = 0.5,
              y: float = 0.5,
              w: float = 0.8,
              h: float = 0.8,
              animation: Union[List[bool], int] = [1]) -> 'Slide':
        """
        Embed external content via iframe.

        :param url: URL of the content to embed
        :param x: Horizontal position of the iframe (0-1, left to right). Defaults to 0.5 (center).
        :param y: Vertical position of the iframe (0-1, bottom to top). Defaults to 0.5 (center).
        :param w: Width (0-1, relative to slide). Defaults to 0.8.
        :param h: Height (0-1, relative to slide). Defaults to 0.8.
        :param animation: Animation sequence for this component. A list of 1s and 0s specifies visibility at each click. An integer specifies the number of clicks to wait before showing the component.
        :return: The slide object (self), allowing method chaining.
        """

        style = get_style(x, y, w, h, "center", "center")

        component = {"type": "Iframe", 
                      "src": url,
                     "style": style}


        self._content.append(component)
        self._animation.append(animation)
        return self

    def show(self, **kwargs: Any) -> None:
        """
        Show the slide as a single-slide presentation.

        Args:
            **kwargs: Additional arguments passed to the presentation show method

        Returns:
            None: Opens presentation in web browser
        """
        from .presentation import Presentation

        Presentation([self]).show(**kwargs)

    def save_standalone(self, directory: str = "output") -> None:
        """
      
        Creates a self-contained presentation directory with PlixLab.
     

        Args:
            directory (str): Output directory name. Defaults to 'output'.

        Note:
            - PlixLab core assets (JS/CSS) are saved locally
            - Third-party libraries (Plotly, Bokeh, etc.) use CDN links
        """

        Presentation([self]).save_standalone(directory=directory)

       

    def save_binary(self, filename: str = "data") -> None:
        """
        Save presentation data to a .plx file.

        Saves the presentation data in a binary format that can be loaded later.

        Args:
            filename (str): Output filename without extension. Defaults to 'data'.
        """    

        Presentation([self]).save_binary(filename=filename)

       

    def get_data(self) -> dict:
        """
        Get the slide data (as a dict) as a presentation.

        Returns:
            dict: Slide data formatted as a single-slide presentation
        """

        return Presentation([self]).get_data()
    
    def get_binary(self,title:str='default') -> bytes:
        """
        Get the binary data as a single-slide presentation.

        Returns:
            bytes: Binarized single-presentation data
        """
        return Presentation([self],title).get_binary()
     
