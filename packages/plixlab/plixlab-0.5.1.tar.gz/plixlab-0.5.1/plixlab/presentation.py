"""
PlixLab Presentation Module

This module contains the Presentation class for managing multi-slide presentations.
"""

import os
import shutil
from typing import List, Dict, Any
import msgpack
import nest_asyncio
from .utils import normalize_dict
from .server import run


class Presentation:
    """
    Container class for multi-slide presentations.

    A Presentation manages multiple slides, handles animations between slides,
    and provides methods for displaying and saving the complete presentation.
    """

    def __init__(self, slides: List[Any] = [], title: str = "default") -> None:
        self.title = title

        data = {}
        for s, slide in enumerate(slides):
            data.update(slide._get(f"slide_{s}"))

        self.slides = data
        """
        Initialize a Presentation object.

        :param slides: List of Slide objects to include in the presentation
        :param title: Title of the presentation. Defaults to 'default'.
        """

   

    def show(self, hot_reload:bool=False,carousel:bool=False) -> None:
        """
        Display the presentation in a web browser.

        Launches a local server.

        Args:
            hot_reload (bool): Enable autoreload for development (default False)
            carousel (bool): Enable carousel mode for slides (default False)
        """
        nest_asyncio.apply()
        run(self.slides, hot_reload=hot_reload, carousel=carousel)
        """
        Display the presentation in a web browser.

        Launches a local server.

        :param hot_reload: Enable autoreload for development (default False)
        :param carousel: Enable carousel mode for slides (default False)
        """

    def save_standalone(self, directory: str = "output") -> None:
        """
      
        Creates a self-contained presentation directory with PlixLab.
     

        Args:
            directory (str): Output directory name. Defaults to 'output'.

        Note:
            - PlixLab core assets (JS/CSS) are always saved locally
            - Third-party libraries (Plotly, Bokeh, etc.) use CDN links
        """
        """
        Creates a self-contained presentation directory with PlixLab.

        :param directory: Output directory name. Defaults to 'output'.

        Note:
            - PlixLab core assets (JS/CSS) are always saved locally
            - Third-party libraries (Plotly, Bokeh, etc.) use CDN links
        """

        # Copy the entire web directory to the output location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(script_dir, "web")
        dst = os.path.join(os.getcwd(), directory)


        # Create a new directory (don't delete existing)
        os.makedirs(dst, exist_ok=True)
        
        # Copy all web files
        shutil.copytree(src, dst, dirs_exist_ok=True)

        # Copy load_standalone.js as load.js for standalone functionality
        load_standalone_path = os.path.join(dst, "assets", "js", "load_standalone.js")
        load_path = os.path.join(dst, "assets", "js", "load.js")
        if os.path.exists(load_standalone_path):
            shutil.copy2(load_standalone_path, load_path)

        # Save the presentation data
        self.save_binary(dst + "/data")

    def save_binary(self, filename: str = "data") -> None:
        """
        Save presentation data to a .plx file.

        Saves the presentation data in a binary format that can be loaded later.

        Args:
            filename (str): Output filename without extension. Defaults to 'data'.
        """    
        """
        Save presentation data to a .plx file.

        Saves the presentation data in a binary format that can be loaded later.

        :param filename: Output filename without extension. Defaults to 'data'.
        """

        binary_data = self.get_binary()

        with open(filename + ".plx", "wb") as file:
            file.write(binary_data)


    def get_data(self) -> Dict[str, Any]:
        """
        Get the presentation data dictionary.

        Returns:
            dict: Complete presentation data including all slides and animations
        """
        """
        Get the presentation data dictionary.

        :return: Complete presentation data including all slides and animations
        """

        return self.slides

    def get_title(self) -> str:
        """
        Get the presentation title.

        Returns:
            str: The title of the presentation
        """
        """
        Get the presentation title.

        :return: The title of the presentation
        """

        return self.title

    def get_binary(self) -> bytes:
        """
        Get presentation data in binary format.

        Returns:
            bytes: Binarized presentation data
        """
        """
        Get presentation data in binary format.

        :return: Binarized presentation data
        """

        normalized_data = normalize_dict(self.slides)
        return msgpack.packb(normalized_data)
       
    
