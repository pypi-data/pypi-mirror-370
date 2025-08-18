from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Cfullable
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.widgets.view_box import ViewBox, AxisNormaliser

from PySide6 import QtWidgets, QtCore
import sys
from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget
from pyqtgraph import opengl
import numpy as np
import uuid 
from dataclasses import dataclass, field


@dataclass(slots=True)
class PlotDataset:
    full: Dict[int, np.ndarray]
    _subset: Dict[int, np.ndarray] = field(init=False, default=None)
    limits_full: Dict[int, Tuple[float, float]] = field(init=False, default_factory=lambda: {ax : (None, None) for ax in range(3)})
    limits_subset: Dict[int, Tuple[float, float]] = field(init=False, default=None)
    _subset_mask: Dict[int, np.ndarray] = field(init=False, default=None)
    _limits_used_for_subset: Dict[int, List[float, float]] = field(init=False, default=None)
    _subset_on: bool = False
    

    def __post_init__(self):
        self.resetSubset()
        
    def setFull(self, full):
        self.full=full
        self._computerLimitsFull()

    def setSubset(self, subset):
        self._subset=subset
        self._computerLimitsSubset()

    def setFullForAxis(self, ax, arr):
        self.full[ax]=arr
        self._computerLimitsFullForAxis(ax)
        
    def updateDatasetAxis(self, ax, arr):
        self.setFullForAxis(ax, arr)
        if self._subset_on:
            self.computeSubsetFromLimits(ax, self._subset_mask[ax])
        self.setSubsetForAxis(ax, arr)        
        
    def setSubsetForAxis(self, ax, arr):
        self.full[ax]=arr
        
    def _axisSubsetCleaup(self, ax):
        self._computerLimitsSubsetForAxis(ax)
        subset_dims_equal_full = [self._subset_mask[ax].sum() == self.full[ax].size for ax in range(3)]
        if all((any(subset_dims_equal_full),
                any([not a is None for a in self._limits_used_for_subset[2]]),
                any((self.limits_full[2][0] != self.limits_subset[2][0],
                     self.limits_full[2][1] != self.limits_subset[2][1]))
                )):
            self._subset_on=True
        else:
            self._subset_on=False            
        
    def subset(self, ax=None):
        if ax is None:
            return self._subset[0], self._subset[1], self._subset[2]
        else:
            return self._subset[ax]
        
    def computeSubsetFromLimits(self, ax, limits):
        self._limits_used_for_subset[ax]=limits
        z_prev_lims = self._limits_used_for_subset[2]
        if ax < 2:
            mask_ax = (self.full[ax] >= limits[0]) & (self.full[ax] <= limits[1])
            new_subset = self.full[ax][mask_ax]
            self._subset_mask[ax]=mask_ax
            mask_other = self._subset_mask[1-ax]
            if ax == 0:
                new_subset_z = self.full[2][mask_ax,:][:,mask_other]
            elif ax == 1:
                new_subset_z = self.full[2][mask_other,:][:,mask_ax]
            
            z_clipped = np.clip(new_subset_z, z_prev_lims[0], z_prev_lims[1])
            self._subset[2] = z_clipped
            self._axisSubsetCleaup(2)
        else:
            new_subset_z = self.full[2][self._subset_mask[0],:][:,self._subset_mask[1]]
            new_subset = np.clip(new_subset_z, z_prev_lims[0], z_prev_lims[1])
        self._subset[ax]=new_subset
        self._axisSubsetCleaup(ax)

    def fullRange():
        return self._ran
        
    def resetSubset(self):
        self._computerLimitsFull()
        self._subset = {ax : arr.copy() for ax, arr in self.full.items()}
        self.limits_subset = {ax : (limit[0], limit[1]) for ax, limit in self.limits_full.items()}
        self._subset_mask = {ax : np.ones(arr.shape, dtype=bool) for ax, arr in self.full.items()}
        self._subset_on=False
        self._limits_used_for_subset = {ax : (None, None) for ax in range(3)}
    
    def _computerLimitsFull(self):
        for ax in self.full:
            self._computerLimitsFullForAxis(ax)

    def _computerLimitsSubset(self):
        for ax, arr in self._subset.items():
            self.limits_subset[ax] = np.nanmin(arr), np.nanmax(arr)
            
    def _computerLimitsFullForAxis(self, axis):
        self.limits_full[axis] = np.nanmin(self.full[axis]), np.nanmax(self.full[axis])

    def _computerLimitsSubsetForAxis(self, axis):
        self.limits_subset[axis] = np.nanmin(self._subset[axis]), np.nanmax(self._subset[axis])
        



