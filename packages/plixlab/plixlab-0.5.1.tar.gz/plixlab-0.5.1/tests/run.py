import msgpack
import numpy as np
import matplotlib.pyplot as plt
import os
import pytest
from plixlab import Slide, Presentation
from plixlab.utils import normalize_dict
import plotly.express as px
from bokeh.plotting import figure, show
import pandas as pd
from typing import Dict, Any


# Get the directory containing this test file
test_dir = os.path.dirname(os.path.abspath(__file__))
prefix = os.path.join(test_dir, 'reference')
assets_prefix = os.path.join(test_dir, 'assets')

def load_data(filename: str) -> Dict[str, Any]:
    """
    Load reference data from a file.
    """
    with open(f'{prefix}/{filename}.plx', 'rb') as f:
        return normalize_dict(msgpack.unpackb(f.read()))

def generate_or_validate(slide: Slide,filename: str,pytestconfig: Any) -> None:
    """
    Handle generating or validating reference data for a given slide.
    """
    generate_references = pytestconfig.getoption("--generate-references")
  
    if generate_references:
      
        # Generate and save reference data
        path = f'{prefix}/{filename}'
        slide.save_binary(path)
        print(f"Reference data for {path} generated.")
    else:
        # Validate against reference data
        data = normalize_dict(slide.get_data())
        reference = load_data(filename)

        assert data == reference, f"Data does not match the reference for {filename}!"


def test_citation(pytestconfig: Any) -> None:
    """
    Test citation functionality.
    """
   
    slide = Slide().cite(key='einstein1935',bibfile = f'{assets_prefix}/biblio.bib')

    generate_or_validate(slide,'citation',pytestconfig)


def test_welcome(pytestconfig):
   """
   Test welcome functionality.
   """

   slide = Slide().text('Welcome to Plix!')

   generate_or_validate(slide,'welcome',pytestconfig)


def test_animation(pytestconfig):
   """
   Test animation.
   """
   p = Slide().text('Text #1',y=0.7).\
     text('Text #2',y=0.5,animation= 1).\
     text('Text #3',y=0.3,animation= 2)

   generate_or_validate(p,'animation',pytestconfig)

def test_logo(pytestconfig):
   """
   Test logo functionality.
   """

   slide = Slide().text('Welcome to Plix!').img(f'{assets_prefix}/logo.png',y=0.2,w=0.2)

   generate_or_validate(slide,'logo',pytestconfig)

def test_markdown(pytestconfig):
    """
    Test markdown functionality.
    """

    slide = Slide().text(
        '<u> This </u> **text** is *really important*.', 
        x=0.5, y=0.6, fontsize=0.1, color='orange'
    )
    generate_or_validate(slide,'markdown',pytestconfig)

def test_equation(pytestconfig):
    """
    Test equation.
    """
    
    slide = Slide().text(
        r'''$-C\frac{\partial T}{\partial t} - \nabla \cdot \left(\kappa \nabla T\\right) = Q$''')

    generate_or_validate(slide,'equation',pytestconfig)



def test_image(pytestconfig):
    """
    Test image functionality.
    """
    
    slide = Slide().img(f'{assets_prefix}/image.png',x=0.5,y=0.5,w=0.65)

    generate_or_validate(slide,'image',pytestconfig)


def test_matplotlib(pytestconfig):
    """
    Test matplotlib functionality.
    """
    
    style_file = f'{assets_prefix}/mpl_style_light'
    
    if os.path.exists(style_file):
     plt.style.use(style_file)
    else:
     print(f"Style file not found: {style_file}")
  
    # Create data points
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
  
    # Plot the sine wave
    fig = plt.figure(figsize=(8, 4.5))
    plt.plot(x, y, label='Sine Wave')
    plt.title('Simple Sine Wave')
    plt.xlabel('x values')
    plt.ylabel('y values')

    slide = Slide().matplotlib(fig)


    generate_or_validate(slide,'matplotlib',pytestconfig)

def test_shape(pytestconfig):
   """
   Test shape functionality.
   """


   slide = Slide().shape('arrow',x=0.2,y=0.45,w=0.2,orientation=45,color=[1,0.015,0]).\
                  shape('square',x=0.6,y=0.5,w=0.2,aspect_ratio=0.25)

   generate_or_validate(slide,'shape',pytestconfig)


