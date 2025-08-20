# -*- coding: utf-8 -*-
# @Author  : Paulo Radatz
# @Email   : paulo.radatz@gmail.com
# @File    : Circuit.py
# @Software: PyCharm

import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from py_dss_toolkit.results.SnapShot.SnapShotPowerFlowResults import SnapShotPowerFlowResults
from py_dss_toolkit.model.ModelBase import ModelBase
from py_dss_interface import DSS
from py_dss_toolkit.view.interactive_view.InteractiveCustomPlotStyle import InteractiveCustomPlotStyle
import numpy as np
import pandas as pd
from typing import Optional, List
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.ActivePowerSettings import ActivePowerSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.VoltageSettings import VoltageSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.UserDefinedNumericalSettings import UserDefinedNumericalSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.UserDefinedCategoricalSettings import UserDefinedCategoricalSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.PhasesSettings import PhasesSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.ThermalViolationSettings import ThermalViolationSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.VoltageViolationSettings import VoltageViolationSettings
from py_dss_toolkit.view.interactive_view.SnapShot.Circuit.CircuitBusMarker import CircuitBusMarker


class Circuit:

    def __init__(self, dss: DSS, results: SnapShotPowerFlowResults, model: ModelBase):
        self._dss = dss
        self._results = results
        self._model = model
        self._plot_style = InteractiveCustomPlotStyle()
        self._active_power_settings = ActivePowerSettings()
        self._voltage_settings = VoltageSettings()
        self._user_numerical_defined_settings = UserDefinedNumericalSettings()
        self._user_categorical_defined_settings = UserDefinedCategoricalSettings()
        self._phases_settings = PhasesSettings()
        self._thermal_violation_settings = ThermalViolationSettings()
        self._voltage_violation_settings = VoltageViolationSettings()

    def circuit_get_bus_marker(self, name: str, symbol: str = "square",
                               size: float = 10,
                               color: str = "black",
                               marker_name: Optional[str] = None):
        if not marker_name:
            marker_name = name
        return CircuitBusMarker(name=name,
                                symbol=symbol,
                                size=size,
                                color=color,
                                marker_name=marker_name)

    @property
    def circuit_plot_style(self):
        return self._plot_style

    @property
    def active_power_settings(self):
        return self._active_power_settings

    @property
    def voltage_settings(self):
        return self._voltage_settings

    @property
    def user_numerical_defined_settings(self):
        return self._user_numerical_defined_settings

    @property
    def phases_settings(self):
        return self._phases_settings

    @property
    def user_categorical_defined_settings(self):
        return self._user_categorical_defined_settings

    def _get_plot_settings(self, parameter):
        """
        Helper to get settings, results, hovertemplate, and numerical_plot for a given parameter.

        Supported parameters:
            - 'active power': Plots total active power (kW) per line.
            - 'reactive power': Plots total reactive power (kvar) per line.
            - 'voltage': Plots voltage statistics (mean/min/max) per line terminal.
            - 'user numerical defined': Plots user-defined numerical results.
            - 'phases': Plots the number of phases per line.
            - 'user categorical defined': Plots user-defined categorical results.
            - 'voltage violations': Highlights lines connected to buses with voltage violations.
            - 'thermal violations': Highlights lines with thermal (current) violations.

        Returns:
            settings: The settings object for the parameter.
            results: The results Series/DataFrame for plotting.
            hovertemplate: The hovertemplate string for Plotly.
            numerical_plot: Boolean, True if the plot is numerical/continuous, False if categorical/binary.
        """
        numerical_plot = True
        line_df = self._model.lines_df
        line_df['name'] = 'line.' + line_df['name']
        hovertemplate = ("<b>%{customdata[0]}</b><br>" +
                         "<b>Bus1: </b>%{customdata[1]} | <b>Bus2: </b>%{customdata[2]}<br>")
        if parameter == "active power":
            settings = self._active_power_settings
            columns = self._results.powers_elements[0].columns
            if "Terminal1.1" not in columns or "Terminal1.2" not in columns or "Terminal1.3" not in columns:
                raise ValueError("A non 3-phase circuit can't be plotted")
            results = self._results.powers_elements[0].loc[:, ["Terminal1.1", "Terminal1.2", "Terminal1.3"]].sum(axis=1)
            hovertemplate = hovertemplate + "<b>Total P: </b>%{customdata[3]:.2f} kW<br>"

        elif parameter == "reactive power":
            settings = self._active_power_settings
            columns = self._results.powers_elements[1].columns
            if "Terminal1.1" not in columns or "Terminal1.2" not in columns or "Terminal1.3" not in columns:
                raise ValueError("A non 3-phase circuit can't be plotted")
            results = self._results.powers_elements[0].loc[:, ["Terminal1.1", "Terminal1.2", "Terminal1.3"]].sum(axis=1)
            hovertemplate = hovertemplate + "<b>Total Q: </b>%{customdata[3]:.2f} kvar<br>"


        elif parameter == "voltage":
            settings = self._voltage_settings
            bus = settings.bus
            columns = self._results.voltages_elements[0].columns
            if bus == "bus1":
                p = 1
            else:
                p = 2
            if "Terminal1.1" not in columns or "Terminal1.2" not in columns or "Terminal1.3" not in columns:
                raise ValueError("A non 3-phase circuit can't be plotted")
            v = self._results.voltages_elements[0].loc[:, [f"Terminal{p}.1", f"Terminal{p}.2", f"Terminal{p}.3"]]
            if settings.nodes_voltage_value == "mean":
                results = v.mean(axis=1)
            elif settings.nodes_voltage_value == "min":
                results = v.min(axis=1)
            elif settings.nodes_voltage_value == "max":
                results = v.max(axis=1)
            hovertemplate = (hovertemplate +
                             f"<b>{settings.nodes_voltage_value.capitalize()} {bus.capitalize()} Voltage: </b>" +
                             "%{customdata[3]:.4f} pu<br>")
        elif parameter == "user numerical defined":
            settings = self._user_numerical_defined_settings
            parameter = settings.parameter
            unit = settings.unit
            num_decimal_points = settings.num_decimal_points
            if settings.results is None:
                raise Exception("No results found")
            else:
                results = settings.results
                hovertemplate = hovertemplate + f"<b>{parameter}:</b>" + " %{customdata[3]:" + f".{num_decimal_points}" + "f}" + f" {unit}<br>"
        elif parameter == "phases":
            numerical_plot = False
            settings = self._phases_settings
            results = line_df.set_index("name")["phases"]
            hovertemplate = hovertemplate + "<b>Phases: </b>%{customdata[3]}<br>"

        elif parameter == "voltage violations":
            numerical_plot = False
            settings = self._voltage_violation_settings
            under_v_bus_violations = self._results.violation_voltage_ln_nodes[0].index
            over_v_bus_violations = self._results.violation_voltage_ln_nodes[1].index
            both_v_bus_violations = under_v_bus_violations.intersection(over_v_bus_violations)
            results = line_df.set_index("name")
            results["bus"] = results['bus1'].str.split('.', n=1).str[0]
            results["violation"] = "0"
            results.loc[results['bus'].isin(under_v_bus_violations), 'violation'] = "1"
            results.loc[results['bus'].isin(over_v_bus_violations), 'violation'] = "2"
            results.loc[results['bus'].isin(both_v_bus_violations), 'violation'] = "3"
            results = results["violation"]
            hovertemplate = hovertemplate

        elif parameter == "thermal violations":
            numerical_plot = False
            settings = self._thermal_violation_settings
            line_violations = self._results.violation_currents_elements.index
            results = line_df.set_index("name")
            results["violation"] = "0"
            results.loc[results.index.isin(line_violations), 'violation'] = "1"
            results = results["violation"]
            hovertemplate = hovertemplate


        elif parameter == "user categorical defined":
            numerical_plot = False
            settings = self._user_categorical_defined_settings
            parameter = settings.parameter
            if settings.results is None:
                raise Exception("No results found")
            else:
                results = settings.results
                hovertemplate = hovertemplate + f"<b>{parameter}:</b>" + " %{customdata[3]}"
        else:
            raise ValueError(f"Unknown parameter: {parameter}")
        return settings, results, hovertemplate, numerical_plot

    def circuit_plot(self,
                     parameter="active power",
                     title: Optional[str] = "Circuit Plot",
                     xlabel: Optional[str] = 'X Coordinate',
                     ylabel: Optional[str] = 'Y Coordinate',
                     width_3ph: int = 3,
                     width_2ph: int = 3,
                     width_1ph: int = 3,
                     dash_3ph: Optional[str] = None,  #https://chart-studio.plotly.com/~neda/1950/solid-dashdot-dash-dot.embed
                     dash_2ph: Optional[str] = None,
                     dash_1ph: Optional[str] = None,
                     dash_oh: Optional[str] = None,
                     dash_ug: Optional[str] = None,
                     mark_buses: bool = True,
                     bus_markers: Optional[List[CircuitBusMarker]] = None,
                     show_colorbar: bool = True,
                     show: bool = True,
                     save_file_path: Optional[str] = None) -> Optional[go.Figure]:

        if mark_buses:
            mode = 'lines+markers'
        else:
            mode = 'lines'

        settings, results, hovertemplate, numerical_plot = self._get_plot_settings(parameter)
        line_df = self._model.lines_df
        line_df['name'] = 'line.' + line_df['name']
        num_phases = line_df.set_index("name")["phases"]
        line_type = line_df.set_index("name")["linetype"]

        buses = list()
        bus_coords = list()
        elements_list = [element.lower() for element in self._dss.circuit.elements_names]
        connections = []

        for element in elements_list:
            if element.split(".")[0].lower() in ["line"]:
                self._dss.circuit.set_active_element(element)
                if self._dss.cktelement.is_enabled:
                    bus1, bus2 = self._dss.cktelement.bus_names[0].split(".")[0].lower(), \
                        self._dss.cktelement.bus_names[1].split(".")[0].lower()
                    connections.append([element, (bus1.lower(), bus2.lower())])

                    if bus1 not in buses:
                        self._dss.circuit.set_active_bus(bus1)
                        x, y = self._dss.bus.x, self._dss.bus.y
                        bus_coords.append((x, y))
                        buses.append(bus1)

                    if bus2 not in buses:
                        self._dss.circuit.set_active_bus(bus2)
                        x, y = self._dss.bus.x, self._dss.bus.y
                        bus_coords.append((x, y))
                        buses.append(bus2)
        bus_coords = np.array(bus_coords)

        result_values = list()
        for element in elements_list:
            if element.split(".")[0].lower() in ["line"]:
                self._dss.circuit.set_active_element(element)
                if self._dss.cktelement.is_enabled:
                    result_values.append(results.loc[element])
        result_values = np.array(result_values)

        fig = go.Figure()
        self._plot_style.apply_style(fig)

        if numerical_plot:
            if not settings.colorbar_cmin:
                cmin = np.min(result_values)
            else:
                cmin = settings.colorbar_cmin

            if not settings.colorbar_cmax:
                cmax = np.max(result_values)
            else:
                cmax = settings.colorbar_cmax

            colorbar_trace_values = np.linspace(cmin, cmax, 100)

            norm_values = (result_values - cmin) / (cmax - cmin)

            for connection, value in zip(connections, norm_values):
                element, (bus1, bus2) = connection
                x0, y0 = bus_coords[buses.index(bus1)]
                x1, y1 = bus_coords[buses.index(bus2)]

                if x0 == 0 and y0 == 0:
                    continue
                if x1 == 0 and y1 == 0:
                    continue

                midpoint_x, midpoint_y = (x0 + x1) / 2, (y0 + y1) / 2

                color = sample_colorscale(settings.colorscale, value)[0]

                customdata = [[element, bus1, bus2, results.loc[element]], [element, bus1, bus2, results.loc[element]]]

                fig.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1],
                    mode=mode,
                    line=dict(
                        color=color,
                        width=self._get_phase_width(element, num_phases, width_1ph, width_2ph, width_3ph),
                        dash=self._get_dash(element, num_phases, dash_1ph, dash_2ph, dash_3ph, line_type, dash_oh, dash_ug)),
                    showlegend=False,
                    name='',
                    text=element,
                    hoverinfo='skip'
                ))

                fig.add_trace(go.Scatter(
                    x=[midpoint_x], y=[midpoint_y],
                    mode='markers',
                    marker=dict(size=0.1, color=color, opacity=0),
                    showlegend=False,
                    name="",
                    hoverinfo='text',
                    customdata=customdata,
                    hovertemplate=hovertemplate
                ))

            if show_colorbar:

                if settings.colorbar_tickvals is not None:
                    custom_tickvals = np.linspace(np.min(result_values), np.max(result_values),
                                                  settings.colorbar_tickvals)
                    if settings.colorbar_ticktext_decimal_points:
                        custom_ticktext = [f"{v:.{settings.colorbar_ticktext_decimal_points}f}" for v in
                                           custom_tickvals]
                    else:
                        custom_ticktext = [f"{v:.{0}f}" for v in custom_tickvals]
                else:
                    custom_tickvals = None
                    custom_ticktext = None

                if settings.colorbar_tickvals_list:
                    custom_tickvals = settings.colorbar_tickvals_list
                    custom_ticktext = settings.colorbar_tickvals_list

                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(
                        colorscale=settings.colorscale,
                        color=colorbar_trace_values,
                        cmin=cmin,
                        cmax=cmax,
                        colorbar=dict(
                            title=settings.colorbar_title,
                            thickness=20,
                            len=0.75,
                            ticks="outside",
                            tickvals=custom_tickvals,
                            ticktext=custom_ticktext
                        ),
                        showscale=True
                    ),
                    hoverinfo='none'
                ))
                fig.update_layout(
                    showlegend=False)

        else:
            legend_added = set()
            for connection in connections:
                element, (bus1, bus2) = connection
                x0, y0 = bus_coords[buses.index(bus1)]
                x1, y1 = bus_coords[buses.index(bus2)]

                if x0 == 0 and y0 == 0:
                    continue
                if x1 == 0 and y1 == 0:
                    continue

                midpoint_x, midpoint_y = (x0 + x1) / 2, (y0 + y1) / 2

                color = settings.color_map[results.loc[element]][1]
                category = settings.color_map[results.loc[element]][0]

                customdata = [[element, bus1, bus2, results.loc[element]], [element, bus1, bus2, results.loc[element]]]

                show_legend = False
                if category not in legend_added:
                    show_legend = True
                    legend_added.add(category)

                fig.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1],
                    mode=mode,
                    line=dict(
                        color=color,
                        width=self._get_phase_width(element, num_phases, width_1ph, width_2ph, width_3ph),
                        dash=self._get_dash(element, num_phases, dash_1ph, dash_2ph, dash_3ph, line_type, dash_oh, dash_ug)),
                    showlegend=show_legend,
                    name=category,
                    hoverinfo='skip',
                    legendgroup="group",
                    legendgrouptitle_text=settings.legendgrouptitle_text
                ))

                fig.add_trace(go.Scatter(
                    x=[midpoint_x], y=[midpoint_y],
                    mode='markers',
                    marker=dict(size=0.1, color=color, opacity=0),
                    showlegend=False,
                    name="",
                    hoverinfo='text',
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                    legendgroup="group"
                ))

                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        x=1,
                        y=1,
                        traceorder="normal"
                    )
                )

        if bus_markers:
            for marker in bus_markers:
                if marker.name in buses:
                    index = buses.index(marker.name)
                    bus_x, bus_y = bus_coords[index]
                    fig.add_trace(go.Scatter(
                        x=[bus_x],
                        y=[bus_y],
                        mode='markers',
                        marker=dict(
                            symbol=marker.symbol,
                            size=marker.size,
                            color=marker.color
                        ),
                        showlegend=False,
                        name="",
                        hoverinfo='text',
                        customdata=[[marker.name]],
                        hovertemplate=("<b>Bus: </b>%{customdata[0]}<br>"),
                    ))

        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
        )

        if save_file_path:
            fig.write_html(save_file_path)
        if show:
            fig.show()

        return fig

    def circuit_geoplot(self,
                     parameter="active power",
                     title: Optional[str] = "Circuit Plot",
                     width_3ph: int = 3,
                     width_2ph: int = 3,
                     width_1ph: int = 3,
                     mark_buses: bool = True,
                     bus_markers: Optional[List[CircuitBusMarker]] = None,
                     show_colorbar: bool = True,
                     show: bool = True,
                     map_style: Optional[str] = 'open-street-map', #https://plotly.com/python/tile-map-layers/
                     save_file_path: Optional[str] = None) -> Optional[go.Figure]:

        if mark_buses:
            mode = 'lines+markers'
        else:
            mode = 'lines'

        settings, results, hovertemplate, numerical_plot = self._get_plot_settings(parameter)
        line_df = self._model.lines_df
        line_df['name'] = 'line.' + line_df['name']
        num_phases = line_df.set_index("name")["phases"]
        line_type = line_df.set_index("name")["linetype"]

        buses = list()
        bus_coords = list()
        elements_list = [element.lower() for element in self._dss.circuit.elements_names]
        connections = []

        for element in elements_list:
            if element.split(".")[0].lower() in ["line"]:
                self._dss.circuit.set_active_element(element)
                if self._dss.cktelement.is_enabled:
                    bus1, bus2 = self._dss.cktelement.bus_names[0].split(".")[0].lower(), \
                        self._dss.cktelement.bus_names[1].split(".")[0].lower()
                    connections.append([element, (bus1.lower(), bus2.lower())])

                    if bus1 not in buses:
                        self._dss.circuit.set_active_bus(bus1)
                        x, y = self._dss.bus.x, self._dss.bus.y
                        bus_coords.append((x, y))
                        buses.append(bus1)

                    if bus2 not in buses:
                        self._dss.circuit.set_active_bus(bus2)
                        x, y = self._dss.bus.x, self._dss.bus.y
                        bus_coords.append((x, y))
                        buses.append(bus2)
        bus_coords = np.array(bus_coords)

        result_values = list()
        for element in elements_list:
            if element.split(".")[0].lower() in ["line"]:
                self._dss.circuit.set_active_element(element)
                if self._dss.cktelement.is_enabled:
                    result_values.append(results.loc[element])
        result_values = np.array(result_values)

        fig = go.Figure()

        if numerical_plot:
            if not settings.colorbar_cmin:
                cmin = np.min(result_values)
            else:
                cmin = settings.colorbar_cmin

            if not settings.colorbar_cmax:
                cmax = np.max(result_values)
            else:
                cmax = settings.colorbar_cmax

            colorbar_trace_values = np.linspace(cmin, cmax, 100)

            norm_values = (result_values - cmin) / (cmax - cmin)

            geo_df = pd.DataFrame()
            for connection, value in zip(connections, norm_values):
                element, (bus1, bus2) = connection
                x0, y0 = bus_coords[buses.index(bus1)]
                x1, y1 = bus_coords[buses.index(bus2)]
                if x0 == 0 and y0 == 0:
                    continue
                if x1 == 0 and y1 == 0:
                    continue
                color = sample_colorscale(settings.colorscale, value)[0]
                width = self._get_phase_width(element, num_phases, width_1ph, width_2ph, width_3ph)
                temp = pd.DataFrame({'element':[element, element, None],
                                     'x':[x0, x1, np.nan],
                                     'y':[y0, y1, np.nan],
                                     'color':[color, color, color],
                                     'bus1':[bus1, bus1, np.nan],
                                     'bus2':[bus2, bus2, np.nan],
                                     'value':[results.loc[element], results.loc[element], np.nan],
                                     'width':[width, width, width],
                                     })
                geo_df = pd.concat([geo_df, temp], axis=0, ignore_index=True)

            for (color, width), group in geo_df.groupby(['color', 'width']):
                fig.add_trace(go.Scattermap(
                    lat=group['y'],
                    lon=group['x'],
                    mode=mode,
                    line=dict(
                        color = color,
                        width = width,
                    ),
                    name='',
                    hoverinfo='skip',
                    showlegend=False
                    ))

                group_mid = group[['element', 'x', 'y']].groupby('element').mean().reset_index()
                group_mid = pd.merge(group_mid, group[['element', 'bus1', 'bus2', 'value']], on='element')

                fig.add_trace(go.Scattermap(
                    lat=group_mid['y'],
                    lon=group_mid['x'],
                    mode='markers',
                    marker=dict(size=0.1, opacity=0, color=color),
                    showlegend=False,
                    name="",
                    hoverinfo='text',
                    customdata=group_mid[['element', 'bus1', 'bus2', 'value']],
                    hovertemplate=hovertemplate
                ))

            if show_colorbar:

                if settings.colorbar_tickvals is not None:
                    custom_tickvals = np.linspace(np.min(result_values), np.max(result_values),
                                                  settings.colorbar_tickvals)
                    if settings.colorbar_ticktext_decimal_points:
                        custom_ticktext = [f"{v:.{settings.colorbar_ticktext_decimal_points}f}" for v in
                                           custom_tickvals]
                    else:
                        custom_ticktext = [f"{v:.{0}f}" for v in custom_tickvals]
                else:
                    custom_tickvals = None
                    custom_ticktext = None

                if settings.colorbar_tickvals_list:
                    custom_tickvals = settings.colorbar_tickvals_list
                    custom_ticktext = settings.colorbar_tickvals_list

                fig.add_trace(go.Scattermap(
                    lat=[None], lon=[None],
                    mode='markers',
                    marker=dict(
                        colorscale=settings.colorscale,
                        color=colorbar_trace_values,
                        cmin=cmin,
                        cmax=cmax,
                        colorbar=dict(
                            title=settings.colorbar_title,
                            thickness=20,
                            len=0.75,
                            ticks="outside",
                            tickvals=custom_tickvals,
                            ticktext=custom_ticktext,
                            x=0.9,
                            xanchor='left',
                            yanchor='middle',
                            bgcolor='rgba(0,0,0,0)',
                            borderwidth=0
                        ),
                        showscale=True
                    ),
                    hoverinfo='none',
                    showlegend = False,
                ))
                fig.update_layout(
                    showlegend=False)

        else:
            legend_added = set()
            geo_df = pd.DataFrame()
            for connection in connections:
                element, (bus1, bus2) = connection
                x0, y0 = bus_coords[buses.index(bus1)]
                x1, y1 = bus_coords[buses.index(bus2)]
                if x0 == 0 and y0 == 0:
                    continue
                if x1 == 0 and y1 == 0:
                    continue
                color = settings.color_map[results.loc[element]][1]
                category = settings.color_map[results.loc[element]][0]
                width = self._get_phase_width(element, num_phases, width_1ph, width_2ph, width_3ph)
                temp = pd.DataFrame({'element':[element, element, None],
                                     'x':[x0, x1, np.nan],
                                     'y':[y0, y1, np.nan],
                                     'color':[color, color, color],
                                     'category':[category,category,category],
                                     'bus1':[bus1, bus1, np.nan],
                                     'bus2':[bus2, bus2, np.nan],
                                     'value':[results.loc[element], results.loc[element], np.nan],
                                     'width':[width, width, width],
                                     })
                geo_df = pd.concat([geo_df, temp], axis=0, ignore_index=True)

            show_legend = False
            if category not in legend_added:
                show_legend = True
                legend_added.add(category)

            for (color, width, category), group in geo_df.groupby(['color', 'width', 'category']):
                fig.add_trace(go.Scattermap(
                    lat=group['y'],
                    lon=group['x'],
                    mode=mode,
                    line=dict(
                        color = color,
                        width = width,
                    ),
                    name=category,
                    hoverinfo='skip',
                    showlegend=show_legend
                    ))

                group_mid = group[['element', 'x', 'y']].groupby('element').mean().reset_index()
                group_mid = pd.merge(group_mid, group[['element', 'bus1', 'bus2', 'value']], on='element')

                fig.add_trace(go.Scattermap(
                    lat=group_mid['y'],
                    lon=group_mid['x'],
                    mode='markers',
                    marker=dict(size=0.1, opacity=0, color=color),
                    showlegend=False,
                    name="",
                    hoverinfo='text',
                    customdata=group_mid[['element', 'bus1', 'bus2', 'value']],
                    hovertemplate=hovertemplate
                ))

                fig.update_layout(
                    showlegend=True,
                    legend=dict(title=settings.legendgrouptitle_text,
                        x=0.85,
                        y=0.9,
                        traceorder="normal"
                    )
                )

        if bus_markers:
            for marker in bus_markers:
                if marker.name in buses:
                    index = buses.index(marker.name)
                    bus_x, bus_y = bus_coords[index]
                    fig.add_trace(go.Scattermap(
                        lon=[bus_x],
                        lat=[bus_y],
                        mode='markers',
                        marker=dict(
                            symbol=marker.symbol,
                            size=marker.size,
                            color=marker.color
                        ),
                        showlegend=False,
                        name="",
                        hoverinfo='text',
                        customdata=[[marker.name]],
                        hovertemplate=("<b>Bus: </b>%{customdata[0]}<br>"),
                    ))

        fig.update_layout(title=title,
                          margin={'r': 0, 't': 32 if title else 0, 'l': 0, 'b': 0},
                          map_style=map_style,
                          autosize=True,
                          hovermode='closest',
                          map = dict(
                              bearing=0,
                              center = dict(
                                  lat=np.mean([lat for _, lat in bus_coords if lat != 0]),
                                  lon=np.mean([lon for lon, _ in bus_coords if lon != 0])
                                  ),
                                  zoom = 10),
                                  )

        if save_file_path:
            fig.write_html(save_file_path)
        if show:
            fig.show()

        return fig


    def _get_phase_width(self, element, num_phases, width_1ph, width_2ph, width_3ph):
        num_phase = int(num_phases[element])
        if num_phase >= 3:
            result = width_3ph
        elif num_phase == 2:
            result = width_2ph
        elif num_phase == 1:
            result = width_1ph
        return result

    def _get_dash(self, element, num_phases, dash_1ph, dash_2ph, dash_3ph, line_type, dash_oh, dash_ug):
        num_phase = int(num_phases[element])
        lt = line_type[element]
        default = 'solid'
        if num_phase >= 3 and dash_3ph is not None:
            return dash_3ph
        elif num_phase == 2 and dash_2ph is not None:
            return dash_2ph
        elif num_phase == 1 and dash_1ph is not None:
            return dash_1ph
        elif lt == 'oh' and dash_oh is not None:
            return dash_oh
        elif lt == 'ug' and dash_ug is not None:
            return dash_ug
        return default