class CustomSurface(opengl.GLSurfacePlotItem):
    def __init__(self, *args, **kwargs):
        self._view_box: ViewBox=None
        self.__parent = None
        self.__view=None
        self._id = uuid.uuid4()
        
        full = {idx : arr for idx, arr in enumerate(args[:3])}
        
        self.dataset = PlotDataset(full)
        
        super().__init__(*args, **kwargs)
        
        self._ax_idx_str_map = {i : s for i, s in enumerate("xyz")}
        
            
    def dataInView(self,
                   view_box: ViewBox
                   ):
        setdataKwargs = {}
        zvalues_in_view=None
        for ax in range(3):
            viewRange = view_box._viewRange[ax]
            if ax != 2:
                values = self.dataset.full[ax]
                mask = (values >= viewRange[0]) & (values <= viewRange[1])
                values_in_view = values[mask]
                setdataKwargs[self._ax_idx_str_map[ax]] = values_in_view
                self.dataset.setSubsetForAxis(ax, values_in_view)
                
                if ax==0:
                    values_z = self.dataset.full[2].copy()
                    zvalues_in_view = values_z[mask, :]
                else:
                    zvalues_in_view = zvalues_in_view[:, mask]
                setdataKwargs["z"] = zvalues_in_view
                
            else:
                zvalues_in_view = np.clip(zvalues_in_view, viewRange[0], viewRange[1])
                setdataKwargs["z"] = zvalues_in_view
                self.dataset.setSubsetForAxis(2, zvalues_in_view)
        return setdataKwargs
    
    def updateXView(self, view_box: ViewBox):
        xRange = view_box._viewRange[0]
        self.dataset.computeSubsetFromLimits(0, xRange)
        x_norm, y_norm, z_norm = view_box.normaliseToView(*self.dataset.subset())
        super().setData(x=x_norm, y=y_norm, z=z_norm)        
        
    def updateYView(self, view_box: ViewBox):
        yRange = view_box._viewRange[1]
        self.dataset.computeSubsetFromLimits(1, yRange)
        x_norm, y_norm, z_norm = view_box.normaliseToView(*self.dataset.subset())
        super().setData(x=x_norm, y=y_norm, z=z_norm)
    
    def updateZView(self, view_box: ViewBox):
        zRange = view_box._viewRange[2]
        self.dataset.computeSubsetFromLimits(2, zRange)
        x_norm, y_norm, z_norm = view_box.normaliseToView(*self.dataset.subset())
        super().setData(x=x_norm, y=y_norm, z=z_norm)

    def updateInView(self,
                     ax: int,
                     view_box: ViewBox
                     ):
        setdataKwargs = self.dataInView(view_box)
        super().setData(**setdataKwargs)


    def linktoView(self,
                   view_box: ViewBox):
        self._view_box=view_box
    
    def filterinView(self, x=None, y=None, z=None):
        if self._view_box is None:
            return {"x" : x, "y" : y, "z" : z}
        setDataKwargs = self.dataInView(self._view_box)
        return setDataKwargs
    
    def _update_dataset(self, x=None, y=None, z=None):
        if not x is None:
            self.dataset.updateDatasetAxis(0, x)
        if not y is None:
            self.dataset.updateDatasetAxis(1, y)
        if not z is None:
            self.dataset.updateDatasetAxis(2, z)

    def setData(self, x=None, y=None, z=None, colors=None):
        self._update_dataset(x, y, z)
        if not self._view_box is None:
            x_norm, y_norm, z_norm = self._view_box.normaliseToView(*self.dataset.subset())
        else:
            x_norm, y_norm, z_norm = self.dataset.subset()
        super().setData(x=x_norm, y=y_norm, z=z_norm)
        
    def setDataFromView(self, view_box: ViewBox):
        for i, viewRange in enumerate(view_box.viewRange()):
            self.dataset.computeSubsetFromLimits(i, viewRange)
        x_norm, y_norm, z_norm = view_box.normaliseToView(*self.dataset.subset())
        super().setData(x=x_norm, y=y_norm, z=z_norm)
        
    def id(self):
        return self._id


class CustomScatter(opengl.GLScatterPlotItem):
    def __init__(self, *args, **kwargs):
        self._view_box: ViewBox=None
        self.__parent = None
        self.__view=None
        self._id = uuid.uuid4()

        super().__init__(*args, **kwargs)

    def setData(self, **kwds):
        super().setData(**kwds)
        if not self._view_box is None:
             self.setTransform(self._view_box.transform_matrix)

    def id(self):
        return self._id


class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self.central_layout = QtWidgets.QVBoxLayout()
        central.setLayout(self.central_layout)
        self.gl_view = GL3DViewWidget.GL3DViewWidget(padding=[0.]*3)
        X = np.arange(-5, 5, 0.5)
        Y = np.arange(-5, 5, 0.5)
        X_mat, Y_mat = np.meshgrid(X, Y)

        Z_mat = 3 * np.sin(X_mat) * np.cos(Y_mat)
        X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
        pos_surface = [X, Y, Z_mat]

        
        
      #  scatter = CustomScatter(pos=pos_scatter, color=(1, 0, 0, 1))
        surface = CustomSurface(*pos_surface,
                                glOptions='opaque',
                                color=(0.5, 0.5, 1, 1)
                                )
       # self.gl_view.addItem(scatter)
        self.gl_view.addItem(surface)

       # self.scatter=scatter
        self.surface=surface
        
        #scatter = CustomScatter(pos=pos)
        
        
        self.central_layout.addWidget(self.gl_view)     
    #    z_new = surface._z * 2
     #   surface.setData(z=z_new)
        #self.gl_view.addItem(scatter, ignoreBounds=False) 

        for i in range(1, 11):
            x = opengl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white")
            y = opengl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow")
            z = opengl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan")
            self.gl_view.addItem(x, ignoreBounds=True)
            self.gl_view.addItem(y, ignoreBounds=True)
            self.gl_view.addItem(z, ignoreBounds=True)
            
        self.showMaximized()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        #self.timer.start(500)
        
    def update(self):
        i,j=np.unravel_index(np.argmax(self.surface._z), self.surface._z.shape)
        z_new= self.surface._z.copy()
        z_new[i,j] = z_new[i,j]+0.5
        self.surface.setData(z=z_new)
        
        pos = self.scatter.pos.copy()
        idx = np.argmax(pos[:,0])
        pos[idx,0] = pos[idx,0]+0.1
        self.scatter.setData(pos=pos)
        #self.gl_view.vb.normalize_scene()



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    

    
