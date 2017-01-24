# TODO: the line slicer should listen to all 2DREFRESH events, get the data and slice it
#      before pushing a new 1D data update.

#
# TODO: NEED MAJOR REFACTOR
#

import math
from PyQt4 import QtGui
from PyQt4 import QtCore

# from copy import deepcopy
# Debug printout
from BaseInteractor import _BaseInteractor
from sas.sasgui.guiframe.dataFitting import Data1D
import sas.qtgui.GuiUtils as GuiUtils

class AnnulusInteractor(_BaseInteractor):
    """
    Select an annulus through a 2D plot.
    This interactor is used to average 2D data  with the region
    defined by 2 radius.
    this class is defined by 2 Ringinterators.
    """
    def __init__(self, base, axes, item=None, color='black', zorder=3):

        _BaseInteractor.__init__(self, base, axes, color=color)
        self.markers = []
        self.axes = axes
        self.base = base
        self._item = item
        self.qmax = min(math.fabs(self.base.data.xmax),
                        math.fabs(self.base.data.xmin))  # must be positive
        self.connect = self.base.connect

        # Number of points on the plot
        self.nbins = 36
        # Cursor position of Rings (Left(-1) or Right(1))
        self.xmaxd = self.base.data.xmax
        self.xmind = self.base.data.xmin

        if (self.xmaxd + self.xmind) > 0:
            self.sign = 1
        else:
            self.sign = -1
        # Inner circle
        self.inner_circle = RingInteractor(self, self.axes,
                                           zorder=zorder,
                                           r=self.qmax / 2.0, sign=self.sign)
        self.inner_circle.qmax = self.qmax
        self.outer_circle = RingInteractor(self, self.axes,
                                           zorder=zorder + 1, r=self.qmax / 1.8,
                                           sign=self.sign)
        self.outer_circle.qmax = self.qmax * 1.2
        self.update()
        self._post_data()

    def set_layer(self, n):
        """
        Allow adding plot to the same panel

        :param n: the number of layer

        """
        self.layernum = n
        self.update()

    def clear(self):
        """
        Clear the slicer and all connected events related to this slicer
        """
        self.clear_markers()
        self.outer_circle.clear()
        self.inner_circle.clear()
        self.base.connect.clearall()

    def update(self):
        """
        Respond to changes in the model by recalculating the profiles and
        resetting the widgets.
        """
        # Update locations
        self.inner_circle.update()
        self.outer_circle.update()

    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self.inner_circle.save(ev)
        self.outer_circle.save(ev)

    def _post_data(self, nbins=None):
        """
        Uses annulus parameters to plot averaged data into 1D data.

        :param nbins: the number of points to plot

        """
        # Data to average
        data = self.base.data
        if data == None:
            return

        from sas.sascalc.dataloader.manipulations import Ring
        rmin = min(math.fabs(self.inner_circle.get_radius()),
                   math.fabs(self.outer_circle.get_radius()))
        rmax = max(math.fabs(self.inner_circle.get_radius()),
                   math.fabs(self.outer_circle.get_radius()))
        # If the user does not specify the numbers of points to plot
        # the default number will be nbins= 36
        if nbins == None:
            self.nbins = 36
        else:
            self.nbins = nbins
        # Create the data1D Q average of data2D
        sect = Ring(r_min=rmin, r_max=rmax, nbins=self.nbins)
        sector = sect(self.base.data)

        if hasattr(sector, "dxl"):
            dxl = sector.dxl
        else:
            dxl = None
        if hasattr(sector, "dxw"):
            dxw = sector.dxw
        else:
            dxw = None
        new_plot = Data1D(x=(sector.x - math.pi) * 180 / math.pi,
                          y=sector.y, dy=sector.dy)
        new_plot.dxl = dxl
        new_plot.dxw = dxw
        new_plot.name = "AnnulusPhi" + "(" + self.base.data.name + ")"
        new_plot.title = "AnnulusPhi" + "(" + self.base.data.name + ")"

        new_plot.source = self.base.data.source
        new_plot.interactive = True
        new_plot.detector = self.base.data.detector
        # If the data file does not tell us what the axes are, just assume...
        new_plot.xaxis("\\rm{\phi}", 'degrees')
        new_plot.yaxis("\\rm{Intensity} ", "cm^{-1}")
        if hasattr(data, "scale") and data.scale == 'linear' and \
                self.base.data.name.count("Residuals") > 0:
            new_plot.ytransform = 'y'
            new_plot.yaxis("\\rm{Residuals} ", "/")

        new_plot.group_id = "AnnulusPhi" + self.base.data.name
        new_plot.id = "AnnulusPhi" + self.base.data.name
        new_plot.is_data = True
        new_plot.xtransform = "x"
        new_plot.ytransform = "y"
        variant_plot = QtCore.QVariant(new_plot)
        GuiUtils.updateModelItemWithPlot(self._item, variant_plot, new_plot.id)

    def moveend(self, ev):
        """
        Called when any dragging motion ends.
        Redraw the plot with new parameters.
        """
        self._post_data(self.nbins)

    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self.inner_circle.restore()
        self.outer_circle.restore()

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        pass

    def set_cursor(self, x, y):
        pass

    def get_params(self):
        """
        Store a copy of values of parameters of the slicer into a dictionary.
        :return params: the dictionary created
        """
        params = {}
        params["inner_radius"] = math.fabs(self.inner_circle._inner_mouse_x)
        params["outer_radius"] = math.fabs(self.outer_circle._inner_mouse_x)
        params["nbins"] = self.nbins
        return params

    def set_params(self, params):
        """
        Receive a dictionary and reset the slicer with values contained
        in the values of the dictionary.

        :param params: a dictionary containing name of slicer parameters and
            values the user assigned to the slicer.
        """
        inner = math.fabs(params["inner_radius"])
        outer = math.fabs(params["outer_radius"])
        self.nbins = int(params["nbins"])
        # Update the picture
        self.inner_circle.set_cursor(inner, self.inner_circle._inner_mouse_y)
        self.outer_circle.set_cursor(outer, self.outer_circle._inner_mouse_y)
        # Post the data given the nbins entered by the user
        self._post_data(self.nbins)

    def draw(self):
        """
        """
        self.base.draw()


