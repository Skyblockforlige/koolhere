---
layout: default
title: Auto-Handwriting Generator
---
 
[← Back to portfolio](../)
 
# Auto-Handwriting Generator
 
A Flask API that converts text into realistic handwriting and physically draws it on paper using an [AxiDraw](https://axidraw.com/) pen plotter. Text is rendered to an SVG by a neural handwriting-synthesis model, cleaned up, then plotted.
 
## How it works
 
1. **Generate** — input text is passed to a handwriting-synthesis model that produces a handwritten-style SVG.
2. **Clean** — non-stroke elements are stripped out and the SVG is resized so it plots correctly.
3. **Plot** — the cleaned SVG is sent to the AxiDraw to draw on real paper.
## Highlights
 
- REST API built with Flask for generating and plotting handwriting
- Automatic line wrapping with a configurable character limit
- Adjustable handwriting style and bias
- Thread-safe plotting (one job at a time) with live status tracking
**Tech:** Python, Flask, neural handwriting synthesis, AxiDraw
 
[View the code on GitHub »](https://github.com/Skyblockforlige/koolhere/tree/main/Handwriting_generator)
