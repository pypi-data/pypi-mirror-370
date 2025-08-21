import os
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


class CurrencySet:
    """
    This is the manager object of the currency class. This class loads the set of all available currencies.

    Attributes:
        currencies (list): list of objects

    Examples:
        >>> from kyoslib_py.settings import CurrencySet
        >>> currency_set = CurrencySet.from_csv()
        >>> currency = currency_set.get_currency(1)
        >>> currency.get_name()
        'EUR'
    """

    def __init__(self, currency_info_list: list = None):
        """
        Args:
            currency_info_list (list): list of dictionaries. Each dictionary has correct Currency format
        """
        self.currencies = [
            Currency(
                currencyId=currency_info["currencyId"],
                name=currency_info["name"],
                defaultCurrency=currency_info["defaultCurrency"],
                commodityId=currency_info["commodityId"],
                commodityGroupId=currency_info["commodityGroupId"],
                fwdCurveId=currency_info["fwdCurveId"],
                settleCurveId=currency_info["settleCurveId"],
                unitId=currency_info["unitId"],
                nameOfCents=currency_info.get("nameOfCents", "cents"),
            )
            for currency_info in currency_info_list
        ]

    # from_{data_source} methods
    @staticmethod
    def from_csv(csv_path: str = './Input/currency.csv') -> object:
        """
        This static method builds the CurrencySet object from xml.

        Args:
            csv_path (str): path to currency.csv

        Returns:
            kyoslib.CurrencySet object

        """
        df = pd.read_csv(csv_path, sep=',')
        currency_info_list = df.to_dict(orient='records')
        currency_set = CurrencySet(currency_info_list)
        return currency_set

    @staticmethod
    def from_json(json_path: str) -> object:
        """
        This static method builds the CurrencySet object from xml.

        Args:
            json_path (str): path to currency.json

        Returns:
            kyoslib.CurrencySet object

        """
        # load from json
        # ! to be done ! Here we will read the json file and map it to the currency_info_list ! #
        return

    # get methods
    def get_currency_list(self) -> list:
        return self.currencies

    def get_currency(self, requested_currency_id: int) -> object:
        """
        Args:
            requested_currency_id (int): the currency id from the server

        Returns:
            kyoslib.Currency object

        """
        # returns requested currency if found otherwise None
        return next(
            (
                currency
                for currency in self.get_currency_list()
                if currency.get_id() == requested_currency_id
            ),
            None,
        )


class Currency:
    """
    A Currency object contains key data pertaining to a currency as defined on the KYOS platform. Currency objects
    should be constructed using CurrencySet.from_csv(), which returns a currency_set = CurrencySet object. The individual
    currency object can be obtained using currency_set.get_currency(currency_id) method. See examples from CurrencySet class.

    Attributes:
        id (int): Currency ID number
        name (str): Name of the currency
        base_currency (bool): Indicates if a currency is the platform base (default) currency. Note: can be different from KySim model currency.
        commodity_id (int): Commodity ID number of the commodity corresponding to the FX pair that represents the exchange rate between this currency and the platform base currency.
        commodity_group_id (int): Id of the group number to which the relevant FX pair belongs, typically the id of the FX-rate group.
        fwd_curve_id (int): Id number of the forward curve of FX rates corresponding to this currency/FX pair.
        settle_curve_id (int): ID number of the settlement curve of FX rates corresponding to this currency/FX pair.
        unit_id (int): ID number corresponding to the unit of the currency, as defined on the KYOS platform. Typically, the generic "Currency" unit is applied to all FX-rates.
        name_of_cents: Name of currency cents (e.g. EUR cents, GBP pence, etc.)
    """

    # constructor
    def __init__(
        self,
        currencyId: int,
        name: str,
        defaultCurrency: bool,
        commodityId: int,
        commodityGroupId: int,
        fwdCurveId: int,
        settleCurveId: int,
        unitId: int,
        nameOfCents: str,
    ):
        self.id = currencyId
        self.name = name
        self.base_currency = defaultCurrency
        self.commodity_id = commodityId
        self.commodity_group_id = commodityGroupId
        self.fwd_curve_id = fwdCurveId
        self.settle_curve_id = settleCurveId
        self.unit_id = unitId
        self.name_of_cents = nameOfCents

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_fwd_curve_id(self):
        return self.fwd_curve_id

    def get_settle_curve_id(self):
        return self.settle_curve_id

    def get_base_currency(self):
        return self.base_currency

    def get_commodity_id(self):
        return self.commodity_id

    def get_commodity_group_id(self):
        return self.commodity_group_id

    def get_unit_id(self):
        return self.unit_id

    def name_of_cents(self):
        return self.name_of_cents


