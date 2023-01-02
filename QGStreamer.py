#!/usr/bin/env python
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication
from gi.repository import Gst, GObject, Gtk
from gi.repository import GdkX11, GstVideo
import numpy as np
import yaml
import time
import sys

import gi
gi.require_version('Gst', '1.0')


# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:


class GStreamerFeed:

    CONFIG_FILE = "config_gstream.yaml"

    def __init__(self):
        Gst.init(None)

        config = self.__load_config()

        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make(config["gstreamer_source"], "vsource")
        self.conv = Gst.ElementFactory.make("videoconvert", "colorspace")
        self.scaler = Gst.ElementFactory.make("videoscale", "fvidscale")
        self.crop = Gst.ElementFactory.make('videocrop', 'VideoCrop')
        self.appsink = Gst.ElementFactory.make("appsink", "video-output")
        self.source.set_property("device", config["input_device"])
        self.appsink.set_property("emit-signals", True)

        caps = Gst.caps_from_string(config["app_sink_caps"])
        self.appsink.set_property("caps", caps)
        self.appsink.connect("new-sample", self.__new_frame, self.appsink)

        self.__add_many(
            [self.source, self.conv, self.scaler, self.crop, self.appsink])
        self.__link_many(
            [self.source, self.conv, self.scaler, self.crop, self.appsink])

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)

        self.frame_buffor = None

    def __load_config(self):
        config_dict = dict()
        with open(self.CONFIG_FILE, "r") as config_file:
            try:
                config_dict = yaml.safe_load(config_file)
            except yaml.YAMLError as err:
                print(err)

        return config_dict

    def __gst_to_np(self, sample):
        '''
        Converts gst to numpy ndarray

        '''
        buf = sample.get_buffer()
        caps = sample.get_caps()
        arr = np.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             3),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8)
        return arr

    def __add_many(self, pipeline_list):
        '''
        Add list of Gst elements to pipeline

        '''

        for node in pipeline_list:
            self.player.add(node)

    def __link_many(self, pipeline_list):
        '''
        Links ordered (left to right) components in pipeline

        '''

        for n in range(len(pipeline_list) - 1):
            pipeline_list[n].link(pipeline_list[n + 1])

    def __new_frame(self, sink, data):
        '''
        Produces new frame for appsink and stores it in curr frame

        '''

        frame = sink.emit("pull-sample")

        arr = self.__gst_to_np(frame)
        self.frame_buffor = arr
        return Gst.FlowReturn.OK

    def __on_message(self, bus, message):
        '''

        '''

        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err} ", debug)
            self.player.set_state(Gst.State.NULL)

    def __on_sync_message(self, bus, message):
        '''


        '''

        if message.get_structure().get_name() == 'prepare-window-handle':
            win_id = self.windowId
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            # if not window id then create new window
            if win_id is None:
                win_id = self.movie_window.get_property('window').get_xid()
            imagesink.set_window_handle(win_id)

    def isFrameReady(self):
        '''
        Allows to check if new frame is ready to be obtained from stream.
        '''

        return not (self.frame_buffor is None)

    def getFrame(self):
        '''
        Returns latest frame from frame buffor
        Frame is stored as numpy array.

        Out:
        frame - numpy ndarray
        '''

        ret_frame = self.frame_buffor
        self.frame_buffor = None
        return ret_frame

    def startPrev(self):
        '''
        Starts the feed from gstream pipe.
        '''

        self.player.set_state(Gst.State.PLAYING)


