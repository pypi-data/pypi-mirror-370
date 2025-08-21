import os

import pandas as pd

from kyoslib_py.kyos_api import call_kyos_api_v1


def write_curve_to_csv(curves, delTypes, grID, fullFileName):
    """
    Stores the forward curves in generalized data format on the disk in ./ForwardCurves
    directory.

    Args:
        curves (dict): HTTP response body which provided by kyos_api.call_kyos_api_v1
        delTypes (list): baseload:1, peak:2, offpeak:3
        grID (int): granularity id of the requested forward curve(e.g. half-hour:1, hour:2, day:3, month:5)
        fullFileName (str): full path of the file(e.g. "./ForwardCurves/ForwardCurveDaily_2_20200101")

    Note:
        The current implementation allows to store only data based on monthly granularity.

    Examples:
        >>> from kyoslib_py.forward_curve import write_curve_to_csv
        >>> curves = {}
        >>> data = {}
        >>> month = {}
        >>> baseload = [{'date':'2020-01-01', 'value':20.2}, {'date':'2020-02-01', 'value':30.3}]
        >>> month['baseload'] = baseload
        >>> data['month'] = month
        >>> curves['data'] = data
        >>> write_curve_to_csv(curves, [1, 2, 3], 5, "./ForwardCurves/ForwardCurveMonthlyDeliveryTypes_2_20200101")
    """

    if grID == 1:  # half-hourly
        return
    elif grID == 2:  # hourly
        return
    elif grID == 3:  # daily
        return
    elif grID == 5:  # monthly
        curves_df = pd.DataFrame()
        numDelType = len(delTypes)
        # read dates from base load and store in the table, column name should be "0" for the date column
        curves_df['0'] = [x['date'] for x in curves['data']['month']['baseload']]

        for i in range(numDelType):
            if delTypes[i] == 1:
                curves_df[str(delTypes[i])] = [
                    x['value'] for x in curves['data']['month']['baseload']
                ]
            elif delTypes[i] == 2:
                curves_df[str(delTypes[i])] = [
                    x['value'] for x in curves['data']['month']['peakload']
                ]
            elif delTypes[i] == 3:
                curves_df[str(delTypes[i])] = [
                    x['value'] for x in curves['data']['month']['offpeak']
                ]
        # write monthly curves to csv
        curves_df.to_csv(fullFileName, index=False)
    return