def make_currency(currency_dir: str = './Input/') -> list:
    """
    Returns a list of all available currency objects in the input currency.csv file generated by the KYOS platform.

    Args:
        currency_dir (str): path to the directory

    Returns:
        (list):  List of currency objects

    Note:
        CSV file called currency.csv must exist within the current working (project) directory. This file contains the relevant currency data.

    Examples:
        >>> from kyoslib_py.settings import make_currency
        >>> currencies = make_currency()
        >>> currencies[0].name
        'EUR'
        >>> next((x for x in currencies if x.get_id() == 2), None)
    """
    # create path to csv file
    csv_path = Path(currency_dir).joinpath('currency.csv')

    currency_set = CurrencySet.from_csv(csv_path=csv_path)
    if currency_set is not None:
        return currency_set.get_currency_list()
    else:
        return None


class DstSwitchesSet:
    """
    This is a set of Daylight saving switches. A method is created to get the timezone dependent dst switches.

    Attributes:
           commodities (list): list of objects
    """

    def __init__(self, dst_file_path: str = './Input/dst_switches.csv'):
        dst_file_path = Path(dst_file_path)
        if dst_file_path.exists() and os.stat(dst_file_path).st_size > 0:
            dst_switches_table = pd.read_csv(dst_file_path).values

            dst_switches_per_timezone = []
            unique_timezone_ids = np.unique(dst_switches_table[:, 0])

            for timezone_id in unique_timezone_ids:
                # find row index for the specific timezone
                index = dst_switches_table[:, 0] == timezone_id
                # filter out the data to create datetime
                year = dst_switches_table[index, 1]
                month = dst_switches_table[index, 2]
                day = dst_switches_table[index, 3]
                hour = dst_switches_table[index, 4]
                min = dst_switches_table[index, 5]

                nr_days = year.shape[0]
                dst_moments = [
                    datetime(year[i], month[i], day[i], hour[i], min[i], 0) for i in range(nr_days)
                ]
                dst_switch_values = dst_switches_table[index, 6]

                dst = pd.Series(dst_switch_values)
                dst.index = dst_moments

                dst_switches_per_timezone.append({"timezone_id": timezone_id, "dst_series": dst})
        else:
            dst_switches_per_timezone = [
                {"timezone_id": 0, "dst_series": pd.Series(data=None, dtype="float64")}
            ]

        self.dst_switches_per_timezone = dst_switches_per_timezone

    def get_dst_moments(self, timezone_id: int) -> pd.Series:
        """
        This method gets the time dependent DST series.

        Args:
            timezone_id (int): id of the relevant timezone

        Returns:
            pandas.Series: series with dst moment with the datetime on the index

        """
        series = [
            dst_switch_series['dst_series']
            for dst_switch_series in self.dst_switches_per_timezone
            if dst_switch_series['timezone_id'] == timezone_id
        ]
        if series == []:
            series = pd.Series(data=None, dtype="float64")
        else:
            series = series[0]
        return series


