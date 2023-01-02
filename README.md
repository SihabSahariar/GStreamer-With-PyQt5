# GStreamer-With-PyQt5
Implementation of Gstreamer with Python in PyQt5 GUI

# What is Gstreamer
GStreamer is an open-source framework for multimedia processing that allows developers to create pipeline-based workflows for manipulating and processing media. It is designed to be modular, with each component in the pipeline functioning as a plug-and-play element that can be easily added, removed, or modified. This makes it ideal for a variety of applications, including media players, video and audio editors, web browsers, and streaming servers. GStreamer provides an API for writing applications using its plugins and handles data flow management and media type handling/negotiation. It is particularly useful in computer vision applications, as it enables the conversion, resizing, and scaling of input and output streams before they are passed to or received from a model.

# Installation
```
sudo apt-get install gstreamer1.0-*
pip install pygobject gst-python
```
Once the installation is complete, you should be able to import GStreamer and its components in your Python scripts using the following import statement:
```
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
```
