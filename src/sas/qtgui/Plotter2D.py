import copy
import numpy
import pylab
import functools

from PyQt4 import QtGui
from PyQt4 import QtCore

DEFAULT_CMAP = pylab.cm.jet
from mpl_toolkits.mplot3d import Axes3D

import sas.qtgui.PlotUtilities as PlotUtilities
import sas.qtgui.GuiUtils as GuiUtils
from sas.qtgui.PlotterBase import PlotterBase
from sas.qtgui.ColorMap import ColorMap
from sas.sasgui.guiframe.dataFitting import Data1D
from sas.sasgui.guiframe.dataFitting import Data2D
from sas.sascalc.dataloader.manipulations import CircularAverage
from sas.sasgui.guiframe.local_perspectives.plotting.binder import BindArtist

# Minimum value of Z for which we will present data.
MIN_Z=-32

class Plotter2DWidget(PlotterBase):
    """
    2D Plot widget for use with a QDialog
    """
    def __init__(self, parent=None, manager=None, quickplot=False, dimension=2):
        self.dimension = dimension
        super(Plotter2DWidget, self).__init__(parent, manager=manager, quickplot=quickplot)

        self.cmap = DEFAULT_CMAP.name
        # Default scale
        self.scale = 'log_{10}'
        # to set the order of lines drawn first.
        self.slicer_z = 5
        # Reference to the current slicer
        self.slicer = None
        # Create Artist and bind it
        self.connect = BindArtist(self.figure)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data=None):
        """ data setter """
        self._data = data
        self.qx_data = data.qx_data
        self.qy_data = data.qy_data
        self.xmin = data.xmin
        self.xmax = data.xmax
        self.ymin = data.ymin
        self.ymax = data.ymax
        self.zmin = data.zmin
        self.zmax = data.zmax
        self.label = data.name
        self.xLabel = "%s(%s)"%(data._xaxis, data._xunit)
        self.yLabel = "%s(%s)"%(data._yaxis, data._yunit)
        self.title(title=data.title)

    @property
    def item(self):
        ''' getter for this plot's QStandardItem '''
        return self._item

    @item.setter
    def item(self, item=None):
        ''' setter for this plot's QStandardItem '''
        self._item = item

    def plot(self, data=None, marker=None, linestyle=None):
        """
        Plot 2D self._data
        """
        # Assing data
        if isinstance(data, Data2D):
            self.data = data

        assert(self._data)

        # Toggle the scale
        zmin_2D_temp, zmax_2D_temp = self.calculateDepth()

        # Prepare and show the plot
        self.showPlot(data=self.data.data,
                      qx_data=self.qx_data,
                      qy_data=self.qy_data,
                      xmin=self.xmin,
                      xmax=self.xmax,
                      ymin=self.ymin, ymax=self.ymax,
                      cmap=self.cmap, zmin=zmin_2D_temp,
                      zmax=zmax_2D_temp)

    def calculateDepth(self):
        """
        Re-calculate the plot depth parameters depending on the scale
        """
        # Toggle the scale
        zmin_temp = self.zmin
        zmax_temp = self.zmax
        # self.scale predefined in the baseclass
        if self.scale == 'log_{10}':
            if self.zmin is not None:
                zmin_temp = numpy.power(10, self.zmin)
            if self.zmax is not None:
                zmax_temp = numpy.power(10, self.zmax)
        else:
            if self.zmin is not None:
                # min log value: no log(negative)
                zmin_temp = MIN_Z if self.zmin <= 0 else numpy.log10(self.zmin)
            if self.zmax is not None:
                zmax_temp = numpy.log10(self.zmax)

        return (zmin_temp, zmax_temp)


    def createContextMenu(self):
        """
        Define common context menu and associated actions for the MPL widget
        """
        self.defaultContextMenu()

        self.contextMenu.addSeparator()
        self.actionDataInfo = self.contextMenu.addAction("&DataInfo")
        self.actionDataInfo.triggered.connect(
                              functools.partial(self.onDataInfo, self.data))

        self.actionSavePointsAsFile = self.contextMenu.addAction("&Save Points as a File")
        self.actionSavePointsAsFile.triggered.connect(
                                functools.partial(self.onSavePoints, self.data))
        self.contextMenu.addSeparator()

        self.actionCircularAverage = self.contextMenu.addAction("&Perform Circular Average")
        self.actionCircularAverage.triggered.connect(self.onCircularAverage)

        self.actionSectorView = self.contextMenu.addAction("&Sector [Q View]")
        self.actionSectorView.triggered.connect(self.onSectorView)
        self.actionAnnulusView = self.contextMenu.addAction("&Annulus [Phi View]")
        self.actionAnnulusView.triggered.connect(self.onAnnulusView)
        self.actionBoxSum = self.contextMenu.addAction("&Box Sum")
        self.actionBoxSum.triggered.connect(self.onBoxSum)
        self.actionBoxAveragingX = self.contextMenu.addAction("&Box Averaging in Qx")
        self.actionBoxAveragingX.triggered.connect(self.onBoxAveragingX)
        self.actionBoxAveragingY = self.contextMenu.addAction("&Box Averaging in Qy")
        self.actionBoxAveragingY.triggered.connect(self.onBoxAveragingY)
        # Additional items for slicer interaction
        if self.slicer:
            self.actionClearSlicer = self.contextMenu.addAction("&Clear Slicer")
            self.actionClearSlicer.triggered.connect(self.onClearSlicer)            
            self.actionEditSlicer = self.contextMenu.addAction("&Edit Slicer Parameters")
            self.actionEditSlicer.triggered.connect(self.onEditSlicer)            
        self.contextMenu.addSeparator()
        self.actionEditGraphLabel = self.contextMenu.addAction("&Edit Graph Label")
        self.actionEditGraphLabel.triggered.connect(self.onEditgraphLabel)
        self.contextMenu.addSeparator()
        self.actionColorMap = self.contextMenu.addAction("&2D Color Map")
        self.actionColorMap.triggered.connect(self.onColorMap)
        self.contextMenu.addSeparator()
        self.actionChangeScale = self.contextMenu.addAction("Toggle Linear/Log Scale")
        self.actionChangeScale.triggered.connect(self.onToggleScale)

    def createContextMenuQuick(self):
        """
        Define context menu and associated actions for the quickplot MPL widget
        """
        self.defaultContextMenu()

        if self.dimension == 2:
            self.actionToggleGrid = self.contextMenu.addAction("Toggle Grid On/Off")
            self.contextMenu.addSeparator()
        self.actionChangeScale = self.contextMenu.addAction("Toggle Linear/Log Scale")

        # Define the callbacks
        self.actionChangeScale.triggered.connect(self.onToggleScale)
        if self.dimension == 2:
            self.actionToggleGrid.triggered.connect(self.onGridToggle)

    def onToggleScale(self, event):
        """
        Toggle axis and replot image
        """
        # self.scale predefined in the baseclass
        if self.scale == 'log_{10}':
            self.scale = 'linear'
        else:
            self.scale = 'log_{10}'

        self.plot()

    def onClearSlicer(self):
        """
        Remove all sclicers from the chart
        """
        if self.slicer:
            self.slicer.clear()
            self.canvas.draw()
            self.slicer = None

    def onEditSlicer(self):
        """
        Present a small dialog for manipulating the current slicer
        """
        pass

    def onCircularAverage(self):
        """
        Perform circular averaging on Data2D
        """
        # Find the best number of bins
        npt = numpy.sqrt(len(self.data.data[numpy.isfinite(self.data.data)]))
        npt = numpy.floor(npt)
        # compute the maximum radius of data2D
        self.qmax = max(numpy.fabs(self.data.xmax),
                        numpy.fabs(self.data.xmin))
        self.ymax = max(numpy.fabs(self.data.ymax),
                        numpy.fabs(self.data.ymin))
        self.radius = numpy.sqrt(numpy.power(self.qmax, 2) + numpy.power(self.ymax, 2))
        #Compute beam width
        bin_width = (self.qmax + self.qmax) / npt
        # Create data1D circular average of data2D
        circle = CircularAverage(r_min=0, r_max=self.radius, bin_width=bin_width)
        circ = circle(self.data)
        dxl = circ.dxl if hasattr(circ, "dxl") else None
        dxw = circ.dxw if hasattr(circ, "dxw") else None

        new_plot = Data1D(x=circ.x, y=circ.y, dy=circ.dy, dx=circ.dx)
        new_plot.dxl = dxl
        new_plot.dxw = dxw
        new_plot.name = new_plot.title = "Circ avg " + self.data.name
        new_plot.source = self.data.source
        new_plot.interactive = True
        new_plot.detector = self.data.detector

        # Define axes if not done yet.
        new_plot.xaxis("\\rm{Q}", "A^{-1}")
        if hasattr(self.data, "scale") and \
                    self.data.scale == 'linear':
            new_plot.ytransform = 'y'
            new_plot.yaxis("\\rm{Residuals} ", "normalized")
        else:
            new_plot.yaxis("\\rm{Intensity} ", "cm^{-1}")

        new_plot.group_id = "2daverage" + self.data.name
        new_plot.id = "Circ avg " + self.data.name
        new_plot.is_data = True
        variant_plot = QtCore.QVariant(new_plot)
        GuiUtils.updateModelItemWithPlot(self._item, variant_plot, new_plot.id)
        # TODO: force immediate display (?)

    def setSlicer(self, slicer):
        """
        Clear the previous slicer and create a new one.
        slicer: slicer class to create
        """
        # Clear current slicer
        if not self.slicer == None:
            self.slicer.clear()
        # Create a new slicer
        self.slicer_z += 1
        self.slicer = slicer(self, self.ax, item=self._item, zorder=self.slicer_z)
        self.ax.set_ylim(self.data.ymin, self.data.ymax)
        self.ax.set_xlim(self.data.xmin, self.data.xmax)
        # Draw slicer
        self.figure.canvas.draw()
        self.slicer.update()

    def onSectorView(self):
        """
        Perform sector averaging on Q and draw sector slicer
        """
        from sas.sasgui.guiframe.local_perspectives.plotting.SectorSlicer import SectorInteractor
        self.setSlicer(slicer=SectorInteractor)

    def onAnnulusView(self):
        """
        Perform sector averaging on Phi and draw annulus slicer
        """
        from sas.sasgui.guiframe.local_perspectives.plotting.AnnulusSlicer import AnnulusInteractor
        self.setSlicer(slicer=AnnulusInteractor)

    def onBoxSum(self):
        """
        """
        pass

    def onBoxAveragingX(self):
        """
        Perform 2D data averaging on Qx
        Create a new slicer.
        """
        from sas.sasgui.guiframe.local_perspectives.plotting.boxSlicer import BoxInteractorX
        self.setSlicer(slicer=BoxInteractorX)

    def onBoxAveragingY(self):
        """
        Perform 2D data averaging on Qy
        Create a new slicer .
        """
        from sas.sasgui.guiframe.local_perspectives.plotting.boxSlicer import BoxInteractorY
        self.setSlicer(slicer=BoxInteractorY)

    def onEditgraphLabel(self):
        """
        """
        pass

    def onColorMap(self):
        """
        Display the color map dialog and modify the plot's map accordingly
        """
        color_map_dialog = ColorMap(self, cmap=self.cmap,
                                    vmin=self.vmin,
                                    vmax=self.vmax,
                                    data=self.data)

        if color_map_dialog.exec_() == QtGui.QDialog.Accepted:
            self.cmap = color_map_dialog.cmap()
            self.vmin, self.vmax = color_map_dialog.norm()
            # Redraw the chart with new cmap
            self.plot()
        pass

    def showPlot(self, data, qx_data, qy_data, xmin, xmax, ymin, ymax,
                 zmin, zmax, color=0, symbol=0, markersize=0,
                 label='data2D', cmap=DEFAULT_CMAP):
        """
        Render and show the current data
        """
        self.qx_data = qx_data
        self.qy_data = qy_data
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        # If we don't have any data, skip.
        if data is None:
            return
        if data.ndim == 1:
            output = PlotUtilities.build_matrix(data, self.qx_data, self.qy_data)
        else:
            output = copy.deepcopy(data)

        zmin_temp = self.zmin
        # check scale
        if self.scale == 'log_{10}':
            try:
                if  self.zmin <= 0  and len(output[output > 0]) > 0:
                    zmin_temp = self.zmin
                    output[output > 0] = numpy.log10(output[output > 0])
                elif self.zmin <= 0:
                    zmin_temp = self.zmin
                    output[output > 0] = numpy.zeros(len(output))
                    output[output <= 0] = MIN_Z
                else:
                    zmin_temp = self.zmin
                    output[output > 0] = numpy.log10(output[output > 0])
            except:
                #Too many problems in 2D plot with scale
                output[output > 0] = numpy.log10(output[output > 0])
                pass

        self.cmap = cmap
        if self.dimension != 3:
            #Re-adjust colorbar
            self.figure.subplots_adjust(left=0.2, right=.8, bottom=.2)

            im = self.ax.imshow(output, interpolation='nearest',
                                origin='lower',
                                vmin=zmin_temp, vmax=self.zmax,
                                cmap=self.cmap,
                                extent=(self.xmin, self.xmax,
                                        self.ymin, self.ymax))

            cbax = self.figure.add_axes([0.84, 0.2, 0.02, 0.7])

            # Current labels for axes
            self.ax.set_ylabel(self.y_label)
            self.ax.set_xlabel(self.x_label)

            # Title only for regular charts
            if not self.quickplot:
                self.ax.set_title(label=self._title)

            if cbax is None:
                ax.set_frame_on(False)
                cb = self.figure.colorbar(im, shrink=0.8, aspect=20)
            else:
                cb = self.figure.colorbar(im, cax=cbax)

            cb.update_bruteforce(im)
            cb.set_label('$' + self.scale + '$')

            self.vmin = cb.vmin
            self.vmax = cb.vmax

        else:
            # clear the previous 2D from memory
            self.figure.clear()

            self.figure.subplots_adjust(left=0.1, right=.8, bottom=.1)

            X = self._data.x_bins[0:-1]
            Y = self._data.y_bins[0:-1]
            X, Y = numpy.meshgrid(X, Y)

            ax = Axes3D(self.figure)
            #cbax = self.figure.add_axes([0.84, 0.1, 0.02, 0.8])

            # Disable rotation for large sets.
            # TODO: Define "large" for a dataset
            SET_TOO_LARGE = 500
            if len(X) > SET_TOO_LARGE:
                ax.disable_mouse_rotation()

            self.figure.canvas.resizing = False
            im = ax.plot_surface(X, Y, output, rstride=1, cstride=1, cmap=cmap,
                                 linewidth=0, antialiased=False)
            self.ax.set_axis_off()

        if self.dimension != 3:
            self.figure.canvas.draw_idle()
        else:
            self.figure.canvas.draw()

    def update(self):
        self.figure.canvas.draw()

    def draw(self):
        self.figure.canvas.draw()


class Plotter2D(QtGui.QDialog, Plotter2DWidget):
    def __init__(self, parent=None, quickplot=False, dimension=2):

        QtGui.QDialog.__init__(self)
        Plotter2DWidget.__init__(self, manager=parent, quickplot=quickplot, dimension=dimension)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/res/ball.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