class CommoditySet:
    """
    This is the manager object of the commodity class. This class loads the set of all available commodites.

    Attributes:
           commodities (list): list of objects

    Examples:
        >>> from kyoslib_py.settings import CommoditySet
        >>> commodity_set = CommoditySet.from_xml()
        >>> commodity = commodity_set.get_commodity(5)
        >>> commodity.get_name()
        'TTF'
    """

    def __init__(self, commodity_info_list, currency_set):
        """
        Args:
            commodity_info_list (list): this is a list of dictionaries. Each dictionary contains the commodity info for
                a commodity object. This is the standard form in which a commodity is described, for example in the KYOS API.
            currency_set (CurrencySet): contains standard information about all currencies available in the KYOS platform.
        """
        # make a list of commodities that will be attached to the CommoditySet object
        self.commodities = []
        for commodity_info in commodity_info_list:
            # each commodity has one currency
            currency_id = commodity_info['CurrencyID']
            del commodity_info['CurrencyID']
            currency = currency_set.get_currency(currency_id)
            self.commodities.append(Commodity(**commodity_info, currency=currency))

    # from_{data_source} methods
    #   Here we combine the static methods that build the class. e.g. we have a from_xml method that build the class
    #   form a xml file.
    @staticmethod
    def from_xml(
        xml_path: str = './PrototypeSettings.xml',
        currency_set: object = None,
        calendar_set: object = None,
        dst_switches_set: object = None,
    ) -> object:
        """
        This method builds the CommoditySet object from a xml file.

        Args:
            xml_path: path to the xml file with commodity information
            currency_set: kyoslib.CurrencySet object
            calendar_set: kyoslib.CalendarSet object
            dst_switches_set: object

        Returns:
            kyoslib.CommoditySet object

        """
        if currency_set is None:
            currency_set = CurrencySet.from_csv()

        if calendar_set is None:
            calendar_set = CalendarSet.from_xml()

        if dst_switches_set is None:
            dst_switches_set = DstSwitchesSet()

        root = ET.parse(xml_path).getroot()
        comm_list = root.findall(".//CommoditiesInfo/CommodityInfo")

        commodity_info_list = []
        for commodity_node in comm_list:
            commodity_info = dict()

            commodity_info['ID'] = int(commodity_node.find('ID').text)
            commodity_info['Name'] = commodity_node.find('Name').text
            commodity_info['IsCent'] = bool(int(commodity_node.find('IsCent').text))

            commodity_info['UnitID'] = int(commodity_node.find('UnitID').text)
            commodity_info['Energy'] = float(commodity_node.find('Energy').text)
            commodity_info['GroupID'] = int(commodity_node.find('GroupID').text)
            commodity_info['GroupType'] = commodity_node.find('GroupType').text
            commodity_info['TimezoneName'] = commodity_node.find('TimezoneName').text
            commodity_info['TradingCalendarID'] = int(
                commodity_node.find('TradingCalendarID').text
            )
            commodity_info['EnergyLHV'] = float(commodity_node.find('EnergyLHV').text)
            commodity_info['TradingDayStart'] = int(commodity_node.find('TradingDayStart').text)
            commodity_info['UnitConversionType'] = int(
                commodity_node.find('UnitConversionType').text
            )
            commodity_info['IsDefaultGroupUnit'] = bool(
                commodity_node.find('IsDefaultGroupUnit').text
            )
            commodity_info['TradablePeriod'] = int(commodity_node.find('TradablePeriod').text)

            commodity_info['VolumeConversionFactor'] = float(
                commodity_node.find('VolumeConversionFactor').text
            )
            commodity_info['CarbonContent'] = float(commodity_node.find('CarbonContent').text)
            TimeZoneId = int(commodity_node.find('TimezoneId').text)
            commodity_info['TimezoneId'] = TimeZoneId
            commodity_info['dst_switches'] = dst_switches_set.get_dst_moments(TimeZoneId)
            commodity_info['TimezoneOffsetMinutes'] = int(
                commodity_node.find('TimezoneOffsetMinutes').text
            )

            # make delivery types
            delivery_types = DeliveryTypeSet.from_xml(
                xml_node=commodity_node, calendar_set=calendar_set
            )
            commodity_info['DeliveryTypes'] = delivery_types

            # we will only add the currecy obj, not the id as separate property.
            commodity_info['CurrencyID'] = int(commodity_node.find('CurrencyID').text)

            commodity_info_list.append(commodity_info)

        return CommoditySet(commodity_info_list, currency_set=currency_set)

    @staticmethod
    def from_json(
        json_path: str = '', currency_set: object = None, calendar_set: object = None
    ) -> object:
        # ! to be done ! #
        return

    # get methods
    # Via these methods you can access the attributes of the class
    def get_commodity_list(self) -> list:
        """
        This method can be used to a list of the commodities inside the commodity set

        Returns:
            (list): each element is a KYOS commodity

        """
        return self.commodities

    def get_commodity_id_list(self) -> list:
        """
        This method can be used to a list of ids of the commodities inside the commodity set

        Returns:
            (list): each element is a KYOS commodity id

        """
        return [x.id for x in self.get_commodity_list()]

    def get_commodity(self, requested_commodity_id: int) -> object:
        """
        Returns commodity object if commodity_id is found in the set of commodities.

        Args:
            requested_commodity_id (int): commodity id from the server

        Returns:
            kyoslib.Commodity object or None
        """
        return next(
            (
                commodity
                for commodity in self.get_commodity_list()
                if commodity.get_id() == requested_commodity_id
            ),
            None,
        )


