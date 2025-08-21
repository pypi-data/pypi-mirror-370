import csv
import json
import os

import numpy as np
import plotly.express as px
from plotly.io import write_json as plotly_write_json


class PlatformGraphs(object):
    """
    Handle the mapping of plotly graphs to a format which can be displayed by the KYOS platform.
    There can be at most one instance of this class (singleton design pattern).
    """

    _instance = None  # keep instance reference

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(PlatformGraphs, cls).__new__(cls)
            # initialize output directory for platform graphs
            output_location = os.path.join(os.getcwd(), 'Output', 'PlatformDisplay')
            if not os.path.exists(output_location):
                os.makedirs(output_location)
            cls._instance.output_location = output_location
        return cls._instance

    def save2disk(
        self,
        fig,
        filename: str,
        xanchor='left',
        yanchor='bottom',
        orientation='h',
        x=0.1,
        y=-0.075,
    ):
        """
        Save a plotly graph object in a json format and in a proper location on the KYOS servers.

        Args:
            fig (plotly.graph_objects): a fully built plotly figure
            filename (str): under what filename should the graph be saved on the server's hard-disk.
                Note that the filename plays a role in the order of displaying graphs in the fornt end.
            xanchor (str) : (Optional) One of ( "auto" | "left" | "center" | "right" ) Sets the title's horizontal
                alignment with respect to its x position. "left" means that the title starts at x. Default:"left"
            yanchor (str) : (Optional) One of ( "auto" | "top" | "middle" | "bottom" ) Sets the title's vertical
                alignment with respect to its y position. "top" means that the title's cap line is at y. Default:"bottom"
            orientation (str) : (Optional) one of ( "v" | "h" ). Sets the orientation of the legend. Default:"h"
            x (float): (Optional) number between or equal to -2 and 3 Sets the x position (in normalized coordinates)
                of the legend. KYOS Platform Defaults to 0.1
            y (float): (Optional) number between or equal to -2 and 3 Sets the y position (in normalized coordinates)
                of the legend. KYOS Platform Defaults to -0.075

        Examples:
            >>> graph_object = PlatformGraphs()
            >>> fig = px.histogram()
            >>> graph_object.save2disk(fig, filename="001_option_value")
        """
        # legend style same over the whole platform
        # -> styling can be moved to a separate method
        fig.update_layout(
            legend={
                'xanchor': xanchor,
                'yanchor': yanchor,
                'orientation': orientation,
                'x': x,
                'y': y,
            }
        )
        fig.update_layout(
            plot_bgcolor="#FFF",  # Sets background color to white
            xaxis=dict(
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False,  # Removes X-axis grid lines
            ),
            yaxis=dict(
                linecolor='gray',
                showgrid=True,  # Keep Y-axis grid lines
            ),
        )

        full_path = os.path.join(self.output_location, filename + "_plotly.json")
        plotly_write_json(fig, full_path)


