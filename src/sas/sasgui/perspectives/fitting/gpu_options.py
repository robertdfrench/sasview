'''
Module provides dialog for setting SAS_OPENCL variable, which defines
device choice for OpenCL calculation

Created on Nov 29, 2016

@author: wpotrzebowski
'''

import os
import warnings
import wx
import logging
from sas.sasgui.guiframe.documentation_window import DocumentationWindow
import imp


class CustomMessageBox(wx.Dialog):
    def __init__(self, parent, msg, title):

        wx.Dialog.__init__(self, parent, title=title)

        panel = wx.Panel(self, -1)
        static_box = wx.StaticBox(panel, -1, "OpenCL test completed!")
        boxsizer = wx.BoxSizer(orient=wx.VERTICAL)

        text = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE
                                       |wx.BORDER_NONE, size=(400,200))
        text.SetValue(msg)
        text.SetBackgroundColour(self.GetBackgroundColour())

        boxsizer.Add(text, 0)

        fit_hsizer = wx.StaticBoxSizer(static_box, orient=wx.VERTICAL)
        fit_hsizer.Add(boxsizer, 0, wx.ALL, 5)

        panel.SetSizer(fit_hsizer)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel, 0, wx.ALL, 10)

        ok_btn = wx.Button(self, wx.ID_OK)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add((10, 20), 1) # stretchable whitespace
        btn_sizer.Add(ok_btn, 0)

        vbox.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(vbox)
        vbox.Fit(self)

        self.Centre()
        self.ShowModal()
        self.Destroy()


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
        #Check if SAS_OPENCL is already set as enviromental variable
        self.sas_opencl = os.environ.get("SAS_OPENCL","")
        print("SAS_OPENCL: ",self.sas_opencl)

        for clopt in clinfo:
            button = wx.CheckBox(self.panel1, -1, label=clopt[1], name=clopt[1])

            if clopt != "No OpenCL":
                self.option_button[clopt[1]] = clopt[0]
                if self.sas_opencl == clopt[0]:
                    button.SetValue(1)
            else:
                self.option_button[clopt] = "None"
                if self.sas_opencl.lower() == "none":
                    button.SetValue(1)

            self.Bind(wx.EVT_CHECKBOX, self.on_check, id=button.GetId())
            self.buttons.append(button)
            boxsizer.Add(button, 0, 0)

        fit_hsizer = wx.StaticBoxSizer(static_box1, orient=wx.VERTICAL)
        fit_hsizer.Add(boxsizer, 0, wx.ALL, 5)

        self.panel1.SetSizer(fit_hsizer)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.panel1, 0, wx.ALL, 10)

        accept_btn = wx.Button(self, wx.ID_OK)
        accept_btn.SetToolTipString("Accept new OpenCL settings. This will"
                                    " overwrite SAS_OPENCL variable if set")

        help_id = wx.NewId()
        help_btn = wx.Button(self, help_id, 'Help')
        help_btn.SetToolTipString("Help on the GPU options")

        reset_id = wx.NewId()
        reset_btn = wx.Button(self, reset_id, 'Reset')
        reset_btn.SetToolTipString("Restore initial settings")

        test_id = wx.NewId()
        test_btn = wx.Button(self, test_id, 'Test')
        test_btn.SetToolTipString("Test if models compile on the given infrastructure")

        self.Bind(wx.EVT_BUTTON, self.on_OK, accept_btn)
        self.Bind(wx.EVT_BUTTON, self.on_test, test_btn)
        self.Bind(wx.EVT_BUTTON, self.on_reset, reset_btn)
        self.Bind(wx.EVT_BUTTON, self.on_help, help_btn)


        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add((10, 20), 1) # stretchable whitespace
        btn_sizer.Add(accept_btn, 0)
        btn_sizer.Add((10, 20), 0) # non-stretchable whitespace
        btn_sizer.Add(test_btn, 0)
        btn_sizer.Add((10, 20), 0) # non-stretchable whitespace
        btn_sizer.Add(reset_btn, 0)
        btn_sizer.Add((10, 20), 0) # non-stretchable whitespace
        btn_sizer.Add(help_btn, 0)

        # Add the button sizer to the main sizer.
        self.vbox.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.SetTitle("OpenCL options")
        self.Centre()

    def _get_clinfo(self):
        """
        Reading in information about available OpenCL infrastructure
        :return:
        """
        clinfo = []
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            p_index = 0
            for platform in platforms:
                d_index = 0
                devices = platform.get_devices()
                for device in devices:
                    if len(devices) > 1 and len(platforms) > 1:
                        combined_index = ":".join([str(p_index),str(d_index)])
                    elif len(platforms) > 1:
                        combined_index = str(p_index)
                    else:
                        combined_index = str(d_index)
                    #combined_index = ":".join([str(p_index),str(d_index)]) \
                    #    if len(platforms) > 1 else str(d_index)
                    clinfo.append((combined_index, ":".join([platform.name,device.name])))
                    d_index += 1
                p_index += 1
        except ImportError:
            warnings.warn("pyopencl import failed. Using only CPU computations")

        clinfo.append(("None","No OpenCL"))
        return clinfo

    #TODO: Dont want to mess with writting to configuration file before end of
    def _write_to_config_file(self):
        from sas.sasgui.guiframe.customdir import SetupCustom
        from sas.sasgui.guiframe.gui_manager import _find_local_config

        c_conf_dir = SetupCustom().find_dir()
        self.custom_config = _find_local_config('custom_config', c_conf_dir)
        if self.custom_config is None:
            self.custom_config = _find_local_config('custom_config', os.getcwd())

        #How to store it in file
        new_config_lines = []
        config_file = open(self.custom_config.__file__[:-1])
        if self.custom_config is not None:
            config_lines = config_file.readlines()
            for line in config_lines:
                if "SAS_OPENCL" in line:
                    if self.sas_opencl:
                        new_config_lines.append("SAS_OPENCL = \""+self.sas_opencl+"\"")
                    else:
                        new_config_lines.append("SAS_OPENCL = None")
                else:
                    new_config_lines.append(line)
        config_file.close()
        new_config_file = open(self.custom_config.__file__[:-1],"w")
        new_config_file.writelines(new_config_lines)
        new_config_file.close()

        #After file is touched module needs to be reloaded
        self.custom_config = _find_local_config('custom_config', c_conf_dir)
        if self.custom_config is None:
            self.custom_config = _find_local_config('custom_config', os.getcwd())

    def on_check(self, event):
        """
        Action triggered when box is selected
        :param event:
        :return:
        """
        selected_button = event.GetEventObject()
        for btn in self.buttons:
            if btn != selected_button:
                btn.SetValue(0)
        if selected_button.GetValue():
            self.sas_opencl = self.option_button[selected_button.Name]
        else:
            self.sas_opencl = None

    def on_OK(self, event):
        """
        Close window on accpetance
        """
        import sasmodels
        #If statement added to handle Reset
        if self.sas_opencl:
            os.environ["SAS_OPENCL"] = self.sas_opencl
        else:
            if "SAS_OPENCL" in os.environ:
                del(os.environ["SAS_OPENCL"])
        sasmodels.kernelcl.ENV = None
        #Need to reload sasmodels.core module to account SAS_OPENCL = "None"
        reload(sasmodels.core)
        event.Skip()

    def on_reset(self, event):
        """
        Close window on accpetance
        """
        for btn in self.buttons:
            btn.SetValue(0)

        self.sas_opencl=None

    def on_test(self, event):
        """
        Run sasmodels check from here and report results from
        """
        import json
        import platform
        import sasmodels
        from sasmodels.model_test import model_tests

        try:
            from sasmodels.kernelcl import environment
            env = environment()
            clinfo = [(ctx.devices[0].platform.vendor,
                      ctx.devices[0].platform.version,
                      ctx.devices[0].vendor,
                      ctx.devices[0].name,
                      ctx.devices[0].version)
                    for ctx in env.context]
        except ImportError:
            clinfo = None

        failures = []
        for test in model_tests():
            try:
                test()
            except Exception:
                failures.append(test.description)

        info = {
            'version':  sasmodels.__version__,
            'platform': platform.uname(),
            'opencl': clinfo,
            'failing tests': failures,
        }

        msg_info = "OpenCL tests"

        msg = "Results: "
        if len(failures) > 0:
            msg += 'Failing tests:\n'
            msg += json.dumps(info['failing tests'])
        else:
            msg+="All tests passed!\n"

        msg +="\nDetails:\n"
        msg += "Sasmodels version: "
        msg += info['version']+"\n"
        msg += "\nPlatform used: "
        msg += json.dumps(info['platform'])+"\n"
        msg += "\nOpenCL driver: "
        msg += json.dumps(info['opencl'])+"\n"

        CustomMessageBox(self.panel1, msg, msg_info)

    def on_help(self, event):
        """
        Provide help on opencl options.
        """
        TreeLocation = "user/gpu_computations.html"
        anchor = "#device-selection"
        DocumentationWindow(self, -1,
                            TreeLocation, anchor, "OpenCL Options Help")