class Commodity:
    """
    A Commodity object contains key data pertaining to a commodity as defined on the KYOS platform. Commodity objects
    should be constructed using the make_commodity() function.

    Attributes:
        id (int): Commodity ID number
        name (str): Name of the commodity
        is_cent (bool): Boolean which indicates if the commodity's currency units are in cents i.e. 1/100th of the main denomination unit
        currency (Currency): Currency object corresponding the Currency ID number for this commodity.
        unit_id (int): Unit id of the commodity
        energy_content (float): Energy content of commodity measred in Joules
        group_id (int): Group ID number of the commodity
        group_name (str): Group name of the commodity e.g. 'power' or 'gas'
        delivery_type_Set (object): kyoslib.DeliveryTypeSet object
        trading_calendar_id (int): ID number of the trading calendar that corresponds to this commodity
        timezone_id (int): ID of the timezone of the commodity
        timezone_name (str): Name of the timezone of the commodity
        timezone_offset_minutes (int): how many minutes dst
        trading_day_start (int): hour of start delivery, e.g. uk power starts at 23:00
        tradable_period_id (int): delivery_period_id of tradable granularity, e.g. Dutch power has hour granularity
        is_default_group_unit (bool): is this commodity unit the default of the group
        unit_conversion_type (int): type of conversion type, e.g. 0 is none, 1 is energy and 2 is volume.
            This is defined in the KYOS' setting screen
        volume_conversion_factor (float): conversion factor to commodity group default. E.g. if the commodity has default
            unit MT but the default of the group is in LBS, then this factor is approximately 2204.6
        carbon_content (float): Carbon content (kg/GJ)
        energy_lhw (float): lower heating value of a fuel commodity
        dst_switches (pd.Series): Series with dst switch moments for the commodity's timezone
    """

    # constructor
    def __init__(
        self,
        ID: int,
        Name: str,
        GroupID: int,
        GroupType: str,
        currency: object,
        Energy: float,
        IsCent: bool,
        UnitID: int,
        TimezoneName: str,
        DeliveryTypes: object,
        TradingCalendarID: int,
        EnergyLHV: float,
        TradingDayStart: int,
        UnitConversionType: int,
        VolumeConversionFactor: float,
        IsDefaultGroupUnit: bool,
        CarbonContent: float,
        TimezoneId: int,
        TimezoneOffsetMinutes: int,
        TradablePeriod: int,
        dst_switches: pd.Series,
    ):
        self.id = ID
        self.name = Name
        self.is_cent = IsCent
        self.currency = currency
        self.unit_id = UnitID
        self.energy_content = Energy  # measured in Joules
        self.group_id = GroupID
        self.group_name = GroupType
        self.delivery_type_set = DeliveryTypes
        self.trading_calendar_id = TradingCalendarID
        self.timezone_id = TimezoneId
        self.timezone_name = TimezoneName
        self.timezone_offset_minutes = TimezoneOffsetMinutes
        self.trading_day_start = TradingDayStart
        self.tradable_period_id = TradablePeriod
        self.is_default_group_unit = (
            IsDefaultGroupUnit  # if true, this unit_id is the default of the group
        )
        self.unit_conversion_type = UnitConversionType
        self.volume_conversion_factor = VolumeConversionFactor
        self.carbon_content = CarbonContent
        self.energy_lhw = EnergyLHV
        self.dst_switches = dst_switches

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_is_cent(self):
        return self.is_cent

    def get_currency(self):
        return self.currency

    def get_currency_id(self):
        return self.currency.get_id()

    def get_unit_id(self):
        return self.unit_id

    def get_energy_content(self):
        return self.energy_content

    def get_group_id(self):
        return self.group_id

    def get_group_name(self):
        return self.group_name

    def get_timezone_name(self):
        return self.timezone_name

    def get_delivery_type_set(self):
        return self.delivery_type_set

    def get_delivery_type(self, requested_id: int):
        return self.delivery_type_set.get_delivery_type(requested_id)

    def get_trading_calnder_id(self):
        return self.trading_calendar_id

    def get_volume_conversion_factor(self):
        return self.volume_conversion_factor

    def get_carbon_content(self):
        return self.carbon_content

    def get_energy_lhw(self):
        return self.energy_lhw

    def get_timezone_offset_minutes(self):
        return self.timezone_offset_minutes

    def get_trading_day_start(self):
        return self.trading_day_start

    def get_tradable_period_id(self):
        return self.tradable_period_id

    def get_is_default_group_unit(self):
        return self.is_default_group_unit

    def get_unit_conversion_type(self):
        return self.unit_conversion_type

    def get_dst_switches(self):
        return self.dst_switches

    def count_delivery_hours(
        self,
        output_granularity: int,
        start_date: datetime,
        end_date: datetime,
        delivery_type_id: int = 1,
    ):
        """
        Counts the number of delivery hours within a given time granularity and for a given delivery type ID.

        Args:
            output_granularity (int): Desired output granularity (day=3, month=5).
            start_date (datetime): Start date (sets time equal to 00:00:00).
            end_date (datetime): End date (sets time equal to 00:00:00).
            delivery_type_id (int): (optional) Delivery type ID (e.g. baseload=1, peakload=2). Default value is 1.

        Returns:
            (tuple): tuple containing:
                - (np.array): delivery_hours. Size: L-by-1 (where L is the number of time periods according to
                output_granularity).
                - (np.array): datetime_vec. Vector of datetime.date values from start_date to end_date, according to desired output
                granularity. Size: L-by-1 (where L is the number of time periods according to output_granularity).
        """
        # error checking: output_granularity value
        if (output_granularity != 3) and (output_granularity != 5):
            raise ValueError('output_granularity value must be either 3 or 5.')

        # create datetime vector of size L-by-1 (hours normalized at midnight)
        datetime_vec = [
            start_date.date() + timedelta(days=i)
            for i in range(0, (end_date - start_date).days + 1)
        ]

        n_periods = len(datetime_vec)
        # special case: baseload delivery
        if delivery_type_id == 1:
            # create total delivery matrix (size L-by-24)
            total_delivery_matrix = np.ones((n_periods, 24))

        else:
            # get delivery type data
            delivery_type = self.get_delivery_type(delivery_type_id)

            # get weekday delivery matrix
            weekday_delivery_matrix = delivery_type.get_delivery_moments()

            # match calendar dates to weekdays (Monday=0, Sunday=6)
            weekday_vec = [datetime_vec[i].weekday() for i in range(0, n_periods)]

            # get total delivery matrix (size L-by-24)
            total_delivery_matrix = weekday_delivery_matrix.iloc[weekday_vec]
            # convert DataFrame to array
            total_delivery_matrix = total_delivery_matrix.values

            # adjust holiday dates
            total_delivery_matrix = delivery_type.holidays_change(
                datetime_vec, total_delivery_matrix
            )

            # convert booleans to floats 0 and 1
            total_delivery_matrix = total_delivery_matrix.astype(float)

        # adjust DST switch dates
        total_delivery_matrix = self.dst_change(datetime_vec, total_delivery_matrix)

        # count delivery hours per days
        delivery_hours = total_delivery_matrix.sum(axis=1)

        # count delivery hours per month
        if output_granularity == 5:
            # convert to DataFrame
            delivery_hours_df = pd.DataFrame(delivery_hours, index=pd.DatetimeIndex(datetime_vec))
            # calculate delivery hours per month
            delivery_hours_df = delivery_hours_df.resample('ME').sum()
            # convert back to array
            delivery_hours = delivery_hours_df.iloc[:, 0].values
            # update datetime_vec
            datetime_vec = delivery_hours_df.index.date
        else:
            datetime_vec = np.array(datetime_vec)

        return delivery_hours, datetime_vec

    def get_delivery_hours(
        self,
        del_period_id: int,
        start_date: datetime,
        end_date: datetime,
        delivery_type_id: int = 1,
    ):
        """
        Returns the delivery hours and the delivery indicators between the start and end date
        granularity and for a given delivery type ID. Current implementation does not support to return delivery dates
        with the DST switches

        Args:
            del_period_id (int): delivery period/granularity of the dates (2-hour, 1 -half hour, 14 - quarter hour)
            start_date (datetime): Start date (sets time equal to 00:00:00).
            end_date (datetime): End date (sets time equal to 00:00:00).
            delivery_type_id (int): (optional) Delivery type ID (e.g. baseload=1, peakload=2). Default value is 1.

        Returns:
            delivery_dates(np.array)(NDays x 24 x period_per_hour): calendar delivery date
            ind_delivery(np.array) (NDays x 24 x period_per_hour): true/false if delivery happens in this period
        """
        # declare the delivery periods per hour,  ( hour = 1, half-hour = 2, quarter-hour = 4 )
        periods_per_hour = 1  # hour
        freq = "h"
        if del_period_id == 14:  # quarter-hour
            periods_per_hour = 4
            freq = "15min"
        elif del_period_id == 1:  # half-hour
            periods_per_hour = 2
            freq = "30min"

        # create datetime vector of size L-by-1 (hours normalized at midnight)
        datetime_vec = pd.date_range(start_date, end_date, freq='d', normalize=True)

        # special case: baseload delivery
        if delivery_type_id == 1:
            # create total delivery matrix (size L-by-24)
            total_delivery_matrix = np.ones((len(datetime_vec), 24 * periods_per_hour), dtype=bool)

        else:
            # get delivery type data
            delivery_type = self.get_delivery_type(delivery_type_id)

            # get weekday delivery matrix
            weekday_delivery_matrix = delivery_type.get_delivery_moments()

            # match calendar dates to weekdays (Monday=0, Sunday=6)
            weekday_vec = datetime_vec.weekday

            # get total delivery matrix (size L-by-24* periodperhour)
            total_delivery_matrix = weekday_delivery_matrix.iloc[weekday_vec]
            # convert DataFrame to array
            total_delivery_matrix = total_delivery_matrix.values

            # adjust holiday dates
            total_delivery_matrix = delivery_type.holidays_change(
                datetime_vec.date, total_delivery_matrix
            )

        # declare the delivery dates
        delivery_dates = pd.date_range(start_date, end_date + timedelta(hours=23), freq=freq)

        # declare the delivery indicator true/false
        ind_delivery = total_delivery_matrix.reshape((delivery_dates.shape[0], 1))

        return delivery_dates, ind_delivery

    def dst_change(self, date_vector: np.array, delivery_matrix: np.array):
        """
        Adjusts the number of delivery hours in the delivery matrix, according to DST switch dates.

        Args:
            date_vector (np.array): Vector of dates (daily granularity).
            delivery_matrix (np.array): Matrix of delivery hours for each date in date_vector. Elements in the matrix
                must be of type float, with value=1 (delivery) or value=0 (no delivery). Size: L-by-24, with L the
                length of date_vector.

        Returns:
            (np.array): Delivery matrix with adjusted delivery hours.
        """
        # error checking: delivery_matrix data type
        if delivery_matrix.dtype != float:
            raise TypeError('delivery_matrix must be of type float.')

        # get dst_switch
        dst_switch = self.get_dst_switches()

        # stop here if dst_switch is empty
        if dst_switch.empty:
            return delivery_matrix

        # find common dates between date_vector and dst_switch
        _, date_vector_index, dst_switch_index = np.intersect1d(
            date_vector, dst_switch.index.date, return_indices=True
        )

        # trading day start
        trading_day_start = self.get_trading_day_start()

        # artificial time shift if UK commodity
        if trading_day_start == 23:
            trading_day_start = 0
            # shift dst_switch index accordingly
            dst_switch.index = dst_switch.index + timedelta(hours=1)

        # time shift in hours
        dst_shift = dst_switch.values[dst_switch_index] / 60

        # time (hour) when DST switch takes place
        time_pre_dst = dst_switch.index.hour.values.astype(float)[dst_switch_index]
        time_post_dst = time_pre_dst + dst_shift

        # calculate delivery time adjustment on day before DST switch
        alpha_10 = trading_day_start - np.minimum(time_pre_dst, time_post_dst)
        alpha_11 = np.minimum(np.maximum(0, alpha_10), abs(dst_shift))
        adj_previous_day = np.sign(dst_shift) * alpha_11

        # calculate delivery time adjustment on DST switch day
        alpha_20 = np.maximum(time_pre_dst, time_post_dst) - trading_day_start
        alpha_21 = np.minimum(np.maximum(0, alpha_20), abs(dst_shift))
        adj_dst_day = np.sign(dst_shift) * alpha_21

        # find hour affected by DST switch
        delivery_hour_index = np.minimum(time_pre_dst, time_post_dst).astype(int)

        # check if DST switch happens during a delivery hour
        delivery_hour_check = (
            delivery_matrix[date_vector_index, dst_switch.index.hour[dst_switch_index]] == 1
        )

        # check if date_vector contains the day prior to DST switch, for all DST switches occurring within date_vector
        existing_previous_day = date_vector_index - 1 >= 0

        # adjust delivery matrix accordingly
        date__vector_index_prev_day = date_vector_index[existing_previous_day] - 1
        delivery_hour_index_prev_day = delivery_hour_index[existing_previous_day]

        delivery_matrix[date__vector_index_prev_day, delivery_hour_index_prev_day] -= (
            adj_previous_day[existing_previous_day] * delivery_hour_check[existing_previous_day]
        )

        delivery_matrix[date_vector_index, delivery_hour_index] -= (
            adj_dst_day * delivery_hour_check
        )

        return delivery_matrix


