"""Functionality related to the KYOS platform valuation interface. It allows the transfer of data between different
models within the platform."""

import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

from kyoslib_py.kyos_utils import dict_merge


class MetaData:
    """
    The MetaData class stores metadata information about a particular contract

    Attributes:
        isBuy (bool): Indicator that shows if the contract position is long (=true) or short (=false)
        isPhysical (bool): Indicator that shows if the contract is physical (=true) or financial (=false)
        entityId (int): ID number of the relevant entity
        counterpartyId (int): ID number of the counterparty
        confirmationNumber (str): Confirmation number of the contract (character string of numbers and letters)
        traderId (int): ID number of the trader responsible for the contract
        counterpartyTraderId (int): ID number of the trader of the counterparty
        bookId (int): ID number of the book for the trade
        documentationId (int): ID number of the documentation for the trade
        deliveryPoint (int): Number representing the delivery point location
        businessUnit (int): number representing the relevant business unit
        customFields (dict): To contain custom field information. Not always provided as part of a contract
        comment (str): Relevant comments related to the contract
    """

    def __init__(
        self,
        isBuy,
        isPhysical,
        entityId,
        counterpartyId,
        confirmationNumber,
        traderId,
        counterpartyTraderId,
        bookId,
        documentationId,
        deliveryPoint,
        businessUnit,
        customFields,
        comment,
    ):
        """
        Args:
            isBuy (bool): Indicator that shows if the contract position is long (=true) or short (=false)
            isPhysical (bool): Indicator that shows if the contract is physical (=true) or financial (=false)
            entityID (int): ID number of the relevant entity
            counterpartyID (int): ID number of the counterparty
            confirmationNumber (str): Confirmation number of the contract (character string of numbers and letters)
            traderID (int): ID number of the trader responsible for the contract
            counterpartyTraderId (int): ID number of the trader of the counterparty
            bookID (int): ID number of the book for the trade
            documentationId (int): ID number of the documentation for the trade
            deliveryPoint (int): Number representing the delivery point location
            businessUnit (int): number representing the relevant business unit
            customFields (dict): To contain custom field information. Not always provided as part of a contract
            comment (str): Relevant comments related to the contract
        """

        self.isBuy = isBuy
        self.isPhysical = isPhysical
        self.entityId = entityId
        self.counterpartyId = counterpartyId
        self.confirmationNumber = confirmationNumber
        self.traderId = traderId
        self.counterpartyTraderId = counterpartyTraderId
        self.bookId = bookId
        self.documentationId = documentationId
        self.deliveryPoint = deliveryPoint
        self.businessUnit = businessUnit
        self.comment = comment

        if customFields is not None:
            self.customFields = customFields


class CommData:
    """
    The CommData class stores data about a particular commodity, forward curve, currency and granularity combination,
    which itself is stored within an instance of the ValuationInterface class.

    Attributes:
        commodity_id (int): Commodity ID of the data to be stored
        forward_curve_id (int): Forward curve ID of the data to be stored.
        currency_id (int): Currency ID of the data to be stored
        granularity (int): Granularity ID number of the data to be stored e.g. 2 = hourly, 3 = daily, 5 - monthly.
        delivery_type (int): Delivery type ID of the data to be stored. e.g. 1 = baseload, 2 = peakload etc.
        type_output (list): List of strings indicating the type of time-series (by column) or simulations
        type_calculation (list): List of strings indicating the type of calculations associated with the time-series (by column) or simulations
        csv_filename (str): Name of the csv file to be saved which stores the data values
        dates (numpy array): 1D numpy array containing the dates of the data values
        values (numpy array): 2D numpy array containing the data values
        simulations (list): A list of instances of the SimulationData class, which contain specifically simulation data.

    Note:
        Note that only the parameters of the constructor are assigned to the object when called, and the other attributes
        are populated using the set_data method.

    Examples:
        >>> from kyoslib_py.valuation_interface
        >>> this_comm_data = CommData(commodity_id=2, forward_curve_id=33, currency_id=1,
                                granularity=5)
        >>> this_comm_data.commodity_id =
        2
    """

    def __init__(self, commodity_id, forward_curve_id, currency_id, granularity, delivery_type):
        """
        Args:
            commodity_id (int): Commodity ID of the data to be stored
            forward_curve_id (int): Forward curve ID of the data to be stored.
            currency_id (int): Currency ID of the data to be stored
            granularity (int): Granularity ID number of the data to be stored e.g. 2 = hourly, 3 = daily, 5 - monthly.
            delivery_type (int): Delivery type ID of the data to be stored. e.g. 1 = baseload, 2 = peakload etc.
        """
        self.commodity_id = commodity_id
        self.forward_curve_id = forward_curve_id
        self.granularity = granularity
        self.currency_id = currency_id
        self.delivery_type = delivery_type
        self.simulations = []
        self.dates = np.array([])
        self.values = np.array([])
        self.type_output = []
        self.type_calculation = []
        self.csv_filename = str()