class RingInteractor(_BaseInteractor):
    """
     Draw a ring Given a radius
    """
    def __init__(self, base, axes, color='black', zorder=5, r=1.0, sign=1):
        """
        :param: the color of the line that defined the ring
        :param r: the radius of the ring
        :param sign: the direction of motion the the marker

        """
        _BaseInteractor.__init__(self, base, axes, color=color)
        self.markers = []
        self.axes = axes
        # Current radius of the ring
        self._inner_mouse_x = r
        # Value of the center of the ring
        self._inner_mouse_y = 0
        # previous value of that radius
        self._inner_save_x = r
        # Save value of the center of the ring
        self._inner_save_y = 0
        # Class instantiating RingIterator class
        self.base = base
        # the direction of the motion of the marker
        self.sign = sign
        # # Create a marker
        # Inner circle marker
        x_value = [self.sign * math.fabs(self._inner_mouse_x)]
        self.inner_marker = self.axes.plot(x_value, [0], linestyle='',
                                           marker='s', markersize=10,
                                           color=self.color, alpha=0.6,
                                           pickradius=5, label="pick",
                                           zorder=zorder,
                                           visible=True)[0]
        # Draw a circle
        [self.inner_circle] = self.axes.plot([], [], linestyle='-', marker='', color=self.color)
        # The number of points that make the ring line
        self.npts = 40

        self.connect_markers([self.inner_marker])
        self.update()

    def set_layer(self, n):
        """
        Allow adding plot to the same panel

        :param n: the number of layer

        """
        self.layernum = n
        self.update()

    def clear(self):
        """
        Clear the slicer and all connected events related to this slicer
        """
        self.clear_markers()
        try:
            self.inner_marker.remove()
            self.inner_circle.remove()
        except:
            # Old version of matplotlib
            for item in range(len(self.axes.lines)):
                del self.axes.lines[0]

    def get_radius(self):
        """
        :return self._inner_mouse_x: the current radius of the ring
        """
        return self._inner_mouse_x

    def update(self):
        """
        Draw the new roughness on the graph.
        """
        # Plot inner circle
        x = []
        y = []
        for i in range(self.npts):
            phi = 2.0 * math.pi / (self.npts - 1) * i

            xval = 1.0 * self._inner_mouse_x * math.cos(phi)
            yval = 1.0 * self._inner_mouse_x * math.sin(phi)

            x.append(xval)
            y.append(yval)

        self.inner_marker.set(xdata=[self.sign * math.fabs(self._inner_mouse_x)],
                              ydata=[0])
        self.inner_circle.set_data(x, y)

    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self._inner_save_x = self._inner_mouse_x
        self._inner_save_y = self._inner_mouse_y

    def moveend(self, ev):
        """
        Called after a dragging motion
        """
        self.base.moveend(ev)

    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self._inner_mouse_x = self._inner_save_x
        self._inner_mouse_y = self._inner_save_y

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        self._inner_mouse_x = x
        self._inner_mouse_y = y
        self.base.base.update()

    def set_cursor(self, x, y):
        """
        draw the ring given x, y value
        """
        self.move(x, y, None)
        self.update()

    def get_params(self):
        """
        Store a copy of values of parameters of the slicer into a dictionary.
        :return params: the dictionary created
        """
        params = {}
        params["radius"] = math.fabs(self._inner_mouse_x)
        return params

    def set_params(self, params):
        """
        Receive a dictionary and reset the slicer with values contained
        in the values of the dictionary.

        :param params: a dictionary containing name of slicer parameters and
            values the user assigned to the slicer.

        """
        x = params["radius"]
        self.set_cursor(x, self._inner_mouse_y)

