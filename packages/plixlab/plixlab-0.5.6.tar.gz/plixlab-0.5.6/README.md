# PlixLab 

[![PyPI version](https://badge.fury.io/py/plixlab.svg)](https://badge.fury.io/py/plixlab)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://plixlabdev.github.io/plixlab/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


**PlixLab** is a Python tool for interactive presentations that combine code execution, data visualization, and multimedia content in web-based slides.

## ✨ Key Features


🖥️ Presentations are created programmatically

🌐 Runs in any modern browser 

🔬 Built for researchers, educators, and data scientists

🚀 Supports live Python code execution within presentations

📊 Seamless integration with Plotly, Bokeh, and Matplotlib

🧬 Supports 3D protein visualization

📖 Automatically formats citations 


⚡ Enables live editing with instant preview updates

## 📚 Documentation

- **[Documentation](https://plixlabdev.github.io/plixlab/)** - Complete guide, API reference, and examples

## 🎯 Use Cases

- **Research Presentations**: Interactive data exploration during talks
- **Educational Materials**: Live coding demonstrations and tutorials
- **Conference Talks**: Engaging presentations with real-time analysis

## 🚀 Quick Start

### Installation

```bash
pip install plixlab
```

### Getting started

```python
from plixlab import Slide

# Create a simple slide
slide = Slide()
slide.text("Welcome to PlixLab!", y=0.7, color="white")
slide.text("Interactive Scientific Presentations", y=0.3, color="lightblue")
slide.show()
```


## 💡 Examples
### Interactive Plot Example

```python
import plotly.express as px
from plixlab import Slide

# Create data visualization
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

# Add to slide
slide = Slide()
slide.plotly(fig, x=0.1, y=0.1, w=0.8, h=0.8)
slide.show()
```


### Multi-slide Presentations
```python

from plixlab import Presentation

s1 = Slide().text('Slide 1')
s2 = Slide().text('Slide 2')

pres = Presentation([s1, s2], title="My Presentation")
pres.show()
```

### Molecular Visualization
```python
from plixlab import Slide

Slide().molecule('9B31').show()
```



## 📄 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.