class SimulationData:
    """
    The SimulationData class stores simulation data (dates and values) for a particular CommData object. Called within
    the set_data method of the ValuationInterface class.

    Attributes:
        csv_filename (str): Name of the csv file to be saved which stores the data values. Constructed automatically within the ValuationInterface class
        type_output (list): List with length one containing a string indicating the type of output (i.e. simulations)
        type_calculation (list): List with length one containing a string indicating the type of calculations associated with the simulations
        dates (numpy array): 1D numpy array containing the dates of the data values
        values (numpy array): 2D numpy array containing the data values

    Note:
        Note that only the parameters of the constructor are assigned to the object when called, and the other attributes
        are populated using the set_data method.

    Examples:
        >>> from kyoslib_py.valuation_interface
        >>> this_sim_data = SimulationData(csv_filename='example.csv', type_output=['simulation'],
            type_calculation = ['simulation'] , dates=date_array, values=simulation_array)
    """

    def __init__(self, csv_filename, type_output, type_calculation, dates=None, values=None):
        """
        Args:
            csv_filename (str): Name of the csv file to be saved which stores the data values
            type_output (list): List with length one containing a string indicating the type of output (i.e. simulations)
            type_calculation (list): List with length one containing a string indicating the type of calculations associated with the simulations
            dates (numpy array, optional): 1D numpy array containing the dates of the data values
            values (numpy array, optional): 2D numpy array containing the data values
        """
        self.csv_filename = csv_filename
        self.type_output = type_output
        self.type_calculation = type_calculation

        if dates is not None or values is not None:
            self.dates = dates
            self.values = values