def make_commodity(
    xml_folder: str = None,
    xml_path: str = 'PrototypeSettings.xml',
    currencies: list = None,
    json_path: str = None,
    commodity_info_list: list = None,
) -> list:
    """
    Returns a list of all available commodity objects in the input xml file generated by the KYOS platform

    Args:
        xml_path (str): Full path to xml file including name

    Returns:
        (list): List of commodity objects

    Note:
        XML settings file called KyPythonSettings.xml must exist within the current working (project) directory. This file
        contains the commodity information.
        The make_currency function should be run before make_commodity

    Examples:
        >>> from kyoslib_py.settings import make_commodity
        >>> commodity_set = make_commodity()
        >>> commodity_set[0].group_name
        'power'
        >>> next((x for x in commodity_set if x.id == 5), None)
    """
    # create path to xml file
    if xml_folder is None:
        xml_path = Path(xml_path).absolute()
    else:
        xml_path = Path(xml_path).joinpath(xml_path)

    commodity_set = CommoditySet.from_xml(xml_path=xml_path)

    if commodity_set is not None:
        return commodity_set.get_commodity_list()
    else:
        return None


class DeliveryTypeSet:
    """
    This is the manager object of the DeliveryType class. This class loads the set of all available delivery types
    for a commodity. For example, delivery type can be base and peakload.

    Examples:
        >>> from kyoslib_py.settings import DeliveryTypeSet
        >>> delivery_types = DeliveryTypeSet.from_xml(xml_node=commodity_node, calendar_set=calendar_set)
        >>> baseload = delivery_types.get_delivery_type(1)

    """

    def __init__(self, delivery_type_info_list: list = None) -> object:
        if delivery_type_info_list is None:
            # to be done, raise error
            return

        self.delivery_types = [
            DeliveryType(**delivery_type_info) for delivery_type_info in delivery_type_info_list
        ]

    # from_{data_source} methods
    @staticmethod
    def from_xml(xml_node: object = None, calendar_set: object = None) -> object:
        delivery_types_nodes = xml_node.findall('.//DeliveryTypes/')
        delivery_types_nodes = [dtn for dtn in delivery_types_nodes if dtn.find('ID') != None]
        delivery_type_info_list = []
        nr_delivery_types = len(delivery_types_nodes)
        if nr_delivery_types != 0:
            for delivery_type_node in delivery_types_nodes:
                delivery_type_info = dict()

                delivery_type_info['ID'] = int(delivery_type_node.find('ID').text)

                calendar_id = int(delivery_type_node.find('CalendarID').text)
                delivery_type_info['Calendar'] = None
                if (calendar_id != 0) & (calendar_set != None):
                    delivery_type_info['Calendar'] = calendar_set.get_calendar(calendar_id)

                delivery_type_info['holiday_delivery_type'] = False
                if delivery_type_node.find('Days/Hol') is not None:
                    if delivery_type_node.find('Days/Hol').text is not None:
                        delivery_type_info['holiday_delivery_type'] = True

                delivery_type_info['DeliveryMoments'] = DeliveryType.create_del_types(
                    delivery_type_node=delivery_type_node,
                    holiday_del_type=delivery_type_info['holiday_delivery_type'],
                )

                delivery_type_info_list.append(delivery_type_info)
        return DeliveryTypeSet(delivery_type_info_list)

    @staticmethod
    def from_json(json_key: dict = None, calendar_set: object = None):
        all_delivery_types = json_key
        delivery_type_info_list = []
        for delivery_type_dict in all_delivery_types:
            delivery_moments = delivery_type_dict['Days']

            delivery_type_info = dict()
            delivery_type_info['ID'] = delivery_type_dict['ID']
            calendar_id = delivery_type_dict['CalendarID']

            delivery_type_info['Calendar'] = None
            if (calendar_id != 0) & (calendar_set != None):
                delivery_type_info['Calendar'] = calendar_set.get_calendar(calendar_id)

            delivery_type_info['holiday_delivery_type'] = False
            if delivery_moments['Hol'] != {}:
                # when there is no delivery on holiday, the object is an empty dict
                delivery_type_info['holiday_delivery_type'] = True

            delivery_type_info['DeliveryMoments'] = DeliveryType.create_del_types(
                delivery_type_dict=delivery_type_dict['Days'],
                holiday_del_type=delivery_type_info['holiday_delivery_type'],
            )

            delivery_type_info_list.append(delivery_type_info)
        return DeliveryTypeSet(delivery_type_info_list)

    # get methods
    def get_delivery_type_list(self):
        return self.delivery_types

    def get_delivery_type(self, requested_delivery_type_id: int):
        requested_delivery_type = next(
            (
                delivery_type
                for delivery_type in self.get_delivery_type_list()
                if delivery_type.get_id() == requested_delivery_type_id
            ),
            None,
        )
        return requested_delivery_type


