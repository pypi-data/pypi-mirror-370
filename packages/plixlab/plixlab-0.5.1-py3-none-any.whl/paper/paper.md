---
title: 'PlixLab: A Python package for browser-based interactive presentations'
tags:
  - Python
  - visualization
  - presentations
  - browser
authors:
  - name: Giuseppe Romano
    orcid: 0000-0003-0026-8237
    affiliation: 1
affiliations:
 - name: Massachusetts Institute of Technology, Cambridge MA, United States
   index: 1
   ror: 042nb2s44
date: 16 March 2025
bibliography: paper.bib

---

# Summary

Disseminating scientific results increasingly requires interactivity with figures and data. For example, enabling the rotation of a molecule within a presentation slide allows biologists to illustrate molecular docking mechanisms critical to drug discovery. In computational fluid dynamics, key insights are often encoded in spatial maps; allowing presenters to interactively explore these maps can lead to more engaging and effective communication. Despite these needs, mainstream presentation tools primarily support static content. `PlixLab` addresses this gap by combining the power of Python with modern JavaScript visualization libraries. `PlixLab` is a Python-based framework that generates JSON-encoded data, which is rendered interactively in the browser.


# Statement of need

`PlixLab` is a Python library for creating browser-based interactive presentations. It supports a range of plugins, including interfaces to `3jmol` [@rego20153dmol] for protein visualization, ``plotlyjs`` [@plotlyjs] and ``Bokeh`` [@Bokeh] for dynamic plots, and web embedding for integrating full scientific web applications directly into slides. Notably, when embedding a JupyterLite application [@jupyterlite], `PlixLab` enables the use of an in-slide REPL or even a full `Jupyter Notebook` [@kluyver2016jupyter], with Python running locally in the browser via `Pyodide` [@pyodide_2021]. These capabilities make `PlixLab` a unified platform for building data-centric presentations, eliminating the need to juggle multiple tools. Standard presentation features, such as animations, can also be implemented programmatically.

![Real-time update flow in PlixLab. When a Python file is modified, the server sends an SSE (1–2) to the browser, which opens a WebSocket (3) to receive binarized JSON data (4) and re-render the presentation (5), enabling seamless hot-reloading..\label{fig:example}](figure.pdf)

The graphical user interface (GUI), written in JavaScript, offers three navigation modes: single-slide view, grid view, and fullscreen presentation mode. To streamline slide development, `PlixLab` includes hot-reload functionality (see \autoref{fig:example}). When a user modifies the Python source file, a local server is triggered, which uses Server-Sent Events (SSE) to notify the browser client. The client then opens a WebSocket connection to receive the updated binary JSON data and renders the new content. This design avoids inefficient client-side polling, resulting in a responsive and seamless development experience.


# References