class ValuationInterface:
    """
    The ValuationInterface class allows valuation data to be sent between models in a consistent format, using a JSON
    file which describes the data, and csv files which contain the data.

    Attributes:
        model_name (str): Name of the model from which data is being saved
        trading_date (str): String in format YYYYMMDD representing the trading date of the model run
        folder (string): Full path to the folder where JSON and csv files are to be saved
        profile_id (int): Profile ID of the model where data is being saved
        data (list): List which holds instances of the CommData class
        extra_model_data (dict): model specific information

    Note:
        Only one DataInterface can be constructed at a time. Each new instance of the class is appended to the list class
        variable all_interfaces

    Examples:
        >>> from kyoslib_py.valuation_interface import ValuationInterface
        >>> import datetime as dt
        >>> contract_output = ValuationInterface(model_name='Accumulator',
        >>>                                      trading_date=dt.datetime(2020, 1, 1),
        >>>                                      folder ='/Output', profile_id=13))
        >>> print(contract_output.model_name)
        >>> 'Accumulator'
    """

    # Class variable list which contains all instances of the class
    all_interfaces = []

    def __init__(self, model_name, trading_date, folder, profile_id=None):
        """
        Constructor of the ValuationInterface class.

        Args:
            model_name (str): Name of the model from which data is being saved
            trading_date (DateTime): DateTime object representing the trading date of the model run
            folder (string): Full path to the folder where JSON and csv files are to be saved
            profile_id (int, optional): Profile ID of the model where data is being saved
        """
        self.model_name = model_name
        #  Assign trading date attribute value as a string in format YYYYMMDD
        trading_year = str(trading_date.year)
        trading_month = trading_date.month
        trading_day = trading_date.day
        if trading_month < 10:
            trading_month = '0' + str(trading_month)
        else:
            trading_month = str(trading_month)
        if trading_day < 10:
            trading_day = '0' + str(trading_day)
        else:
            trading_day = str(trading_day)
        self.trading_date = trading_year + trading_month + trading_day
        self.folder = folder
        self.profile_id = profile_id
        self.data = []
        self.extra_model_information = dict()
        ValuationInterface.all_interfaces.append(
            self
        )  # Append to class variable with all instances

    def set_data(
        self,
        commodity_id,
        forward_curve_id,
        currency_id,
        granularity,
        delivery_type,
        type_output,
        type_calculation,
        dates,
        values,
    ):
        """
        The set_data method allows data (dates and values) to be added to an existing ValuationInterface class instance.
        The method automatically detects if time series or simulations are being added, and adds a CommData and/or
        SimulationData class instance to the data attribute of the ValuationInterface instance.

        Args:
            commodity_id (int): Commodity ID of the data to be stored
            forward_curve_id (int): Forward curve ID of the data to be stored.
            currency_id (int): Currency ID of the data to be stored
            granularity (int): Granularity ID number of the data to be stored e.g. 2 = hourly, 3 = daily, 5 - monthly.
            delivery_type (int): Delivery type ID of the data (e.g. 1 = baseload, 2 = peakload etc.)
            type_output (list): List with length one containing a string indicating the type of output (i.e. simulations)
            type_calculation (list): List with length one containing a string indicating the type of calculations associated with the simulations
            dates (numpy array, optional): 1D numpy array containing the dates of the data values
            values (numpy array, optional): 2D numpy array containing the data values

        Returns:
            (ValuationInterface): Instance of the ValuationInterface class object with CommData and/or SimulationData class instances appended

        Examples:
            >>> import numpy as np
            >>> import datetime as dt
            >>> from kyoslib_py.valuation_interface import ValuationInterface
            >>> contract_output = ValuationInterface(model_name='Accumulator',
            >>>                                      trading_date=dt.datetime(2020, 1, 1),
            >>>                                      folder ='/Output', profile_id=13))
            >>> volume_dates = np.array([dt.datetime(2020,1,1), dt.datetime(2020,2,1),
            >>>                          dt.datetime(2020,3,1)])
            >>> volume_sims = np.array([[110,120,130], [111,121,132], [115,124,137]])
            >>> contract_output.set_data(contract_id=1, forward_curve_id=1, currency_id=1, granularity=5,
            >>>                          delivery_type=1, type_output=['Simulation'],
            >>>                          type_calculation=['Volume'],
            >>>                          dates=volume_dates, values=volume_dates)
        """

        #  First check if we have simulations or time series:
        # 1. Simulations, if type_output and type_calculation has length one, and data has more than one column.
        # 2. Otherwise, Time Series. Length of type_output and type_calculation must match.
        num_col = len(type_output)
        if num_col == 1 and len(type_calculation) == 1 and values.shape[1] > 1:
            num_sim = values.shape[1]
        else:
            num_sim = 0
        if num_sim == 0 and (num_col != len(type_calculation) or num_col != values.shape[1]):
            exit(
                'Arguments type_output and type_calculation must have the same length as the number of columns in'
                + 'argument values (time series only)'
            )

        # Check if data to be added matches an existing CommData object.
        matching_comm = next(
            (
                x
                for x in self.data
                if (
                    x.commodity_id == commodity_id
                    and x.currency_id == currency_id
                    and x.forward_curve_id == forward_curve_id
                    and x.granularity == granularity
                    and x.delivery_type == delivery_type
                )
            ),
            None,
        )
        if matching_comm is not None:
            # A match with existing CommData object exists.
            matching_pos = self.data.index(matching_comm)
            if num_sim == 0:
                # Attach time series to an existing CommData object
                if matching_comm.dates.size != 0:
                    # Find unique dates between existing and new data
                    dates_cur = matching_comm.dates
                    values_cur = matching_comm.values
                    dates_all = np.unique(np.concatenate((dates_cur, dates)))
                    num_dates = len(dates_all)

                    # Find relevant indices of existing data and new data to be added
                    type_output_all = self.data[matching_pos].type_output
                    type_calculation_all = self.data[matching_pos].type_calculation
                    num_curr_col = len(self.data[matching_pos].type_output)
                    data_all = np.zeros([num_dates, num_curr_col])
                    i_curr = np.isin(
                        dates_all, dates_cur
                    )  # Logical index of location of existing date data

                    index = np.argsort(dates_cur)  # Index position of exiting dates to sort them
                    sorted_y = dates_cur[index]
                    sorted_index = np.searchsorted(sorted_y, dates_all)
                    xindex = np.take(index, sorted_index, mode="clip")
                    mask = dates_cur[xindex] != dates_all
                    i_curr_orig = np.ma.array(xindex, mask=mask)  # Sorted indices of existing data
                    i_curr_orig = np.ma.compressed(i_curr_orig)
                    data_all[i_curr, :] = values_cur[i_curr_orig, :]

                    i_new = np.isin(dates_all, dates)  # Index of new data to be added
                    index = np.argsort(dates)
                    sorted_y = dates[index]
                    sorted_index = np.searchsorted(sorted_y, dates_all)
                    xindex = np.take(index, sorted_index, mode="clip")
                    mask = dates[xindex] != dates_all
                    i_new_orig = np.ma.array(xindex, mask=mask)
                    i_new_orig = np.ma.compressed(
                        i_new_orig
                    )  # Indices of data required to sort the data correctly

                    #  Loop through columns of data which are being newly added
                    for c in range(num_col):
                        # See if there is matching with the output and calculation type. Existing data on the same
                        # date is overwritten
                        find_existing_outputs = [
                            i for i, x in enumerate(type_output_all) if x == type_output[c]
                        ]
                        find_existing_calcs = [
                            i
                            for i, x in enumerate(type_calculation_all)
                            if x == type_calculation[c]
                        ]
                        match = set(find_existing_outputs).intersection(find_existing_calcs)
                        if not match:
                            type_output_all = type_output_all + [type_output[c]]
                            type_calculation_all = type_calculation_all + [type_calculation[c]]
                            data_new = np.zeros([num_dates, 1])
                            data_new[i_new] = np.array([values[i_new_orig, c]]).T
                            data_all = np.concatenate([data_all, data_new], axis=1)
                        else:
                            ind_col = type_output_all.index(
                                type_output[c]
                            )  # Column of data to update
                            data_all[i_new, ind_col] = values[
                                i_new_orig, c
                            ]  # Update all new rows with new data
                else:
                    # CommData object exists, but only contains simulations
                    type_output_all = type_output
                    type_calculation_all = type_calculation
                    dates_all = dates
                    data_all = values
                    num_data = 1
                    self.data[matching_pos].csv_filename = (
                        self.model_name
                        + '_'
                        + str(self.profile_id)
                        + '_data_'
                        + str(num_data)
                        + '_'
                        + self.trading_date
                        + '.csv'
                    )

                # Update the CommData object with the new data
                self.data[matching_pos].type_output = type_output_all
                self.data[matching_pos].type_calculation = type_calculation_all
                self.data[matching_pos].dates = dates_all
                self.data[matching_pos].values = data_all

            else:
                # Add a SimulationData object to existing CommData object
                # Each SimulationData object contains a separate set of simulations:
                # - there can be no repeating sets of simulations
                # First, check if we have already a simulation data profile for this data
                # - if yes, overwrite the simulations
                # if no, create a new SimulationData object
                try:
                    matching_sim = next(
                        (
                            x
                            for x in self.data[matching_pos].simulations
                            if (
                                x.type_output == type_output
                                and x.type_calculation == type_calculation
                            )
                        ),
                        None,
                    )
                    ind_sim = self.data[matching_pos].simulations.index(matching_sim)
                    self.data[matching_pos].simulations[ind_sim].dates = dates
                    self.data[matching_pos].simulations[ind_sim].values = values
                except ValueError:
                    num_data = matching_pos + 1  # start count from 1 instead of Python 0th element
                    num_data_sim = len(self.data[matching_pos].simulations) + 1
                    csv_filename = (
                        self.model_name
                        + '_'
                        + str(self.profile_id)
                        + '_data_'
                        + str(num_data)
                        + '_sim_'
                        + str(num_data_sim)
                        + '_'
                        + self.trading_date
                        + '.csv'
                    )
                    simulation_data = SimulationData(
                        csv_filename=csv_filename,
                        type_output=type_output,
                        type_calculation=type_calculation,
                        dates=dates,
                        values=values,
                    )
                    self.data[matching_pos].simulations.append(simulation_data)

        else:
            # No match found, create new CommData object, and append it to the data attribute.
            comm_data = CommData(
                commodity_id=commodity_id,
                forward_curve_id=forward_curve_id,
                currency_id=currency_id,
                granularity=granularity,
                delivery_type=delivery_type,
            )
            self.data.append(comm_data)
            num_data = len(self.data)
            if num_sim == 0:
                # Time series data. Populate fields for newly added CommData object.
                csv_filename = (
                    self.model_name
                    + '_'
                    + str(self.profile_id)
                    + '_data_'
                    + str(num_data)
                    + '_'
                    + self.trading_date
                    + '.csv'
                )
                self.data[-1].csv_filename = csv_filename
                self.data[-1].type_output = type_output
                self.data[-1].type_calculation = type_calculation
                self.data[-1].dates = dates
                self.data[-1].values = values
            else:
                #  Simulations. Create new SimulationData object and append it to the CommData object.
                num_data_sim = (
                    1  # this is a new object, so there will only be one simulation dataset
                )
                csv_filename = (
                    self.model_name
                    + '_'
                    + str(self.profile_id)
                    + '_data_'
                    + str(num_data)
                    + '_sim_'
                    + str(num_data_sim)
                    + '_'
                    + self.trading_date
                    + '.csv'
                )
                simulation_data = SimulationData(
                    csv_filename=csv_filename,
                    type_output=type_output,
                    type_calculation=type_calculation,
                    dates=dates,
                    values=values,
                )
                self.data[-1].simulations.append(simulation_data)
        return self

    def export_data(self, commodity_id=None):
        """
        The export_data method exports data for the relevant commodity into csv files and a single JSON files that
        describes the relevant data.

        Args:
            commodity_id (int, optional):
                Commodity ID of the data to be exported. If not provided, all data is exported to csv and JSON.

        Examples:
            >>> import numpy as np
            >>> import datetime as dt
            >>> from kyoslib_py.valuation_interface import ValuationInterface
            >>> contract_output = ValuationInterface(model_name='Accumulator',
            >>>                                      trading_date=dt.datetime(2020, 1, 1),
            >>>                                      folder ='/Output', profile_id=13))
            >>> volume_dates = np.array([dt.datetime(2020,1,1), dt.datetime(2020,2,1),
            >>>                          dt.datetime(2020,3,1)])
            >>> volume_sims = np.array([[110,120,130], [111,121,132], [115,124,137]])
            >>> contract_output.set_data(contract_id=1, forward_curve_id=1, currency_id=1, granularity=5,
            >>>                          delivery_type=1, type_output=['Simulation'],
            >>>                          type_calculation=['Volume'],
            >>>                          dates=volume_dates, values=volume_dates)
            >>> contract_output.export_data()
        """

        #  JSON dumper object which ensures all subclasses within the ValuationInterface object are written to JSON.
        def dumper(obj):
            return obj.__dict__

        #  If commodity_id is not supplied, get list of all commodity IDs for export.
        if commodity_id is None:
            commodity_id = list(
                set([o.commodity_id for o in self.data])
            )  # returns a list of unique commodity ids
        output_folder = self.folder

        # Create a deepcopy of the ValuationInterface object, & remove the data and folder fields which we don't want to
        # export to JSON
        temp_interface = deepcopy(self)
        delattr(temp_interface, 'data')
        delattr(temp_interface, 'folder')

        temp_interface.data = []
        num_comm = len(commodity_id)
        if len(self.data) != 0:
            #  Loop through unique commodity IDs and build a boolean array where there is a match against the list of
            #  CommData objects
            for c in range(num_comm):
                ind_data = np.zeros([len(self.data)], dtype=bool)
                for j in range(len(self.data)):
                    if self.data[j].commodity_id == commodity_id[c]:
                        ind_data[j] = True
                    else:
                        ind_data[j] = False
                row_ind = np.where(ind_data == True)
                all_row_ind = range(len(row_ind[0]))
                # Loop through the index positions of this commodity and export data to csv
                for n in all_row_ind:
                    r = row_ind[0][n]  # row_ind it a tuple hence the 0th index
                    if pd.DatetimeIndex(self.data[r].values).empty is not True:
                        date_df = pd.DatetimeIndex(self.data[r].dates)
                        num_periods = self.data[r].dates.shape[0]
                        # Extract all data including dates as numpy array. Reshape required to make each column vector
                        # 2D (required for concatenation)
                        data_for_export = np.concatenate(
                            (
                                np.reshape(date_df.year.values, (num_periods, 1)),
                                np.reshape(date_df.month.values, (num_periods, 1)),
                                np.reshape(date_df.day.values, (num_periods, 1)),
                                np.reshape(date_df.hour.values, (num_periods, 1)),
                                np.reshape(date_df.minute.values, (num_periods, 1)),
                                self.data[r].values,
                            ),
                            axis=1,
                        )
                        output_folder_path = Path(output_folder)
                        csv_to_save = output_folder_path / self.data[r].csv_filename
                        num_data_cols = self.data[r].values.shape[1]
                        fmt_data = ['%10.10f'] * num_data_cols
                        fmt = ['%i', '%i', '%i', '%i', '%i'] + fmt_data
                        np.savetxt(csv_to_save, data_for_export, delimiter=",", fmt=fmt)

                    # Again create copy of the CommData object and remove fields to required for JSON
                    temp_data = deepcopy(self.data[r])
                    delattr(temp_data, 'dates')
                    delattr(temp_data, 'values')
                    delattr(temp_data, 'simulations')
                    temp_data.simulations = []

                    # If there are SimulationData objects present, follow the same process as above.
                    num_sim = len(self.data[r].simulations)
                    for s in range(num_sim):
                        date_df = pd.DatetimeIndex(self.data[r].simulations[s].dates)
                        num_periods = self.data[r].simulations[s].dates.shape[0]
                        data_for_export = np.concatenate(
                            (
                                np.reshape(date_df.year.values, (num_periods, 1)),
                                np.reshape(date_df.month.values, (num_periods, 1)),
                                np.reshape(date_df.day.values, (num_periods, 1)),
                                np.reshape(date_df.hour.values, (num_periods, 1)),
                                np.reshape(date_df.minute.values, (num_periods, 1)),
                                self.data[r].simulations[s].values,
                            ),
                            axis=1,
                        )
                        output_folder_path = Path(output_folder)
                        csv_to_save = output_folder_path / self.data[r].simulations[s].csv_filename
                        num_data_cols = self.data[r].simulations[s].values.shape[1]
                        fmt_data = ['%10.10f'] * num_data_cols
                        fmt = [
                            '%i',
                            '%i',
                            '%i',
                            '%i',
                            '%i',
                        ] + fmt_data  # Apply int formatting to date columns
                        np.savetxt(csv_to_save, data_for_export, delimiter=",", fmt=fmt)
                        temp_sim = deepcopy(self.data[r].simulations[s])
                        delattr(temp_sim, 'dates')
                        delattr(temp_sim, 'values')
                        temp_data.simulations.append(temp_sim)

                    temp_interface.data.append(temp_data)

        # Export copy of DI object with relevant subclasses with data etc. removed.
        json_file_path = output_folder_path / "ValuationInterface.json"
        with open(json_file_path, "w") as write_file:
            json.dump(temp_interface, write_file, default=dumper, indent=2)

    def set_metadata(self, input_folder):
        """
        A method to include a MetaData class object as a field within an existing ValuationInterface object.
        The metadata is saved ina file called 'metadata.json'.
        The metadata has a specific format, and it is used to pass extra data identifying an asset.
        Please contact KYOS for more information on the metadata.

        Args:
            input_folder (str): Full path of directory where the metadata.json file is located, without trailing file separator

        Examples:
            >>> from kyoslib_py.valuation_interface import ValuationInterface
            >>> contract_output = ValuationInterface(model_name='Accumulator',
            >>>                                      trading_date=dt.datetime(2020, 1, 1),
            >>>                                      folder ='/Output', profile_id=13))
            >>> contract_output.set_metadata('/metadata_folder')
        """

        json_filename = 'metadata.json'
        json_path = Path(input_folder)
        full_json_path = json_path / json_filename
        try:
            with open(full_json_path, "r") as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            exit(
                'The input metadata JSON file could not be found or there was an error loading it'
            )

        # Variable names must match those used in MATLAB to ensure consistency
        isBuy = data['isBuy']
        isPhysical = data['isPhysical']
        entityId = data['entityId']
        counterpartyId = data['counterpartyId']
        confirmationNumber = data['confirmationNumber']
        traderId = data['traderId']
        counterpartyTraderId = data['counterpartyTraderId']
        bookId = data['bookId']
        documentationId = data['documentationId']
        deliveryPoint = data['deliveryPoint']
        businessUnit = data['businessUnit']
        if "customFields" in data:
            customFields = data['customFields']
        else:
            customFields = None
        comment = data['comment']

        metadata = MetaData(
            isBuy,
            isPhysical,
            entityId,
            counterpartyId,
            confirmationNumber,
            traderId,
            counterpartyTraderId,
            bookId,
            documentationId,
            deliveryPoint,
            businessUnit,
            customFields,
            comment,
        )

        self.metadata = metadata

    def set_extra_model_data(self, data, overwrite=False):
        """
        The set_extra_model_data method allows to store extra model information in the ValuationInterface class instance.
        instead of updating only top-level keys, set_extra_model_data recurses down into dicts nested
        to an arbitrary depth.

        Args:
            data (dict):  a dictinary which conatins model specific information. e.g. accumulator object
            overwrite (bool): True, clear the dictonariy and append the new input,
                              False, append new input to the existing dictonary

        Returns:
            (ValuationInterface): Instance of the ValuationInterface class object with extra model data

        Examples:
            >>> import datetime as dt
            >>> from kyoslib_py.valuation_interface import ValuationInterface
            >>> contract_output = ValuationInterface(model_name='KyAccumulator',
            >>>                                      trading_date=dt.datetime(2020, 1, 1),
            >>>                                      folder ='/Output', profile_id=13)
            >>> extraInfo = {"accumulator": {"knock_out_price" : 150, "trigger_price": 130, "accumulation_price": 110}}
            >>> contract_output.set_extra_model_data(data=extraInfo)
            >>> extraInfo_2 = {"accumulator": {"knock_out_price" : 140, "trigger_price": 120, "accumulation_price": 100,
            >>> "buy": 1}}
            >>> contract_output.set_extra_model_data(data=extraInfo_2, overwrite=True)
        """
        # append the user defined key and values
        if overwrite:
            self.extra_model_information.clear()
            self.extra_model_information.update(data)
        else:
            self.extra_model_information = dict_merge(self.extra_model_information, data)