class DeliveryType:
    """
    Attributes:
        id (int): id of delivery type
        calendar_id (int): id of calendar
        calendar (calendar obj or []): obj including holidays and bridge days
        delivery_moments (pandas.DataFrame): dataframe with all delivery days. For every 24 h and indicator True or False.
    """

    # constructor
    def __init__(self, ID, Calendar, holiday_delivery_type, DeliveryMoments):
        self.id = ID
        self.calendar = Calendar
        self.holiday_delivery_type = holiday_delivery_type
        self.delivery_moments = DeliveryMoments

    def get_id(self):
        return self.id

    def get_calendar(self):
        return self.calendar

    def get_holiday_delivery_type(self):
        return self.holiday_delivery_type

    def get_delivery_moments(self):
        return self.delivery_moments

    # read delivery types from xml
    @staticmethod
    def create_del_types(
        delivery_type_node: object = None, delivery_type_dict=None, holiday_del_type=False
    ):
        """
        Args:
            delivery_type_node (object): node in XML tree containing info about delivery types
            delivery_type_dict (dict): dict containing info about delivery types
            holiday_del_type (bool): indicating if there is special delivery types on holidays. e.g. no peak on holidays

        Returns:
            (pd.DataFrame): with delivery types
        """

        def nr2bool(nr):
            """
            sub function used inside create_del_types:
            makes from number a boolean. e.g.
            0 -> False
            1 -> True
            """
            nr = int(nr)
            if nr == 1:
                true_false = True
            elif nr == 0:
                true_false = False
            else:
                true_false = []
            return true_false

        read_from_xml = delivery_type_dict == None
        # read the data from xml
        list_of_delivery_moments = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Hol']
        weekly_delivery_moments = []
        for delivery_moment in list_of_delivery_moments:
            if read_from_xml:
                delivery_type_numbers_text = delivery_type_node.find('Days/' + delivery_moment)
                delivery_type_numbers = None
                if delivery_type_numbers_text is not None:
                    # Note that delivery_type_numbers.text can be None on the <Hol> node
                    delivery_type_numbers = delivery_type_numbers_text.text
            else:
                delivery_type_numbers = delivery_type_dict[delivery_moment]

            if delivery_type_numbers is not None:
                """
                delivery_type_numbers is a list of numbers. Should be converted to True or False.
                We use nr2bool for this, e.g.
                001 - > [False, False, True]
                """
                list_of_del_mom = np.array([nr2bool(i) for i in list(delivery_type_numbers)])[
                    np.newaxis
                ]
                if list_of_del_mom.size > 0:
                    weekly_delivery_moments.append(list_of_del_mom)

        # vertically stack the data
        weekly_delivery_moments = np.vstack(weekly_delivery_moments)

        # Create indexes
        # Rows
        if holiday_del_type is True:
            rows_index = [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
                'Holiday',
            ]
        else:
            rows_index = [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
            ]

        # create column index h_1, h_2, ...
        nr_columns = 24
        h = np.repeat('h', nr_columns)
        i = np.arange(nr_columns).astype(str)
        h_i = np.char.add(h, i)
        return pd.DataFrame(weekly_delivery_moments, index=rows_index, columns=h_i)

    def convert_time_granularity(self, multiplier):
        # method to convert hourly delivery times from hourly to half-hourly delivery times
        # from hour to half hour multiplier = 48 / 24 = 2
        del_types_days = []
        for days in self.delivery_moments.to_numpy():
            day = []
            for hours in days:
                day.append([hours] * multiplier)
            del_types_days.append(np.hstack(day))

        df = pd.DataFrame(np.vstack(del_types_days))

        nr_columns = df.shape[1]
        hh = np.repeat('hh', nr_columns)
        i = np.arange(nr_columns).astype(str)
        hh_i = np.char.add(hh, i)

        df.columns = hh_i
        df.index = self.delivery_moments.index.to_list()
        return df

    def holidays_change(self, date_vector: date, delivery_matrix: np.array):
        """
        Adjusts delivery hours in the delivery matrix, according to holidays.

        Args:
            date_vector (np.array): Vector of dates (daily granularity).
            delivery_matrix (np.array): Matrix of delivery hours for each date in date_vector. Elements in the matrix
                must be of type boolean, with value=True (delivery) or value=False (no delivery). Size: L-by-24, with L
                the length of date_vector.

        Returns:
            (np.array): Delivery matrix with adjusted delivery hours.
        """
        # error checking: delivery_matrix data type
        if delivery_matrix.dtype != bool:
            raise TypeError('delivery_matrix must be of type Boolean.')

        # get calendar
        calendar = self.get_calendar()

        if calendar is not None:
            # get holidays
            holidays = calendar.get_holidays()

            if holidays is not None:
                # find index of common dates
                _, holidays_ind, _ = np.intersect1d(date_vector, holidays, return_indices=True)

                # get holidays delivery
                holidays_delivery = self.get_delivery_moments().loc["Holiday"]

                # adjust delivery type on holiday dates
                delivery_matrix[holidays_ind] = holidays_delivery

        return delivery_matrix