def make_platform_table(
    df, table_name, bold_row_name=True, bold_column_name=True, columns_names=None
):
    """
    Function which outputs a pandas dataframe in a format which can be displayed in the KYOS platform.

    Args:
        df (pandas.Dataframe): A single row index is allowed. Multiple column indexes are allowed.
        bold_row_name (bool): Display the row name in bold font when showing it in the platform front-end
        bold_column_name (bool): Display the column name in bold font when showing it in the platform front-end
        columns_names (None|list): None: use the column names of the dataframe | list of list: user defined columns names (should include name for the row index as well)

    Notes:
        The data in the dataframe saved in a csv file in the desired format.

    Examples:
        >>> make_platform_table(data_df, '001_Option_Value', bold_column_name=True)
    """
    current_dir = os.path.dirname(os.path.realpath('__file__'))
    # create output directory
    output_dir = os.path.join(current_dir, 'Output/PlatformDisplay/')
    os.makedirs(output_dir, exist_ok=True)

    values = df.values.tolist()

    # attach row names to the values
    # currently only a single row name index is supported
    all_rows = df.index.values.tolist()
    n_row_indx = len(all_rows)
    for r in range(n_row_indx):
        name = all_rows[r]
        if bold_row_name == True and name != "":
            # add a tag to display the column name as bold
            name = "<b>" + name.replace('_', ' ') + "</b>"
        values[r].insert(0, name)

    # Generate columns names consistent with the platform display format
    if columns_names == None:
        all_columns = df.columns.values.tolist()
        all_col_names = []
        if type(all_columns[0]) == str:
            n_col_indx = 1
        else:  # tuple of all column indexes' name
            n_col_indx = len(all_columns[0])

        for i in range(n_col_indx):
            col_names = [""]  # currently only a single row name indexation is supported
            unique_name = None
            for col in all_columns:
                if n_col_indx == 1:
                    name = col  # col is just a string name
                else:
                    name = str(col[i])  # column is a tuple of string names

                if unique_name is not None and name == unique_name:
                    # a dataframe outputs the same name for a column when we have multi-indexing
                    # to display properly in the platform we drop the repeating names
                    name = ""
                else:
                    unique_name = name

                if bold_column_name == True and name != "":
                    # add a tag to display the column name as bold
                    name = "<b>" + name + "</b>"
                col_names.append(name)
            all_col_names.append(col_names)
    else:
        n_col_rows = len(columns_names[0])
        all_col_names = []
        for i in range(n_col_rows):
            col_names = [x[i] for x in columns_names]
            all_col_names.append(col_names)

    with open(output_dir + table_name + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(all_col_names)
    with open(output_dir + table_name + ".csv", "a") as f:
        writer = csv.writer(f)
        writer.writerows(values)


def make_platform_histogram(
    values, values_names, n_bins='auto', title=' ', output_filename='name'
):
    """
    Build a histogram based on one or more value series. The histogram will be displayed dynamically in the
    Kyos Analytical Platform.

    Args:
        values (numpy.ndarray): a histogram is built for each value series.
            The min/max of the histogram buckets is based on the smallest/biggest element of all series.
            [shape = (n_rows, n_series)]
        values_names (list): a list of string names for each series.
            [len = n_series]
        n_bins (int): how many bins should be used in the histogram.
        title (string): title of the histogram
        output_filename (string): beginning of the name of the output json file. It can be used to order how graphs are
            displayed in the platform. Graph with start of the name "001_" will be displayed first.

    Note:
        The histogram graph is build using the "Highcharts" package. For more info refer to [HighCharts](https://www.highcharts.com/demo/column-basic)

    Examples:
        >>> make_platform_histogram(values=values, values_names=['Value'],
        >>>                         title='Total Option Value (EUR)',
        >>>                         n_bins=20, output_filename='001_option_value')
    """
    # find bin edges based on all value series.
    bin_edges = np.histogram_bin_edges(values, bins=n_bins, range=None, weights=None)
    bin_means = list()
    for b in range(len(bin_edges[:-1])):
        bin_means.append((bin_edges[b] + bin_edges[b + 1]) / 2)

    # find the frequency histogram per a single series
    series = []
    n_series = values.shape[1]
    for i in range(n_series):
        hist, bin_edges_out = np.histogram(values[:, i], bins=bin_edges)
        hist_frequency = hist / hist.sum() * 100
        hist_frequency = hist_frequency.tolist()
        series.append({'name': values_names[i], 'data': hist_frequency})

    y_label = 'Frequency'
    column_chart = {
        'chart': {'type': 'column'},
        'title': {'text': title},
        'subtitle': {'text': ' '},
        'xAxis': {
            'labels': {'format': '{value:,.0f}'},
            'categories': bin_means,
            'crosshair': 'true',
        },
        'yAxis': {
            'labels': {'format': '{value} %'},
            'min': 0,
            'title': {
                'text': y_label,
            },
        },
        'tooltip': {
            'headerFormat': ' ',
            'pointFormat': '<p><span style="color:{series.color}">&#x25cf;</span> <b>{series.name}: </b>{point.y:.1f} %</p>',
            'shared': 'true',
            'useHTML': 'true',
        },
        'credits': {'text': 'Kyos Energy Consulting', 'href': 'http://www.kyos.com'},
        'plotOptions': {'column': {'pointPadding': 0, 'borderWidth': 0}},
        'series': series,
    }
    # output chart to json
    with open('Output/PlatformDisplay/' + output_filename + '_chart.json', 'w') as outfile:
        json.dump(column_chart, outfile)


def make_bar_column_chart(
    values,
    values_names,
    is_stacked=False,
    x_axis=None,
    title=' ',
    y_axis_title='values',
    output_filename='name',
    unit_name='unit',
):
    """
    Build a bar column chart based on one or more value series. The chart will be displayed dynamically in the
    Kyos Analytical Platform.

    Args:
        values (numpy.ndarray): y axis values
            [shape = (n_rows, n_series)]
        values_names (list): a list of string names for each series.
            [len = n_series]
        is_stacked (bool): indicator for chart type. basic column and stacked column chart supported
            False: Basic column chart
            True: Stacked column chart
        x_axis (None|list): list of x-axis values
            None: integer values will be used [1,2,3 .......]
            list: user defined x axis names (e.g. dates)
        title (string): title of the chart
        y_axis_title (string): title of the y-axis
        output_filename (string): beginning of the name of the output json file. It can be used to order how graphs are
            displayed in the platform. Graph with start of the name "001_" will be displayed first.
        unit_name (string): unit name of the values

    Note:
        The histogram graph is build using the "Highcharts" package. For more info refer to
        [HighCharts](https://www.highcharts.com/demo/column-basic)

    Examples:
        >>> make_bar_column_chart(values=np.zeros((2,2)), values_names=['series_1', 'series_2'],is_stacked=True,
        >>> x_axis=['2019-01-01', '2019-01-02'], title='Daily Positions', y_axis_title='Positions',
        >>> output_filename='001_option_value', unit_name='Lots')
    """

    if x_axis is None:
        x_axis = []
    y_axis_title = y_axis_title + ' (' + unit_name + ')'
    # Check chart type and create plot options
    plot_options = {}
    if is_stacked:
        plot_options = {'column': {'stacking': 'normal'}}
    # covert series to list
    series = []
    n_series = values.shape[1]
    for i in range(n_series):
        series_i = values[:, i].tolist()
        series.append({'name': values_names[i], 'data': series_i})

    bar_chart = {
        'chart': {'type': 'column'},
        'title': {'text': title},
        'xAxis': {'categories': x_axis},
        'yAxis': {'min': 0, 'title': {'text': y_axis_title}},
        'tooltip': {
            'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
            'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td>'
            + '<td style="padding:0"><b>{point.y:.1f} '
            + unit_name
            + '</b></td></tr>',
            'footerFormat': '</table>',
            'shared': 'true',
            'useHTML': 'true',
        },
        'credits': {'text': 'Kyos Energy Consulting', 'href': 'http://www.kyos.com'},
        'plotOptions': plot_options,
        'series': series,
    }

    # output chart to json
    with open('Output/PlatformDisplay/' + output_filename + '_chart.json', 'w') as outfile:
        json.dump(bar_chart, outfile)


def make_basic_line_chart(
    values,
    values_names,
    x_axis=None,
    title=' ',
    y_axis_title='values',
    output_filename='name',
    unit_name='unit',
):
    """
    Build a bar column chart based on one or more value series. The chart will be displayed dynamically in the
    Kyos Analytical Platform.

    Args:
        values (numpy.ndarray): y axis values
            [shape = (n_rows, n_series)]
        values_names (list): a list of string names for each series.
            [len = n_series]
        x_axis (None|list): list of x-axis values
            None: integer values will be used [1,2,3 .......]
            list: user defined x axis names (e.g. dates)
        title (string): title of the chart
        y_axis_title (string): title of the y-axis
        output_filename (string): beginning of the name of the output json file. It can be used to order how graphs are
            displayed in the platform. Graph with start of the name "001_" will be displayed first.
        unit_name (string): unit name of the values

    Note:
        The histogram graph is build using the "Highcharts" package. For more info refer to
         [HighCharts](https://www.highcharts.com/demo/column-basic)

    Examples:
        >>> make_basic_line_chart(values=np.zeros((2,2)), values_names=['series_1', 'series_2'],
        >>> x_axis=['2019-01-01', '2019-01-02'], title='Daily Positions', y_axis_title=' ',
        >>> output_filename='001_option_value', unit_name='Lots')
    """

    if x_axis is None:
        x_axis = []
    y_axis_title = y_axis_title + ' (' + unit_name + ')'
    # covert series to list
    series = []
    n_series = values.shape[1]
    for i in range(n_series):
        series_i = values[:, i].tolist()
        series.append({'name': values_names[i], 'data': series_i})

    line_chart = {
        'title': {'text': title},
        'xAxis': {'categories': x_axis},
        'yAxis': {'title': {'text': y_axis_title}},
        'tooltip': {
            'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
            'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td>'
            + '<td style="padding:0"><b>{point.y:.1f} '
            + unit_name
            + '</b></td></tr>',
            'footerFormat': '</table>',
            'shared': 'true',
            'useHTML': 'true',
        },
        'credits': {'text': 'Kyos Energy Consulting', 'href': 'http://www.kyos.com'},
        'series': series,
    }

    # output chart to json
    with open('Output/PlatformDisplay/' + output_filename + '_chart.json', 'w') as outfile:
        json.dump(line_chart, outfile)