def test_embed(pytestconfig):
   """
   Test embed functionality.
   """
   url = 'https://examples.pyscriptapps.com/antigravity/latest/'
   slide = Slide().embed(url)

   generate_or_validate(slide,'embed',pytestconfig)


def test_youtube(pytestconfig):
   """
   Test youtube functionality.
   """

   slide = Slide().youtube('zDtx6Z9g4xA')

   generate_or_validate(slide,'youtube',pytestconfig)


def test_plotly(pytestconfig):
   """
   Test plotly functionality.
   """

   df = px.data.iris()

   fig = px.scatter(df, x="sepal_width", \
                   y="sepal_length", \
                   color="species")

   slide = Slide().plotly(fig)

   generate_or_validate(slide,'plotly',pytestconfig)

def test_bokeh(pytestconfig):
   """
   Test bokeh functionality.
   """

   x = [1, 2, 3, 4, 5]
   y = [6, 7, 2, 4, 5]

   p = figure(
   x_axis_label='x',
   y_axis_label='y'
   )

   p.line(x, y, legend_label="Temp.", line_width=2)

   slide = Slide().bokeh(p)

   generate_or_validate(slide,'bokeh',pytestconfig)

def test_molecule(pytestconfig):
   """
   Test molecule functionality.
   """

   slide = Slide().molecule('9B31')

   generate_or_validate(slide,'molecule',pytestconfig)

def test_python(pytestconfig):
   """
   Test python functionality.
   """

   slide = Slide().python()

   generate_or_validate(slide,'python',pytestconfig)

def test_model(pytestconfig):
   """
   Test model functionality.
   """

   credits  = 'Blue Flower Animated" (https://skfb.ly/oDIqT) by morphy.vision is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).'

   slide = Slide().model3D(f'{assets_prefix}/model.glb').text(credits,y=0.1,fontsize=0.03)

   generate_or_validate(slide,'model',pytestconfig)                 


def test_demo(pytestconfig):
   """
   Test demo.
   """

   text  = 'Blue Flower Animated" (https://skfb.ly/oDIqT) by morphy.vision is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).'

   s0 = Slide().model3D(f'{assets_prefix}/model.glb',y=0.4).text(text,y=0.9,fontsize=0.02,w=0.3).text('Interact with it!',y=0.1,color='orange',fontsize=0.06)



   df = px.data.iris()

   fig = px.scatter(df, x="sepal_width", \
                   y="sepal_length", \
                   color="species")


   s1 = Slide().plotly(fig,y=0.6).text('Zoom in!',y=0.1,color='orange',fontsize=0.06)

   s2 = Slide().molecule('9B31',y=0.6).text('Rotate it!',y=0.1,color='orange',fontsize=0.06)

   s3 = Slide().python(y=0.57,x=0.45).text('Type code!',y=0.1,color='orange',fontsize=0.06)

   presentation = Presentation([s0,s1,s2,s3])

   generate_or_validate(presentation,'demo',pytestconfig)


def test_multislide(pytestconfig):
   """
   Test presentation functionality.
   """


   s1 = Slide().text('Welcome to Plix!')

   df = px.data.iris()

   fig = px.scatter(df, x="sepal_width", \
                   y="sepal_length", \
                   color="species")

   s2 = Slide().plotly(fig)

   presentation = Presentation([s1,s2])

   generate_or_validate(presentation,'multislide',pytestconfig)


if __name__ == '__main__':

    # Simulate pytestconfig for testing manually
    class MockPytestConfig:
        def getoption(self, option):
            if option == "--generate-references":
                return True  # Change to True to generate references

    # Create a mock pytestconfig instance
    pytestconfig = MockPytestConfig()

   #  # Run the test function
   #  test_citation(pytestconfig)
   #  test_markdown(pytestconfig)
   #  test_equation(pytestconfig)
   #  test_image(pytestconfig)
   #  test_matplotlib(pytestconfig)
   #  test_shape(pytestconfig)
   #  test_embed(pytestconfig)
   #  test_youtube(pytestconfig)
   #  test_plotly(pytestconfig)
   #  test_bokeh(pytestconfig)
   #  test_molecule(pytestconfig)
   #  test_multislide(pytestconfig)
   #  test_animation(pytestconfig)
   #  test_welcome(pytestconfig)
   #  test_logo(pytestconfig)
   #  test_python(pytestconfig)
   #  test_model(pytestconfig)



