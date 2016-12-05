'''
Module provides dialog for setting SAS_OPENCL variable, which defines
device choice for OpenCL calculation

Created on Nov 29, 2016

@author: wpotrzebowski
'''

import os
import warnings
import wx

from sas.sasgui.guiframe.documentation_window import DocumentationWindow

class GpuOptions(wx.Dialog):
    """
    "OpenCL options" Dialog Box

    Provides dialog for setting SAS_OPENCL variable, which defines
    device choice for OpenCL calculation

    """

    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        clinfo = self._get_clinfo()

        self.panel1 = wx.Panel(self, -1)
        static_box1 = wx.StaticBox(self.panel1, -1, "Available OpenCL Options:")

        boxsizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.option_button = {}
        self.buttons = []
        for index, clopt in enumerate(clinfo):
            button = wx.CheckBox(self.panel1, -1, label=clopt, name=clopt)
            if clopt != "No OpenCL":
                self.option_button[clopt] = str(index)
            else:
                self.option_button[clopt] = "None"
            self.Bind(wx.EVT_CHECKBOX, self.on_check, id=button.GetId())
            self.buttons.append(button)
            boxsizer.Add(button, 0, 0)

        fit_hsizer = wx.StaticBoxSizer(static_box1, orient=wx.VERTICAL)
        fit_hsizer.Add(boxsizer, 0, wx.ALL, 5)

        self.panel1.SetSizer(fit_hsizer)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.panel1, 0, wx.ALL, 10)

        accept_btn = wx.Button(self, wx.ID_OK)
        accept_btn.SetToolTipString("Accept OpenCL settings")

        help_id = wx.NewId()
        help_btn = wx.Button(self, help_id, 'Help')
        help_btn.SetToolTipString("Help on the GPU options")

        self.Bind(wx.EVT_BUTTON, self.on_OK, accept_btn)
        self.Bind(wx.EVT_BUTTON, self.on_help, help_btn)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add((10, 20), 1) # stretchable whitespace
        btn_sizer.Add(accept_btn, 0)
        btn_sizer.Add((10, 20), 0) # non-stretchable whitespace
        btn_sizer.Add(help_btn, 0)

        # Add the button sizer to the main sizer.
        self.vbox.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.Centre()

    def _get_clinfo(self):
        clinfo = []

        try:
            import pyopencl as cl
            for platform in cl.get_platforms():
                for device in platform.get_devices():
                    clinfo.append(device.name)
        except ImportError:
            warnings.warn("pyopencl import failed. Please check installation")

        clinfo.append("No OpenCL")
        return clinfo

    def on_check(self, event):
        """
        Action triggered when button is selected
        :param event:
        :return:
        """
        selected_button = event.GetEventObject()
        for btn in self.buttons:
            if btn != selected_button:
                btn.SetValue(0)
        os.environ["SAS_OPENCL"] = self.option_button[selected_button.Name]

    def on_OK(self, event):
        """
        Close window on accpetance
        """
        import sasmodels
        sasmodels.kernelcl.ENV = None
        #Need to reload sasmodels.core module to account SAS_OPENCL = "None"
        reload(sasmodels.core)
        event.Skip()

    def on_help(self, event):
        """
        Provide help on opencl options.
        """
        TreeLocation = "user/gpu_computations.html"
        anchor = "#device-selection"
        DocumentationWindow(self, -1,
                            TreeLocation, anchor, "OpenCL Options Help")
