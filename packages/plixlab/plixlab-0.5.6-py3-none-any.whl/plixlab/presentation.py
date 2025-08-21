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
from bs4 import BeautifulSoup
import base64
import webbrowser



class Presentation:
    """
    Container class for multi-slide presentations.

    A Presentation manages multiple slides, handles animations between slides,
    and provides methods for displaying and saving the presentation.
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

    def get_title(self) -> str:
        """
        Get the title of the presentation.

        :return: Title of the presentation
        """
        return self.title

    def show(self, hot_reload:bool=False,carousel:bool=False) -> None:
        """
        Display the presentation in a web browser.

        Launches a local server.

        :param hot_reload: Enable autoreload for development (default False)
        :param carousel: Enable carousel mode for slides (default False)
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
        Save presentation data to a binary .plx file.

        Saves the presentation data in a binary format.

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

        return self.slides

    def get_html(self, filename: str = None) -> str:
        """

        Get a self-contained HTML code (minus external libraries).

        :param filename: Output filename without extension. If not provided, no file will be saved.

        """


        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(script_dir, "web")
        src = os.path.join(base_path, "index.html")

        

        def is_local(path):
           return not path.startswith(("http://", "https://", "//"))

        with open(src, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")


        # Inline favicon
        for link_tag in soup.find_all("link", rel=lambda x: x and "icon" in x):
         href = link_tag.get("href")
         if href and is_local(href):
           icon_path = os.path.join(base_path, href)
           if os.path.exists(icon_path):
            with open(icon_path, "rb") as icon_file:
                encoded_icon = base64.b64encode(icon_file.read()).decode("ascii")
            ext = os.path.splitext(icon_path)[1].lstrip(".").lower()
            mime_type = "image/x-icon" if ext == "ico" else f"image/{ext}"
            link_tag["href"] = f"data:{mime_type};base64,{encoded_icon}"
        
        # Inline local CSS
        for link_tag in soup.find_all("link", rel="stylesheet"):
           href = link_tag.get("href")
           if href and is_local(href):
             local_path = os.path.join(base_path, href)
             if os.path.exists(local_path):
              with open(local_path, "r", encoding="utf-8") as css_file:
                css_content = css_file.read()
              style_tag = soup.new_tag("style")
              style_tag.string = css_content
              link_tag.replace_with(style_tag)

        # Inline local JavaScript
        for script_tag in soup.find_all("script", src=True):
          src_attr = script_tag.get("src")
          if src_attr and is_local(src_attr):
           if os.path.basename(src_attr) == "load.js":
            script_tag.decompose()  # remove entirely
            continue
          local_path = os.path.join(base_path, src_attr)
          if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as js_file:
                js_content = js_file.read()
            # Keep type="module" if it was present
            new_script_tag = soup.new_tag("script", type=script_tag.get("type"))
            new_script_tag.string = js_content
            script_tag.replace_with(new_script_tag)

        # Inject JSON and render call at end of body
        json_script = soup.new_tag("script")
        bytes_literal = ",".join(str(b) for b in self.get_binary())
        json_script.string = f"""
window.addEventListener('load', function() {{
    const data = new Uint8Array([{bytes_literal}]);
    const unpackedData = msgpack.decode(data);
    window.render_slides(unpackedData);
}});
"""
        soup.body.append(json_script)

        
        # Save output HTML
        if filename:
         with open(f'{filename}.html', "w", encoding="utf-8") as f:
          f.write(str(soup))


        return str(soup)




    def get_binary(self) -> bytes:
        """
        Get presentation data in binary format.

        Returns:
            bytes: Binarized presentation data
        """
       

        normalized_data = normalize_dict(self.slides)
        return msgpack.packb(normalized_data)
       
    