class CalendarSet:
    """
    This is the manager object of the Calendar class. A commodity can have multiple calendars. For example, a holiday calendar
    but also a bridge day calendar.

    Examples:
        >>> from kyoslib_py.settings import CalendarSet
        >>> calendar_set = CalendarSet.from_xml()
        >>> calendar = calendar_set.get_calendar(1)
        >>> calendar.get_name()
        'NL'
    """

    def __init__(self, calendar_info_list: list = None):
        if calendar_info_list is None:
            # to be done raise error
            return

        self.calendars = [Calendar(**calendar_info) for calendar_info in calendar_info_list]

    # from {data_type} methods
    @staticmethod
    def from_xml(xml_path: str = './PrototypeSettings.xml') -> object:
        root = ET.parse(xml_path).getroot()
        calendar_list = root.findall('.//CalendarsInfo/CalendarInfo')

        calendar_info_list = []
        for calender_node in calendar_list:
            # if <CalendarInfo> doesn't exist calendar_node is empty
            if calender_node is not None:
                # if node exist but is actually empty, then calender_node.text is None
                if calender_node.text is not None:
                    calender_info = dict()
                    calender_info['ID'] = int(calender_node.find('ID').text)
                    calender_info['Name'] = calender_node.find('Name').text
                    calender_info['Holiday'] = CalendarSet.set_day_sort(calender_node, 'Holiday')
                    calender_info['BridgeDays'] = CalendarSet.set_day_sort(calender_node, 'Bridge')
                    calendar_info_list.append(calender_info)

        return CalendarSet(calendar_info_list)

    @staticmethod
    def from_json(json_path: str = None):
        # ! to be done ! #
        return

    # get methods
    def get_calendar_list(self):
        return self.calendars

    def get_calendar_days(self, id: int, type: str):
        requested_calendar = self.get_calendar(id)
        if type == 'holidays':
            # should write a method to get the holidays
            calendar_days = requested_calendar.get_holidays()
        elif type == 'bridge_days':
            # should write a method to get the bridge days
            calendar_days = requested_calendar.get_bridge_days()
        else:
            calendar_days = None
        return calendar_days

    def get_calendar(self, requested_calendar_id: int) -> object:
        # returns requested calendar if found otherwise None
        return next(
            (
                calendar
                for calendar in self.get_calendar_list()
                if calendar.get_id() == requested_calendar_id
            ),
            None,
        )

    # Method that reads holidays and bridge days from xml node
    @staticmethod
    def set_day_sort(node, day_sort):
        days = []
        for sub_node in node.findall('.//Days/' + day_sort):
            for element in sub_node.findall('./*'):
                if element.tag == 'Day':
                    d = element.text
                elif element.tag == 'Month':
                    m = element.text
                elif element.tag == 'Year':
                    y = element.text
            days.append(date(int(y), int(m), int(d)))
        day_vector = np.array(days)[np.newaxis].T
        return day_vector


class Calendar:
    """
    Attributes:
        id (int): id of calendar
        name (str): name of calendar
        holidays (list): list of dates of holidays
        bridge_days (list): list of dates of bridge days
    """

    # constructor #
    def __init__(self, ID, Name, Holiday, BridgeDays):
        self.id = ID
        self.name = Name
        self.holidays = Holiday
        self.bridge_days = BridgeDays

    # get methods
    def get_id(self) -> int:
        return self.id

    def get_name(self):
        self.name

    def get_holidays(self) -> list:
        return self.holidays

    def get_bridge_days(self) -> list:
        return self.bridge_days
