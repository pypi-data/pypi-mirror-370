import collections
import importlib.resources
import pathlib
from typing import Dict, Literal, Tuple

import dclab
import numpy as np
from PyQt6 import uic, QtCore, QtWidgets
import pyqtgraph as pg
from scipy.ndimage import binary_erosion

from ..compute.comp_stats import STAT_METHODS
from ... import idiom
from ..widgets import show_wait_cursor


#: default choices for x-axis in plots in descending order
AXES_DEFAULT_CHOICES_X = [
    "area_um", "index", "frame", "index_online", "time",
]
#: default choices for y-axis in plots in descending order
AXES_DEFAULT_CHOICES_Y = [
    "deform", "bright_avg", "bright_bc_avg", "bg_med", "index",
]


class QuickView(QtWidgets.QWidget):
    polygon_filter_created = QtCore.pyqtSignal()
    polygon_filter_modified = QtCore.pyqtSignal()
    polygon_filter_about_to_be_deleted = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        self._hover_ds_id = None
        self._hover_event_idx = None
        super(QuickView, self).__init__(*args, **kwargs)
        ref = importlib.resources.files(
            "dcscope.gui.quick_view") / "qv_main.ui"
        with importlib.resources.as_file(ref) as path_ui:
            uic.loadUi(path_ui, self)

        ref = importlib.resources.files(
            "dcscope.gui.quick_view") / "qv_style.css"
        with importlib.resources.as_file(ref) as path_css:
            stylesheet = pathlib.Path(path_css).read_text()
        self.groupBox_image.setStyleSheet(stylesheet)
        self.groupBox_trace.setStyleSheet(stylesheet)
        self.comboBox_x.default_choices = AXES_DEFAULT_CHOICES_X
        self.comboBox_y.default_choices = AXES_DEFAULT_CHOICES_Y

        self.setWindowTitle("Quick View")

        self._set_initial_ui()

        # Set scale options (with data)
        for cb in [self.comboBox_xscale, self.comboBox_yscale]:
            cb.clear()
            cb.addItem("linear", "linear")
            cb.addItem("logarithmic", "log")

        # Set marker hue options (with data)
        self.comboBox_hue.clear()
        self.comboBox_hue.addItem("KDE", "kde")
        self.comboBox_hue.addItem("feature", "feature")

        # Set look-up table options for isoelasticity lines
        self.comboBox_lut.clear()
        lut_dict = dclab.features.emodulus.load.get_internal_lut_names_dict()
        for lut_id in lut_dict.keys():
            self.comboBox_lut.addItem(lut_id, lut_id)
        # Set LE-2D-FEM-19 as a default
        idx = self.comboBox_lut.findData("LE-2D-FEM-19")
        self.comboBox_lut.setCurrentIndex(idx)

        # settings button
        self.toolButton_event.toggled.connect(self.on_tool)
        self.toolButton_poly.toggled.connect(self.on_tool)
        self.toolButton_settings.toggled.connect(self.on_tool)

        # polygon filter signals
        self.label_poly_create.setVisible(False)
        self.label_poly_modify.setVisible(False)
        self.pushButton_poly_save.setVisible(False)
        self.pushButton_poly_cancel.setVisible(False)
        self.pushButton_poly_delete.setVisible(False)
        self.pushButton_poly_create.clicked.connect(self.on_poly_create)
        self.pushButton_poly_save.clicked.connect(self.on_poly_done_save)
        self.pushButton_poly_cancel.clicked.connect(self.on_poly_done_cancel)
        self.pushButton_poly_delete.clicked.connect(self.on_poly_done_delete)
        self.comboBox_poly.currentIndexChanged.connect(self.on_poly_modify)
        self.update_polygon_panel()

        # event changed signal
        self.widget_scatter.scatter.sigClicked.connect(
            self.on_event_scatter_clicked)
        self.widget_scatter.update_hover_pos.connect(
            self.on_event_scatter_hover)
        self.spinBox_event.valueChanged.connect(self.on_event_scatter_spin)
        self.checkBox_image_contour.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_image_contrast.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_image_zoom.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_image_background.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_trace_raw.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_trace_legend.stateChanged.connect(
            self.on_event_scatter_update)
        self.checkBox_trace_zoom.stateChanged.connect(
            self.on_event_scatter_update)
        self.tabWidget_event.currentChanged.connect(
            self.on_event_scatter_update)

        # apply button
        self.toolButton_apply.clicked.connect(self.plot)
        # value changed signals for plot
        self.signal_widgets = [self.checkBox_downsample,
                               self.spinBox_downsample,
                               self.comboBox_x,
                               self.comboBox_y,
                               self.comboBox_xscale,
                               self.comboBox_yscale,
                               self.checkBox_isoelastics,
                               self.comboBox_z_hue,
                               self.comboBox_hue,
                               self.checkBox_hue,
                               self.comboBox_lut
                               ]
        for w in self.signal_widgets:
            if hasattr(w, "currentIndexChanged"):
                w.currentIndexChanged.connect(self.plot_auto)
            elif hasattr(w, "stateChanged"):
                w.stateChanged.connect(self.plot_auto)
            elif hasattr(w, "valueChanged"):
                w.valueChanged.connect(self.plot_auto)
        # copy statistics to clipboard
        self.toolButton_stats2clipboard.clicked.connect(
            self.on_stats2clipboard)

        # Set individual plots
        kw0 = dict(x=np.arange(10), y=np.arange(10))
        self.trace_plots = {
            "fl1_raw": pg.PlotDataItem(pen="#6EA068", **kw0),  # green
            "fl2_raw": pg.PlotDataItem(pen="#8E7A45", **kw0),  # orange
            "fl3_raw": pg.PlotDataItem(pen="#8F4D48", **kw0),  # red
            "fl1_median": pg.PlotDataItem(pen="#15BF00", **kw0),  # green
            "fl2_median": pg.PlotDataItem(pen="#BF8A00", **kw0),  # orange
            "fl3_median": pg.PlotDataItem(pen="#BF0C00", **kw0),  # red
        }
        for key in self.trace_plots:
            self.graphicsView_trace.addItem(self.trace_plots[key])
            self.trace_plots[key].setVisible(False)

        self.graphicsView_trace.plotItem.setLabels(
            left="Fluorescence [a.u.]", bottom="Event time [µs]")
        self.legend_trace = self.graphicsView_trace.addLegend(
            offset=(-.01, +.01))

        # qpi_pha cmaps
        self.cmap_pha = pg.colormap.get('CET-D1A', skipCache=True)
        self.cmap_pha_with_black = pg.colormap.get('CET-D1A', skipCache=True)
        self.cmap_pha_with_black.color[0] = [0, 0, 0, 1]

        # image display default range of values that the cmap will cover
        self.levels_image = (0, 255)
        self.levels_qpi_pha = (-3.14, 3.14)
        self.levels_qpi_amp = (0, 2)

        #: default parameters for the event image
        self.img_info = {
            "image": {
                "view_event": self.imageView_image,
                "view_poly": self.imageView_image_poly,
                "cmap": None,
                "cmap_changed": {"view_event": False,
                                 "view_poly": False},
                "kwargs": dict(autoLevels=False, levels=self.levels_image),
            },
            "qpi_pha": {
                "view_event": self.imageView_image_pha,
                "view_poly": self.imageView_image_poly_pha,
                "cmap": self.cmap_pha,
                "cmap_changed": {"view_event": False,
                                 "view_poly": False},
                "kwargs": dict(autoLevels=False, levels=self.levels_qpi_pha),
            },
            "qpi_amp": {
                "view_event": self.imageView_image_amp,
                "view_poly": self.imageView_image_poly_amp,
                "cmap": None,
                "cmap_changed": {"view_event": False,
                                 "view_poly": False},
                "kwargs": dict(autoLevels=False, levels=self.levels_qpi_amp),
            },
        }

        # set initial empty dataset
        self._rtdc_ds = None
        #: A cache for the event index plotted for a dataset
        self._dataset_event_plot_indices_cache = {}
        self.slot = None

        self._statistics_cache = collections.OrderedDict()

    def read_pipeline_state(self):
        plot = {
            "downsampling": self.checkBox_downsample.isChecked(),
            "downsampling value": self.spinBox_downsample.value(),
            "axis x": self.comboBox_x.currentData(),
            "axis y": self.comboBox_y.currentData(),
            "scale x": self.comboBox_xscale.currentData(),
            "scale y": self.comboBox_yscale.currentData(),
            "isoelastics": self.checkBox_isoelastics.isChecked(),
            "lut": self.comboBox_lut.currentData(),
            "marker hue": self.checkBox_hue.isChecked(),
            "marker hue value": self.comboBox_hue.currentData(),
            "marker hue feature": self.comboBox_z_hue.currentData(),
        }
        event = {
            "index": self.spinBox_event.value(),
            "image auto contrast": self.checkBox_image_contrast.isChecked(),
            "image contour": self.checkBox_image_contour.isChecked(),
            "image zoom": self.checkBox_image_zoom.isChecked(),
            "image background": self.checkBox_image_background.isChecked(),
            "trace legend": self.checkBox_trace_legend.isChecked(),
            "trace raw": self.checkBox_trace_raw.isChecked(),
            "trace zoom": self.checkBox_trace_zoom.isChecked(),
        }
        state = {
            "plot": plot,
            "event": event,
        }
        return state

    def write_pipeline_state(self, state):
        plot = state["plot"]
        for tb in self.signal_widgets:
            tb.blockSignals(True)
        # downsampling
        self.checkBox_downsample.setChecked(plot["downsampling"])
        self.spinBox_downsample.setValue(plot["downsampling value"])
        self.checkBox_hue.setChecked(plot["marker hue"])
        # combo box key selection
        self.update_feature_choices()
        for key, cb in [
            # axes labels
            ("axis x", self.comboBox_x),
            ("axis y", self.comboBox_y),
            # scaling
            ("scale x", self.comboBox_xscale),
            ("scale y", self.comboBox_yscale),
            # look up table
            ("lut", self.comboBox_lut),
            # marker hue
            ("marker hue value", self.comboBox_hue),
            ("marker hue feature", self.comboBox_z_hue),
        ]:
            idx = cb.findData(plot[key])
            idx = idx if idx > 0 else 0
            cb.setCurrentIndex(idx)

        # isoelastics
        self.checkBox_isoelastics.setChecked(plot["isoelastics"])
        for tb in self.signal_widgets:
            tb.blockSignals(False)
        if "event" in state:
            event = state["event"]
            self.checkBox_image_contrast.setChecked(
                event["image auto contrast"])
            self.checkBox_image_contour.setChecked(event["image contour"])
            self.checkBox_image_zoom.setChecked(event["image zoom"])
            self.checkBox_image_background.setChecked(
                event["image background"])
            self.spinBox_event.setValue(event["index"])
            self.checkBox_trace_raw.setChecked(event["trace raw"])
            self.checkBox_trace_legend.setChecked(event["trace legend"])

    def _check_file_open(self, rtdc_ds):
        """Check whether a dataset is still open"""
        if isinstance(rtdc_ds, dclab.rtdc_dataset.RTDC_HDF5):
            if rtdc_ds.h5file:
                # the file is open
                isopen = True
            else:
                isopen = False
        elif isinstance(rtdc_ds, dclab.rtdc_dataset.RTDC_Hierarchy):
            isopen = self._check_file_open(rtdc_ds.get_root_parent())
        else:
            # DCOR
            isopen = True
        return isopen

    def _set_initial_ui(self):
        self._hover_ds_id = None
        self._hover_event_idx = None
        # events label
        self.label_noevents.setVisible(False)
        self.enable_interface(False)

    def enable_interface(self, value):
        # Initially, only show the info about how QuickView works
        self.widget_tool.setEnabled(value)
        self.widget_scatter.setVisible(value)
        # stacked widget
        self.stackedWidget.setEnabled(value)
        # how-to label
        self.label_howto.setVisible(not value)

        if not value:
            self.imageView_image.setImage(np.full((10, 10), 200))
            self.imageView_image_amp.setImage(np.full((10, 10), 200))
            self.imageView_image_pha.setImage(np.full((10, 10), 200))

    @property
    def rtdc_ds(self):
        """Dataset to plot; set to None initially and if the file is closed"""
        if self._rtdc_ds is not None:
            if not self._check_file_open(self._rtdc_ds):
                self._rtdc_ds = None
        # now check again
        if self._rtdc_ds is None:
            self._set_initial_ui()
        return self._rtdc_ds

    @rtdc_ds.setter
    def rtdc_ds(self, rtdc_ds):
        if self._rtdc_ds is not rtdc_ds:
            self._hover_ds_id = None
            self._hover_event_idx = None

        self._rtdc_ds = rtdc_ds

        # Hide "Subtract Background"-Checkbox if feature
        # "image_bg" not in dataset
        contains_bg_feat = "image_bg" in rtdc_ds
        self.checkBox_image_background.setVisible(contains_bg_feat)

        # set the dataset for the FeatureComboBoxes
        self.comboBox_x.set_dataset(rtdc_ds)
        self.comboBox_y.set_dataset(rtdc_ds)
        self.comboBox_z_hue.set_dataset(rtdc_ds)

    # Showing image data
    ####################
    def get_event_image(self, ds, event, feat="image"):
        """Handle the image processing and contour processing for the event"""
        state = self.read_pipeline_state()
        if feat == "image":
            cell_img = self._prepare_event_image_image(ds, event, state)
        elif feat == "qpi_pha":
            cell_img = self._prepare_event_image_qpi_pha(ds, event, state)
        elif feat == "qpi_amp":
            cell_img = self._prepare_event_image_qpi_amp(ds, event, state)
        else:
            raise NotImplementedError(f"Image feature {feat} not implemented")

        return cell_img

    def _prepare_event_image_image(self, ds, event, state):
        cell_img = ds["image"][event]
        # apply background correction
        if "image_bg" in ds:
            if state["event"]["image background"]:
                bgimg = ds["image_bg"][event].astype(np.int16)
                cell_img = cell_img.astype(np.int16)
                cell_img = cell_img - bgimg + int(np.mean(bgimg))
        # automatic contrast
        if state["event"]["image auto contrast"]:
            vmin, vmax = cell_img.min(), cell_img.max()
            cell_img = (cell_img - vmin) / (vmax - vmin) * 255
        cell_img = self._convert_to_rgb(cell_img)
        # clip and convert to int
        cell_img = np.clip(cell_img, 0, 255)
        cell_img = np.require(cell_img, np.uint8, 'C')

        cell_img = self._insert_contour_and_zoom(
            cell_img,
            cmap_levels=self.img_info["image"]["kwargs"]["levels"],
            contour_style="red",
            ds=ds,
            event=event,
            state=state)

        return cell_img

    def _prepare_event_image_qpi_amp(self, ds, event, state):
        cell_img = ds["qpi_amp"][event]
        if state["event"]["image auto contrast"]:
            vmin, vmax = cell_img.min(), cell_img.max()
        else:
            vmin, vmax = self.levels_qpi_amp
        self.img_info["qpi_amp"]["kwargs"]["levels"] = (vmin, vmax)
        # to get the correct contour colour it is easier to view the
        # amplitude as an RGB image
        cell_img = self._convert_to_rgb(cell_img)

        cell_img = self._insert_contour_and_zoom(
            cell_img,
            cmap_levels=self.img_info["qpi_amp"]["kwargs"]["levels"],
            contour_style="red",
            ds=ds,
            event=event,
            state=state)

        return cell_img

    @staticmethod
    def _convert_to_rgb(cell_img):
        cell_img = cell_img.reshape(
            cell_img.shape[0], cell_img.shape[1], 1)
        return np.repeat(cell_img, 3, axis=2)

    def _prepare_event_image_qpi_pha(self, ds, event, state):
        cell_img = ds["qpi_pha"][event]
        # colormap levels
        if state["event"]["image auto contrast"]:
            vmin, vmax = self._vmin_max_around_zero(cell_img)
            if state["event"]["image contour"]:
                # offset required for auto-contrast with contour
                # two times the contrast range, divided by the cmap length
                # this essentially adds a cmap point for our contour
                offset = 2 * ((vmax - vmin) / len(self.cmap_pha.color))
                vmin = vmin - offset
        else:
            vmin, vmax = self.levels_qpi_pha
        self.img_info["qpi_pha"]["kwargs"]["levels"] = (vmin, vmax)

        # update colormap
        if state["event"]["image contour"]:
            new_cmap = self.cmap_pha_with_black
        else:
            new_cmap = self.cmap_pha
        if self.img_info["qpi_pha"]["cmap"] != new_cmap:
            self.img_info["qpi_pha"]["cmap"] = new_cmap
            # performance
            self.img_info["qpi_pha"]["cmap_changed"]["view_poly"] = True
            self.img_info["qpi_pha"]["cmap_changed"]["view_event"] = True

        cell_img = self._insert_contour_and_zoom(
            cell_img,
            cmap_levels=self.img_info["qpi_pha"]["kwargs"]["levels"],
            contour_style="lowest-level",
            ds=ds,
            event=event,
            state=state)

        return cell_img

    def _vmin_max_around_zero(self, cell_img):
        vmin_abs, vmax_abs = np.abs(cell_img.min()), np.abs(cell_img.max())
        v_largest = max(vmax_abs, vmin_abs)
        vmin, vmax = -v_largest, v_largest
        return vmin, vmax

    def _insert_contour_and_zoom(self,
                                 cell_img: np.ndarray,
                                 cmap_levels: Tuple[float, float],
                                 contour_style: Literal["red", "lowest-level"],
                                 ds: dclab.rtdc_dataset.RTDCBase,
                                 event: int,
                                 state: Dict):
        if "mask" in ds and len(ds["mask"]) > event:
            mask = ds["mask"][event]
            if state["event"]["image contour"]:
                # Compute contour image from mask. If you are wondering
                # whether this is kosher, please take a look at issue #76:
                # https://github.com/DC-analysis/dclab/issues/76
                cont = mask ^ binary_erosion(mask)
                if contour_style == "red":
                    # draw red contour for grayscale images
                    ch_red = cmap_levels[1] * 0.7
                    ch_other = int(cmap_levels[0]) if \
                        cmap_levels[1] == 255 else cmap_levels[0]
                    # assign channel values for contour
                    cell_img[cont, 0] = int(
                        ch_red) if cmap_levels[1] == 255 else ch_red
                    cell_img[cont, 1] = ch_other
                    cell_img[cont, 2] = ch_other
                elif contour_style == "lowest-level":
                    # use the lowest value from the colormap
                    # (used for e.g. phase images)
                    cell_img[cont] = cmap_levels[0]

            if state["event"]["image zoom"]:
                cell_img = self.image_zoom(cell_img, mask)

        return cell_img

    def get_event_image_and_show(self, ds, event, feat, view):
        """Convenience method for getting and showing event image"""
        cell_img = self.get_event_image(ds, event, feat)
        self.show_image(feat, view, cell_img)

    def show_image(self, feat, view, cell_img):
        self.img_info[feat][view].setImage(cell_img,
                                           **self.img_info[feat]["kwargs"])

        if (self.img_info[feat]["cmap"] is not None
                # performance
                and self.img_info[feat]["cmap_changed"][view]):
            self.img_info[feat]["cmap_changed"][view] = False
            self.img_info[feat][view].setColorMap(self.img_info[feat]["cmap"])
        self.img_info[feat][view].setVisible(True)

    @staticmethod
    def image_zoom(cell_img, mask):
        xv, yv = np.where(mask)
        idminx = xv.min() - 5
        idminy = yv.min() - 5
        idmaxx = xv.max() + 5
        idmaxy = yv.max() + 5
        idminx = idminx if idminx >= 0 else 0
        idminy = idminy if idminy >= 0 else 0
        shx, shy = mask.shape
        idmaxx = idmaxx if idmaxx < shx else shx
        idmaxy = idmaxy if idmaxy < shy else shy
        return cell_img[idminx:idmaxx, idminy:idmaxy]

    # Statistics
    ############
    def get_statistics(self):
        if self.rtdc_ds is not None:
            features = [self.comboBox_x.currentData(),
                        self.comboBox_y.currentData()]
            # cache statistics from
            dsid = "-".join(features
                            + [self.rtdc_ds.identifier,
                               self.rtdc_ds.filter._parent_hash]
                            )
            if dsid not in self._statistics_cache:
                stats = dclab.statistics.get_statistics(ds=self.rtdc_ds,
                                                        features=features,
                                                        methods=STAT_METHODS)
                self._statistics_cache[dsid] = stats
            if len(self._statistics_cache) > 1000:
                # avoid a memory leak
                self._statistics_cache.popitem(last=False)
            return self._statistics_cache[dsid]
        else:
            return None, None

    # Scatter Plot
    ##############
    @QtCore.pyqtSlot(object, object)
    def on_event_scatter_clicked(self, plot, point):
        """User clicked on scatter plot

        Parameters
        ----------
        plot: pg.PlotItem
            Active plot
        point: QPoint
            Selected point (determined by scatter plot widget)
        """
        if self.widget_scatter.events_plotted is not None:
            # plotted events
            plotted = self.widget_scatter.events_plotted
            # get corrected index
            ds_idx = np.where(plotted)[0][point.index()]
            self.show_event(ds_idx)
        # Note that triggering the toolButton_event must be done after
        # calling show_event, otherwise the first event is shown and
        # only after that the desired one. This would be a drawback when
        # events come from remote locations.
        #
        # `self.on_tool` (`self.toolButton_event`) takes care of this:
        # self.widget_scatter.select.setVisible(True)
        if not self.toolButton_event.isChecked():
            # emulate mouse toggle
            self.toolButton_event.setChecked(True)
            self.toolButton_event.toggled.emit(True)

    @QtCore.pyqtSlot(QtCore.QPointF)
    def on_event_scatter_hover(self, pos):
        """Update the image view in the polygon widget """
        if self.rtdc_ds is not None and self.toolButton_poly.isChecked():
            ds = self.rtdc_ds
            # plotted events
            plotted = self.widget_scatter.events_plotted
            spos = self.widget_scatter.scatter.mapFromView(pos)
            point = self.widget_scatter.scatter.pointAt(spos)
            # get corrected index
            event = np.where(plotted)[0][point.index()]

            # Only plot if we have not plotted this event before
            if (self._hover_ds_id != id(ds)
                    or self._hover_event_idx != event):
                # remember where we were
                self._hover_ds_id = id(ds)
                self._hover_event_idx = event
                view = "view_poly"
                for key in self.img_info.keys():
                    self.img_info[key][view].setVisible(False)

                try:
                    # if we have qpi data, image might be a different shape
                    if "qpi_pha" in ds:
                        self.get_event_image_and_show(
                            ds, event, "qpi_pha", view)
                        if "qpi_amp" in ds:
                            self.get_event_image_and_show(
                                ds, event, "qpi_amp", view)
                    elif "image" in ds:
                        self.get_event_image_and_show(
                            ds, event, "image", view)
                except IndexError:
                    # the plot got updated, and we still have the old data
                    self.get_event_image_and_show(ds, 0, "image", view)

    @QtCore.pyqtSlot(int)
    def on_event_scatter_spin(self, event):
        """Sping control for event selection changed"""
        self.show_event(event - 1)

    @QtCore.pyqtSlot()
    def on_event_scatter_update(self):
        """Just update the event shown"""
        event = self.spinBox_event.value()
        self.show_event(event - 1)

    # Polygon Selection
    ###################
    @QtCore.pyqtSlot()
    def on_poly_create(self):
        """User wants to create a polygon filter"""
        self.pushButton_poly_create.setEnabled(False)
        if not self.toolButton_poly.isChecked():
            # emulate mouse toggle
            self.toolButton_poly.setChecked(True)
            self.toolButton_poly.toggled.emit(True)
        self.comboBox_poly.setEnabled(False)
        self.groupBox_poly.setEnabled(True)
        self.label_poly_create.setVisible(True)
        self.pushButton_poly_save.setVisible(True)
        self.pushButton_poly_cancel.setVisible(True)
        # defaults
        self.lineEdit_poly.setText("Polygon Filter {}".format(
            dclab.PolygonFilter._instance_counter + 1))
        self.checkBox_poly.setChecked(False)
        self.widget_scatter.activate_poly_mode()
        # trigger resize and redraw
        mdiwin = self.parent()
        mdiwin.adjustSize()
        mdiwin.update()
        self.update()

    @QtCore.pyqtSlot()
    def on_poly_done(self, mode="none"):
        """User is done creating or modifying a polygon filter"""
        self.pushButton_poly_create.setEnabled(True)
        self.label_poly_create.setVisible(False)
        self.label_poly_modify.setVisible(False)
        self.pushButton_poly_save.setVisible(False)
        self.pushButton_poly_cancel.setVisible(False)
        self.pushButton_poly_delete.setVisible(False)
        # remove the PolyLineRoi
        self.widget_scatter.activate_scatter_mode()
        self.update_polygon_panel()
        if mode == "create":
            self.polygon_filter_created.emit()
        elif mode == "modify":
            self.polygon_filter_modified.emit()

    @QtCore.pyqtSlot()
    def on_poly_done_delete(self):
        # delete the polygon filter
        idp = self.comboBox_poly.currentData()
        if idp is not None:
            # There is a polygon filter that we want to delete
            self.polygon_filter_about_to_be_deleted.emit(idp)
            dclab.PolygonFilter.remove(idp)
            mode = "modify"
        else:
            mode = "none"
        self.on_poly_done(mode)

    @QtCore.pyqtSlot()
    def on_poly_done_cancel(self):
        self.on_poly_done()

    @QtCore.pyqtSlot()
    def on_poly_done_save(self):
        # save the polygon filter
        points = self.widget_scatter.get_poly_points()
        name = self.lineEdit_poly.text()
        inverted = self.checkBox_poly.isChecked()
        axes = self.widget_scatter.xax, self.widget_scatter.yax
        # determine whether to create a new polygon filter or whether
        # to update an existing one.
        idp = self.comboBox_poly.currentData()
        if idp is None:
            dclab.PolygonFilter(axes=axes, points=points, name=name,
                                inverted=inverted)
            mode = "create"
        else:
            pf = dclab.PolygonFilter.get_instance_from_id(idp)
            pf.name = name
            pf.inverted = inverted
            pf.points = points
            mode = "modify"
        self.on_poly_done(mode)

    @QtCore.pyqtSlot()
    def on_poly_modify(self):
        """User wants to modify a polygon filter"""
        self.pushButton_poly_create.setEnabled(False)
        self.comboBox_poly.setEnabled(False)
        self.groupBox_poly.setEnabled(True)
        self.label_poly_modify.setVisible(True)
        self.pushButton_poly_save.setVisible(True)
        self.pushButton_poly_cancel.setVisible(True)
        self.pushButton_poly_delete.setVisible(True)
        # get the polygon filter id
        idp = self.comboBox_poly.currentData()
        pf = dclab.PolygonFilter.get_instance_from_id(idp)
        # set UI information
        self.lineEdit_poly.setText(pf.name)
        self.checkBox_poly.setChecked(pf.inverted)
        # set axes
        state = self.read_pipeline_state()
        state["plot"]["axis x"] = pf.axes[0]
        state["plot"]["axis y"] = pf.axes[1]
        self.write_pipeline_state(state)
        self.plot()
        # add ROI
        self.widget_scatter.activate_poly_mode(pf.points)

    # Buttons
    #########
    @QtCore.pyqtSlot()
    def on_stats2clipboard(self):
        """Copy the statistics as tsv data to the clipboard"""
        h, v = self.get_statistics()
        if h is not None:
            # assemble tsv data
            tsv = ""
            for hi, vi in zip(h, v):
                tsv += "{}\t{:.7g}\n".format(hi, vi)
            QtWidgets.qApp.clipboard().setText(tsv)

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def on_tool(self, collapse=False):
        """Show and hide tools when the user selected a tool button"""
        toblock = [self.toolButton_event,
                   self.toolButton_poly,
                   self.toolButton_settings,
                   ]
        for b in toblock:
            b.blockSignals(True)
        # show extra data
        show_event = False
        show_poly = False
        show_settings = False
        sender = self.sender()
        if sender == self.toolButton_event:
            show_event = self.toolButton_event.isChecked()
        elif sender == self.toolButton_poly:
            show_poly = self.toolButton_poly.isChecked()
        elif sender == self.toolButton_settings:
            show_settings = self.toolButton_settings.isChecked()
        elif collapse:
            # show nothing
            pass
        else:
            # keep everything as-is but update the sizes
            show_event = self.stackedWidget.currentWidget() is self.page_event
            show_settings = (
                self.stackedWidget.currentWidget() is self.page_settings)
            show_poly = self.stackedWidget.currentWidget() is self.page_poly

        # toolbutton checked
        self.toolButton_event.setChecked(show_event)
        self.toolButton_poly.setChecked(show_poly)
        self.toolButton_settings.setChecked(show_settings)

        # stack widget visibility
        if show_event:
            self.stackedWidget.setCurrentWidget(self.page_event)
        elif show_settings:
            self.stackedWidget.setCurrentWidget(self.page_settings)
        elif show_poly:
            self.stackedWidget.setCurrentWidget(self.page_poly)

        self.widget_scatter.select.setVisible(show_event)  # point in scatter

        if show_event:
            # update event plot (maybe axes changed)
            self.on_event_scatter_update()

        for b in toblock:
            b.blockSignals(False)

        if not show_poly:
            self.on_poly_done()

        self.update()

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def plot(self):
        """Update the plot using the current state of the UI"""
        if self.rtdc_ds is not None:
            plot = self.read_pipeline_state()["plot"]
            downsample = plot["downsampling"] * plot["downsampling value"]
            hue_kwargs = {}
            if self.checkBox_hue.isChecked():
                hue_type = self.comboBox_hue.currentData()
                if hue_type == "kde":
                    hue_kwargs = {"kde_type": "histogram"}
                if hue_type == "feature":
                    hue_kwargs = {"feat": self.comboBox_z_hue.currentData()}
            else:
                hue_type = "none"
            self.widget_scatter.plot_data(rtdc_ds=self.rtdc_ds,
                                          slot=self.slot,
                                          downsample=downsample,
                                          xax=plot["axis x"],
                                          yax=plot["axis y"],
                                          xscale=plot["scale x"],
                                          yscale=plot["scale y"],
                                          hue_type=hue_type,
                                          hue_kwargs=hue_kwargs,
                                          isoelastics=plot["isoelastics"],
                                          lut_identifier=plot["lut"])
            # make sure the correct plot items are visible
            # (e.g. scatter select)
            self.on_tool()
            # update polygon filter axis names
            self.label_poly_x.setText(
                dclab.dfn.get_feature_label(plot["axis x"]))
            self.label_poly_y.setText(
                dclab.dfn.get_feature_label(plot["axis y"]))
            self.show_statistics()
            # Make sure features are properly colored in the comboboxes
            self.update_feature_choices()

    @QtCore.pyqtSlot()
    def plot_auto(self):
        """Update the plot only if the "Auto-apply" checkbox is checked"""
        if self.checkBox_auto_apply.isChecked():
            sender = self.sender()
            for cb, sen in [
                (self.checkBox_downsample, [self.spinBox_downsample]),
                (self.checkBox_hue, [self.comboBox_hue,
                                     self.comboBox_z_hue])]:
                # Do not replot if the user changes the options for a
                # disabled settings (e.g. downsampling, hue)
                if sender in sen:
                    if not cb.isChecked():
                        break
            else:
                self.plot()

    @show_wait_cursor
    @QtCore.pyqtSlot(int)
    def show_event(self, event):
        """Display the event data (image, contour, trace)

        Parameters
        ----------
        event: int
            Event index of the dataset; indices start at 0
            If set to None, the index from `self.spinBox_event`
            will be used.
        """
        if self.rtdc_ds is None:
            return

        # dataset
        ds = self.rtdc_ds
        self._dataset_event_plot_indices_cache[
            id(self.rtdc_ds.hparent)] = event
        event_count = ds.config["experiment"]["event count"]
        if event_count == 0:
            # nothing to do
            return
        # Update spin box data
        self.spinBox_event.blockSignals(True)
        self.spinBox_event.setValue(event + 1)
        self.spinBox_event.blockSignals(False)

        # Update selection point in scatter plot
        self.widget_scatter.setSelection(event)
        if self.tabWidget_event.currentIndex() == 0:
            # update image
            state = self.read_pipeline_state()
            self.groupBox_image.setVisible(False)

            view = "view_event"
            for key in self.img_info.keys():
                self.img_info[key][view].setVisible(False)

            # if we have qpi data, image might be a different shape
            if "qpi_pha" in ds:
                self.get_event_image_and_show(ds, event, "qpi_pha", view)
                if "qpi_amp" in ds:
                    self.get_event_image_and_show(ds, event, "qpi_amp", view)
            elif "image" in ds:
                self.get_event_image_and_show(ds, event, "image", view)

            self.groupBox_image.setVisible(True)

            if "trace" in ds:
                # remove legend items
                for item in reversed(self.legend_trace.items):
                    self.legend_trace.removeItem(item[1].text)
                self.legend_trace.setVisible(state["event"]["trace legend"])
                # get slot from identifier
                # time axis
                flsamples = ds.config["fluorescence"]["samples per event"]
                flrate = ds.config["fluorescence"]["sample rate"]
                fltime = np.arange(flsamples) / flrate * 1e6
                # temporal range (min, max, fl-peak-maximum)
                range_t = [fltime[0], fltime[-1], 0]
                # fluorescence intensity
                range_fl = [0, 0]
                for key in dclab.dfn.FLUOR_TRACES:
                    if key.count("raw") and not state["event"]["trace raw"]:
                        # hide raw trace data if user decided so
                        show = False
                    else:
                        show = True
                    flid = key.split("_")[0]
                    if key in ds["trace"] and show:
                        # show the trace information
                        tracey = ds["trace"][key][event]  # trace data
                        range_fl[0] = min(range_fl[0], tracey.min())
                        range_fl[1] = max(range_fl[1], tracey.max())
                        self.trace_plots[key].setData(fltime, tracey)
                        self.trace_plots[key].setVisible(True)
                        if state["event"]["trace zoom"]:
                            flpos = ds["{}_pos".format(flid)][event]
                            flwidth = ds["{}_width".format(flid)][event]
                            flmax = ds["{}_max".format(flid)][event]
                            # use the peak maximum to decide which range to use
                            if flmax > range_t[2]:
                                range_t[0] = flpos - 1.5 * flwidth
                                range_t[1] = flpos + 1.5 * flwidth
                                range_t[2] = flmax
                        # set legend name
                        ln = "{} {}".format(
                            self.slot.fl_name_dict[
                                "FL-{}".format(key[2])], key[4:])
                        self.legend_trace.addItem(self.trace_plots[key], ln)
                        self.legend_trace.update()
                    else:
                        self.trace_plots[key].setVisible(False)
                self.graphicsView_trace.setXRange(*range_t[:2], padding=0)
                if range_fl[0] != range_fl[1]:
                    self.graphicsView_trace.setYRange(*range_fl, padding=.01)
                self.graphicsView_trace.setLimits(xMin=0, xMax=fltime[-1])
                self.groupBox_trace.setVisible(True)
            else:
                self.groupBox_trace.setVisible(False)
        else:
            # only use computed features (speed)
            fcands = ds.features_local
            feats = [f for f in fcands if f in ds.features_scalar]
            lf = sorted([(dclab.dfn.get_feature_label(f), f) for f in feats])
            keys = []
            vals = []
            for lii, fii in lf:
                keys.append(lii)
                val = ds[fii][event]
                if fii in idiom.INTEGER_FEATURES:
                    val = int(np.round(val))
                vals.append(val)
            self.tableWidget_feats.set_key_vals(keys, vals)

    @show_wait_cursor
    @QtCore.pyqtSlot(object, object)
    def show_rtdc(self, rtdc_ds, slot):
        """Display an RT-DC measurement given by `path` and `filters`"""
        if np.all(rtdc_ds.filter.all) and rtdc_ds.format == "hierarchy":
            # No filers applied, no additional hierarchy child required.
            self.rtdc_ds = rtdc_ds
        else:
            # Create a hierarchy child so that the user can browse
            # comfortably through the data without seeing hidden events.
            self.rtdc_ds = dclab.new_dataset(
                rtdc_ds,
                identifier=f"child-of-{rtdc_ds.identifier}")
        event_count = self.rtdc_ds.config["experiment"]["event count"]
        if event_count == 0:
            self.enable_interface(False)
            self.label_noevents.setVisible(True)
            self.on_tool(collapse=True)
            return
        else:
            # make things visible
            self.enable_interface(True)
            self.label_noevents.setVisible(False)

        # get the state
        state = self.read_pipeline_state()
        plot = state["plot"]
        # remove event state (ill-defined for different datasets)
        state.pop("event")

        self.slot = slot

        # check whether axes exist in ds and change them to defaults
        # if necessary
        ds_features = sorted(self.rtdc_ds.features_scalar)
        if plot["axis x"] not in ds_features and ds_features:
            plot["axis x"] = ds_features[0]
        if plot["axis y"] not in ds_features and ds_features:
            if len(ds_features) > 1:
                plot["axis y"] = ds_features[1]
            else:
                # If there is only one feature, at least we
                # have set the state to a reasonable value.
                plot["axis y"] = ds_features[0]

        # set control ranges
        self.spinBox_event.blockSignals(True)
        self.spinBox_event.setMaximum(event_count)
        self.spinBox_event.setToolTip("total: {}".format(event_count))
        cur_value = self._dataset_event_plot_indices_cache.get(
            id(rtdc_ds), 0) + 1
        self.spinBox_event.setValue(cur_value)
        self.spinBox_event.blockSignals(False)

        # set quick view state
        self.write_pipeline_state(state)
        # scatter plot
        self.plot()
        # reset image view
        self.groupBox_image.setVisible(False)
        self.groupBox_trace.setVisible(False)
        # this only updates the size of the tools (because there is no
        # sender)
        self.on_tool()

    def show_statistics(self):
        h, v = self.get_statistics()
        if h is not None:
            self.tableWidget_stat.set_key_vals(keys=h, vals=v)

    def update_feature_choices(self):
        """Updates the axes comboboxes choices

        This is used e.g. when emodulus becomes available
        """
        if self.rtdc_ds is not None:
            # axes combobox choices
            self.comboBox_x.update_feature_list()
            self.comboBox_y.update_feature_list()
            self.comboBox_z_hue.update_feature_list()

    @QtCore.pyqtSlot()
    def update_polygon_panel(self):
        """Update polygon filter combobox etc."""
        if self.label_poly_modify.isVisible():
            # User is currently modifying a polygon filter (issue 148).
            # We discard the user's changes.
            self.on_poly_done_cancel()

        pfts = dclab.PolygonFilter.instances
        self.comboBox_poly.blockSignals(True)
        self.comboBox_poly.clear()
        self.comboBox_poly.addItem("Choose...", None)
        for pf in pfts:
            self.comboBox_poly.addItem(pf.name, pf.unique_id)
        self.comboBox_poly.blockSignals(False)
        self.comboBox_poly.setEnabled(True)
        if not pfts:
            # disable combo box if there are no filters
            self.comboBox_poly.setEnabled(False)
        self.groupBox_poly.setEnabled(False)