class CircularMask(_BaseInteractor):
    """
     Draw a ring Given a radius
    """
    def __init__(self, base, axes, color='grey', zorder=3, side=None):
        """
        :param: the color of the line that defined the ring
        :param r: the radius of the ring
        :param sign: the direction of motion the the marker
        """
        _BaseInteractor.__init__(self, base, axes, color=color)
        self.markers = []
        self.axes = axes
        self.base = base
        self.is_inside = side
        self.qmax = min(math.fabs(self.base.data.xmax),
                        math.fabs(self.base.data.xmin))  # must be positive
        self.connect = self.base.connect

        # Cursor position of Rings (Left(-1) or Right(1))
        self.xmaxd = self.base.data.xmax
        self.xmind = self.base.data.xmin

        if (self.xmaxd + self.xmind) > 0:
            self.sign = 1
        else:
            self.sign = -1
        # Inner circle
        self.outer_circle = RingInteractor(self, self.axes, 'blue',
                                           zorder=zorder + 1, r=self.qmax / 1.8,
                                           sign=self.sign)
        self.outer_circle.qmax = self.qmax * 1.2
        self.update()
        self._post_data()

    def set_layer(self, n):
        """
        Allow adding plot to the same panel
        :param n: the number of layer
        """
        self.layernum = n
        self.update()

    def clear(self):
        """
        Clear the slicer and all connected events related to this slicer
        """
        self.clear_markers()
        self.outer_circle.clear()
        self.base.connect.clearall()

    def update(self):
        """
        Respond to changes in the model by recalculating the profiles and
        resetting the widgets.
        """
        # Update locations
        self.outer_circle.update()
        out = self._post_data()
        return out

    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self.outer_circle.save(ev)

    def _post_data(self):
        """
        Uses annulus parameters to plot averaged data into 1D data.

        :param nbins: the number of points to plot

        """
        # Data to average
        data = self.base.data

        # If we have no data, just return
        if data == None:
            return
        mask = data.mask
        from sas.sascalc.dataloader.manipulations import Ringcut

        rmin = 0
        rmax = math.fabs(self.outer_circle.get_radius())

        # Create the data1D Q average of data2D
        mask = Ringcut(r_min=rmin, r_max=rmax)

        if self.is_inside:
            out = (mask(data) == False)
        else:
            out = (mask(data))
        return out


    def moveend(self, ev):
        """
        Called when any dragging motion ends.
        Post an event (type =SlicerParameterEvent)
        to plotter 2D with a copy  slicer parameters
        Call  _post_data method
        """
        self.base.thaw_axes()
        # create a 1D data plot
        self._post_data()

    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self.outer_circle.restore()

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        pass

    def set_cursor(self, x, y):
        pass

    def get_params(self):
        """
        Store a copy of values of parameters of the slicer into a dictionary.

        :return params: the dictionary created

        """
        params = {}
        params["outer_radius"] = math.fabs(self.outer_circle._inner_mouse_x)
        return params

    def set_params(self, params):
        """
        Receive a dictionary and reset the slicer with values contained
        in the values of the dictionary.

        :param params: a dictionary containing name of slicer parameters and
            values the user assigned to the slicer.
        """
        outer = math.fabs(params["outer_radius"])
        # Update the picture
        self.outer_circle.set_cursor(outer, self.outer_circle._inner_mouse_y)
        # Post the data given the nbins entered by the user
        self._post_data()

    def draw(self):
        self.base.update()