def get_curve_api(fwdCurveID, granularityID, deliveryTypes, tradingDates, isCSVWrite):
    """
    Performs API requests to KYOS API and stores the curve inputs in a generalized format in CSV
    files or returns a pandas.DataFrame.

    Args:
        fwdCurveID (int): id of the curve profile
        granularityID (int): half-hour:1, hour:2, day:3, month:5
        deliveryTypes (list|int): list of delivery type ids(int array), base load:1, peak:2, off-peak:3
        tradingDates (list): list of trading dates(string array) e.g. ['2019-01-01', '2019-01-02', '2019-01-03']
        isCSVWrite (bool): indicator of creating csv files, 0 or 1, we will provide a DataFrame in case of zero.

    Returns:
        (pandas.DataFrame): Contains all requested curves. If isCSVWrite equals 1 then the dataframe will be empty and
            the curves will be saved as CSV files on the disk in directory ./ForwardCurves.

    Note:
        KYOS API provides the curves with the daylight saving switches for the half-hourly and hourly curves.
        KYOS API supports base load, peak and off-peak delivery types only for monthly granularity.

    Examples:
        >>> from kyoslib_py.forward_curve import get_curve_api
        >>> arg = {'fwdCurveID': 4, 'granularityID': 5, 'deliveryTypes': [1, 2, 3],
        >>>        'tradingDates': ['2019-01-01', '2019-01-02'], 'isCSVWrite': 1}
        >>> curves_df = get_curve_api(**arg)
        >>> arg = {'fwdCurveID': 4, 'granularityID': 5, 'deliveryTypes': 1 ,
        >>>        'tradingDates': '2019-01-01', 'isCSVWrite': 1}
        >>> curves_df2 = get_curve_api(**arg)
    """
    # Initialize output directory
    curDir = os.getcwd()
    outputDir = os.path.join(curDir, 'ForwardCurves')
    if isCSVWrite and (not os.path.exists(outputDir)):
        os.mkdir(outputDir)
    forward_curves_df = pd.DataFrame()
    # ################################ INPUT VALIDATION ###########################################
    # Check the granularity input
    if granularityID == 1:
        fileName = f"ForwardCurveHalfHourlyDST_{fwdCurveID}_"
        granularity = 'half_hour'
    elif granularityID == 2:
        fileName = f"ForwardCurveHourlyDST_{fwdCurveID}_"
        granularity = 'hour'
    elif granularityID == 3:
        fileName = f"ForwardCurveDaily_{fwdCurveID}_"
        granularity = 'day'
    elif granularityID == 5:
        fileName = f"ForwardCurveMonthlyDeliveryTypes_{fwdCurveID}_"
        granularity = 'month'
    else:
        print('The granularity id:' + str(granularityID) + ' is not supported in KYOS API!!!')
        return forward_curves_df
    # in case of empty delivery type after the cleaning process, initialize base load in the list
    if deliveryTypes is None:
        deliveryTypes = [1]

    # Check the delivery type input, deliveryTypes should be a list
    if type(deliveryTypes) != list:
        deliveryTypes = [deliveryTypes]
    if len(deliveryTypes) == 0:
        deliveryTypes.append(1)  # in case of empty delivery type list, import the base load curve
    else:
        # remove the unsupported delivery types from the list
        deliveryTypes = [
            deliveryTypes for deliveryTypes in deliveryTypes if deliveryTypes in [1, 2, 3]
        ]

    # Check tradingDates, it should be provided as a list
    if type(tradingDates) != list:
        tradingDates = [tradingDates]

    # ########################################### IMPORT CURVES #######################################################
    numTradDays = tradingDates.__len__()
    for i in range(numTradDays):
        tradingDate_i = tradingDates[i]
        query = f"/curves/results/{fwdCurveID}/{tradingDate_i}?filter[granularity]={granularity}"

        status, data = call_kyos_api_v1(query)
        if 200 >= status < 300:
            if isCSVWrite == 1:  # in this case, we will store the curves on disk per trading dates
                fullName = os.path.join(
                    outputDir, f"{fileName}{tradingDate_i.replace('-', '')}.csv"
                )
                write_curve_to_csv(data, deliveryTypes, granularityID, fullName)
            else:  # in this case, we will store the curves in a dataframe
                curves_df_i = pd.DataFrame()
                numDelType = len(deliveryTypes)
                # update curve id and trading dates column
                if granularityID == 1:  # half-hourly
                    if data.get('data'):
                        numHhours = data['data']['half_hour']['baseload'].__len__()
                        curves_df_i['curve_id'] = [fwdCurveID for _ in range(numHhours)]
                        curves_df_i['trading_dates'] = [tradingDate_i for _ in range(numHhours)]

                        # read dates from base load and store in the table as delivery dates
                        curves_df_i['delivery_dates'] = [
                            x['date'] for x in data['data']['half_hour']['baseload']
                        ]
                        curves_df_i['baseload'] = [
                            x['value'] for x in data['data']['half_hour']['baseload']
                        ]
                    else:
                        print('There is no ' + granularity + ' curve for this profile!')
                        return forward_curves_df
                elif granularityID == 2:  # hourly
                    if data.get('data'):
                        numHours = data['data']['hour']['baseload'].__len__()
                        curves_df_i['curve_id'] = [fwdCurveID for _ in range(numHours)]
                        curves_df_i['trading_dates'] = [tradingDate_i for _ in range(numHours)]

                        # read dates from base load and store in the table as delivery dates
                        curves_df_i['delivery_dates'] = [
                            x['date'] for x in data['data']['hour']['baseload']
                        ]
                        curves_df_i['baseload'] = [
                            x['value'] for x in data['data']['hour']['baseload']
                        ]
                    else:
                        print('There is no ' + granularity + ' curve for this profile!')
                        return forward_curves_df
                elif granularityID == 3:  # daily
                    if data.get('data'):
                        numDays = data['data']['day']['baseload'].__len__()
                        curves_df_i['curve_id'] = [fwdCurveID for _ in range(numDays)]
                        curves_df_i['trading_dates'] = [tradingDate_i for _ in range(numDays)]

                        # read dates from base load and store in the table as delivery dates
                        curves_df_i['delivery_dates'] = [
                            x['date'] for x in data['data']['day']['baseload']
                        ]
                        curves_df_i['baseload'] = [
                            x['value'] for x in data['data']['day']['baseload']
                        ]
                    else:
                        print('There is no ' + granularity + ' curve for this profile!')
                        return forward_curves_df
                elif granularityID == 5:  # monthly
                    numMonths = data['data']['month']['baseload'].__len__()
                    curves_df_i['curve_id'] = [fwdCurveID for _ in range(numMonths)]
                    curves_df_i['trading_dates'] = [tradingDate_i for _ in range(numMonths)]

                    # read dates from base load and store in the table as delivery dates
                    curves_df_i['delivery_dates'] = [
                        x['date'] for x in data['data']['month']['baseload']
                    ]
                    for i in range(numDelType):
                        if deliveryTypes[i] == 1:
                            curves_df_i['baseload'] = [
                                x['value'] for x in data['data']['month']['baseload']
                            ]
                        elif deliveryTypes[i] == 2:
                            curves_df_i['peak'] = [
                                x['value'] for x in data['data']['month']['peakload']
                            ]
                        elif deliveryTypes[i] == 3:
                            curves_df_i['offpeak'] = [
                                x['value'] for x in data['data']['month']['offpeak']
                            ]

                forward_curves_df = pd.concat([forward_curves_df, curves_df_i])
            print(query + ' Imported!')
        else:
            print(query + ' could not be imported!')

    return forward_curves_df
