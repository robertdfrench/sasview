import wx.lib.newevent
#send  data to data manager
(NewStoreDataEvent, EVT_NEW_STORE_DATA) = wx.lib.newevent.NewEvent()
# send data to other perspectives
(NewLoadedDataEvent, EVT_NEW_LOADED_DATA) = wx.lib.newevent.NewEvent()
# plot data
(NewPlotEvent, EVT_NEW_PLOT) = wx.lib.newevent.NewEvent()
# print the messages on statusbar
(StatusEvent,  EVT_STATUS)   = wx.lib.newevent.NewEvent()
#create a panel slicer 
(SlicerPanelEvent, EVT_SLICER_PANEL)   = wx.lib.newevent.NewEvent()
#print update paramaters for panel slicer 
(SlicerParamUpdateEvent, EVT_SLICER_PARS_UPDATE)   = wx.lib.newevent.NewEvent()
#update the slicer from the panel 
(SlicerParameterEvent, EVT_SLICER_PARS)   = wx.lib.newevent.NewEvent()
#slicer event
(SlicerEvent, EVT_SLICER)   = wx.lib.newevent.NewEvent()
# event containinG A DICTIONARY OF NAME and errors of selected data
(ErrorDataEvent, ERR_DATA) = wx.lib.newevent.NewEvent()
## event that that destroy a page associate with Data1D removed from the graph
(RemoveDataEvent, EVT_REMOVE_DATA)   = wx.lib.newevent.NewEvent()
##event that allow to add more that to the same plot
(AddManyDataEvent, EVT_ADD_MANY_DATA)   = wx.lib.newevent.NewEvent()
##event for the panel on focus
(PanelOnFocusEvent, EVT_PANEL_ON_FOCUS)   = wx.lib.newevent.NewEvent()

