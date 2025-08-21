import datetime as dt
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import h5py
import numpy as np
import pandas as pd
from numba import jit

from kyoslib_py.kyos_utils import date_to_mc, matlab_datenum_to_datetime, mc_to_year_month
from kyoslib_py.settings import CommoditySet, Currency, CurrencySet
from kyoslib_py.tradable_product import delivery_period_id_from_name, get_start_end


class SimulationError(Exception):
    """
    Capture errors which occurred using the kyoslib_py.simulation module.

    Attributes:
        message (str): explanation of the error

    Examples:
        >>> raise SimulationError(message='Error reading currencies!')
        >>>
        >>> try:
                simulation_spot_daily = simulation_obj.get_spot(comm_name='TTF')
            except SimulationError as err:
                print(err)
            finally:
                exit_code = 1
                sys.exit(exit_code)
    """

    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


class Simulation:
    """
    The Simulation class allows easy access to a particular KySim simulation job.

    Attributes:
        n_sim (int): Number of simulations
        trading_date (datetime): Datetime object of the trading date on which the simulation job
            was based
        end_date (datetime): Datetime object of the end date of the simulations
        commodities (list): List of all the relevant Commodity objects associated with this
            simulation job
        model_currency (Currency): the KySim model currency
        base_currency (Currency): the base currency of the Kyos Platfom
        spot_folder (str): Path to the folder containing the spot simulation outputs of the
            KySim job
        forward_folder (str): Path to the folder containing the forward simulation outputs of the
            KySim job
        power_spot_granul (int): Integer representing the granularity of spot simulations (daily
            only, hourly, half-hourly or quarter-hourly)

    Examples:
        >>> from kyoslib_py.simulation import Simulation
        >>> simulation_obj = Simulation.from_xml()
        >>> simulation_obj.get_nr_simulations()
        100
        >>> simulation_obj.model_currency.get_name()
        'GBP'
    """

    def __init__(self, kysim_info, currency_set, commodity_set):
        """
        Constructor of the Simulation class.

        Args:
            kysim_info (dict): Dictionary with all the simulations properties expected keys: \n
                - SpotSimFolder (str): Path to the folder containing the spot simulation outputs
                    of the KySim job \n
                - FwdSimFolder (str): Path to the folder containing the forward simulation outputs
                    of the KySim job \n
                - OtherSimFolder (str): Path to the folder containing the other simulation outputs
                    of the KySim job \n
                - TradingDate (datetime): Datetime object of the trading date on which the
                    simulation job was based \n
                - PowerSpotGranularity (int): Integer representing the granularity of spot
                    simulations (daily only, hourly, half-hourly or quarter-hourly) \n
                - EndDate (datetime): Datetime object of the end date of the simulations \n
                - NrSimulations( int): Number of simulations \n
                - ModelCurrency (kyoslib_py.settings.Currency): The KySim model currency \n
                - BaseCurrency (kyoslib_py.settings.Currency): The base currency of the Kyos
                    Platform \n
                - curve_info (dict): With commodity_id, fwd_curve_id, spot_source_id per
                    simulated commodity
            currency_set (CurrencySet): Available currencies. The set should contain at least all
                currencies related to the simulation profile.
            commodity_set (CommoditySet): Available commodities. The set should contain at least
                all simulated commodities.
        """

        # copy the information from the dictionary to the object
        self.spot_folder = kysim_info['SpotSimFolder']
        self.forward_folder = kysim_info['FwdSimFolder']
        self.other_model_folder = kysim_info['OtherSimFolder']

        self.trading_date = kysim_info['TradingDate']
        self.power_spot_granul = kysim_info['PowerSpotGranularity']

        minute = 0
        if self.power_spot_granul == 1:
            minute = 30
        elif self.power_spot_granul == 14:
            minute = 45
        self.end_date = kysim_info['EndDate'].replace(hour=23, minute=minute)

        self.n_sim = kysim_info['NrSimulations']
        # currency objects with model and platform base currency
        self.model_currency = currency_set.get_currency(kysim_info['ModelCurrency'])
        self.base_currency = currency_set.get_currency(kysim_info['BaseCurrency'])

        self.curve_info = kysim_info['curve_info']

        commodities_list = []
        for curve_info in kysim_info['curve_info']:
            commodity = commodity_set.get_commodity(curve_info['commodity_id'])
            # if a commodity in kysiminfo is not in the commodity info it, then commodity =None.
            # We should add these none values to the simulation object
            if commodity is not None:
                commodities_list.append(commodity)

        self.commodities = commodities_list

    # methods to build the object
    @staticmethod
    def from_xml(xml_path='./PrototypeSettings.xml', currency_set=None, commodity_set=None):
        """
        This static method builds de simulation class object from a xml file.

        Args:
            xml_path (str): Path to the xml file with KySimInfo.
            currency_set (CurrencySet): Contains all relevant information relative to currencies
                and currency conversions.
            commodity_set (CommoditySet): Contains all relevant information relative to
                commodity settings.

        Returns:
            (Simulation): kyoslib_py.Simulation object
        """
        if currency_set is None:
            currency_set = CurrencySet.from_csv()

        if commodity_set is None:
            commodity_set = CommoditySet.from_xml(currency_set=currency_set)

        # create empty dictionary to be filled with data
        kysim_info_dict = dict()
        root = ET.parse(xml_path).getroot()
        kysim_info_dict['SpotSimFolder'] = root.find(".//KySimInfo/SpotSimFolder").text
        kysim_info_dict['FwdSimFolder'] = root.find(".//KySimInfo/FwdSimFolder").text
        kysim_info_dict['OtherSimFolder'] = ''

        if root.find(".//KySimInfo/OtherSimFolder") is not None:
            # path to weather/volume simulation
            kysim_info_dict['OtherSimFolder'] = root.find(".//KySimInfo/OtherSimFolder").text

        kysim_info_dict['NrSimulations'] = int(root.find(".//KySimInfo/NrSimulations").text)

        kysim_info_dict['ModelCurrency'] = int(root.find(".//KySimInfo/ModelCurrency").text)
        kysim_info_dict['BaseCurrency'] = int(root.find(".//KySimInfo/BaseCurrency").text)

        kysim_info_dict['TradingDate'] = dt.datetime.strptime(
            root.find(".//KySimInfo/TradingDate").text, '%Y%m%d'
        )

        power_spot_granularity = int(root.find(".//KySimInfo/PowerSpotGranularity").text)
        kysim_info_dict['PowerSpotGranularity'] = power_spot_granularity
        kysim_info_dict['EndDate'] = dt.datetime.strptime(
            root.find(".//KySimInfo/EndDate").text, '%Y%m%d'
        )

        # pick up commodity objects for the simulated commodities
        # get info about the simulated commodities
        curve_info = []
        current_comm = 1  # the commodities are added as Com1, Com2, Hence we start by 1
        find_next_comm = True
        while find_next_comm:
            sim_comm_node = ".//KySimInfo/Commodities"
            comm_id_node = root.find(sim_comm_node + "/Comm" + str(current_comm) + "/Id")
            if comm_id_node is None:
                find_next_comm = False
            else:
                comm_id = int(comm_id_node.text)
                fwd_id_node = root.find(
                    sim_comm_node + "/Comm" + str(current_comm) + "/FwdCurveId"
                )
                spot_source_node = root.find(
                    sim_comm_node + "/Comm" + str(current_comm) + "/SpotSourceId"
                )
                fwd_id = int(fwd_id_node.text)
                spot_source_id = int(spot_source_node.text)

                this_curve_info = dict()
                this_curve_info['commodity_id'] = comm_id
                this_curve_info['fwd_curve_id'] = fwd_id
                this_curve_info['spot_source_id'] = spot_source_id
                curve_info.append(this_curve_info)
            current_comm = current_comm + 1

        kysim_info_dict['curve_info'] = curve_info
        return Simulation(kysim_info_dict, currency_set=currency_set, commodity_set=commodity_set)

    # get methods
    def get_spot_sim_folder_path(self):
        return self.spot_folder

    def get_forward_sim_folder_path(self):
        return self.forward_folder

    def get_other_sim_folder_path(self):
        return self.other_model_folder

    def get_trading_date(self):
        return self.trading_date

    def get_end_date(self):
        return self.end_date

    def get_nr_simulations(self):
        return self.n_sim

    def get_commodity_id_list(self):
        return [commodity.get_id() for commodity in self.commodities]

    def get_currency_id_list(self) -> list:
        return [commodity.get_currency().get_id() for commodity in self.commodities]

    def get_currency(
        self, requested_currency_id: int = None, requested_currency_name: str = None
    ) -> object:
        """
        Args:
            requested_currency_id: currency id of the requested currency.
            requested_currency_name: currency name of the requested currency.

        Returns:
            (kyoslib_py.settings.Currency): kyoslib_py.settings.Currency object.
        """
        if requested_currency_id is not None:
            currency = next(
                (
                    x.get_currency()
                    for x in self.commodities
                    if x.get_currency().get_id() == requested_currency_id
                ),
                None,
            )
        elif requested_currency_name is not None:
            currency = next(
                (
                    x.get_currency()
                    for x in self.commodities
                    if x.get_currency().get_name() == requested_currency_name
                ),
                None,
            )

        return currency

    def get_commodity(
        self, requested_commodity_id: int = None, requested_commodity_name: str = None
    ) -> object:
        """
        Args:
            requested_commodity_id (int): commodity id
            requested_commodity_name (str): commodity name

        Returns:
            kyoslib_py.settings.Commodity
        """
        if requested_commodity_id is not None:
            commodity = next(
                (x for x in self.commodities if x.get_id() == requested_commodity_id), None
            )
        elif requested_commodity_name is not None:
            commodity = next(
                (x for x in self.commodities if x.get_name() == requested_commodity_name), None
            )
        else:
            raise ValueError('Either commodity id or commodity name should be provided')

        return commodity

    def get_model_currency(self):
        return self.model_currency

    def get_base_currency(self):
        return self.base_currency

    def get_power_granularity(self):
        return self.power_spot_granul

    def get_spot(
        self,
        commodity_name: str,
        delivery_period_name: str = 'daily',
        delivery_period_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None,
        currency_name: str = None,
        currency_id: int = None,
        is_cent: bool = None,
        delivery_type_id: int = 1,
        carbon_floor: bool = True,
        price_type: str = None,
    ) -> pd.DataFrame:
        """
        A Simulation class method to import spot price simulations.

        Args:
            commodity_name (str): Name of the commodity for which the spot simulations are to be
                imported, as matching the KYOS platform assigned name.
            delivery_period_name (str, optional): Granularity of the requested spot simulations.
                Defaults to daily simulations.
            delivery_period_id (int, optional): Kyos delivery period id matching the product, e.g.
                day = 3 and hour =2
            start_date (datetime, optional): Start date from which to import simulated spot prices.
            end_date (datetime, optional): End date until which the simulated spot prices are to
                be imported.
            currency_name (str, optional): Name of the currency in which to import the simulations.
                Must be in currency which is simulated. Defaults to model base currency.
            currency_id (int, optional): currency of the currency in which to import the
                simulations. Must be in currency which is simulated. Defaults to model base
                currency.
            is_cent (bool, optional): Are the simulations in cents. Defaults to false.
            delivery_type_id (int, optional): ID number of the delivery type of the required spot
                simulation as defined on the KYOS platform i.e. 1 = baseload, 2 = peakload,
                3 = offpeak.
            carbon_floor (bool, optional): Indicates whether the carbon floor adjusted spot
                simulations should be retrieved if the requested commodity belongs to the
                'carbon' group. Defaults to true.
            price_type (str, optional): "hourlyspot", "fixed", "intraday", "imbalance-take", or "imbalance-feedin"

        Returns:
            (pd.DataFrame): Dataframe containing the individual simulations per column where
                each row represents a unique time period e.g. day or hour. If the granularity is
                below daily, then the first column represents the average across the simulations.

        Examples:
            >>> from kyoslib_py.simulation import Simulation
            >>> simulation_obj = Simulation()
            >>> simulation_spot_daily = simulation_obj.get_spot(
                    commodity_name='NBP',
                    delivery_period_name='daily',
                    start_date=dt.datetime(2020, 1, 1),
                    end_date=dt.datetime(2020, 1, 31),
                    currency_name='EUR',
                    del_type_id=1,
                    carbon_floor=False,
                )
            >>> simulation_spot_daily = simulation_obj.get_spot(commodity_name='TTF')
            >>> implied_forward_curve = simulation_spot_daily.mean(axis =1)
        """

        valuation_date = self.get_trading_date() + timedelta(days=1)
        if start_date is None:
            start_date = valuation_date
        if end_date is None:
            end_date = self.get_end_date()

        start_date = max(start_date, valuation_date)
        end_date = min(end_date, self.get_end_date())

        if start_date > end_date:
            raise SimulationError(message='start_date is later than end_date')

        sim_spot_dir = Path(self.get_spot_sim_folder_path())

        # nr simulations inside the simulation set
        nr_simulations = self.get_nr_simulations()

        # find the relevant commodity
        commodity = self.get_commodity(requested_commodity_name=commodity_name)

        if commodity is None:
            raise SimulationError(
                message="Commodity requested not found. Please check the commodity name supplied"
            )

        group_name = commodity.get_group_name()

        load_currency_name, load_currency_id, currency_id = self.get_load_currency_info(
            commodity, currency_id, currency_name
        )

        if delivery_period_id is None:
            # at this time there is always a delivery_period_name
            delivery_period_id = delivery_period_id_from_name(delivery_period_name)

        if group_name == 'carbon' and carbon_floor:
            commodity_name = commodity_name + '_Adj'

        if delivery_period_id == 3:
            delivery_period_name = 'DailySpot'

            if group_name == 'power':
                delivery_type_name = str()
                if delivery_type_id in [2, 3]:
                    delivery_type_name = Simulation.get_delivery_type_name_from_id(
                        delivery_type_id=delivery_type_id, group_name=group_name
                    )

                if not load_currency_name:
                    delivery_type_name = 'Power' + delivery_type_name
                    spot_file = sim_spot_dir.joinpath(
                        delivery_period_name
                        + delivery_type_name
                        + '_'
                        + commodity_name
                        + "_Spot.mat"
                    )
                else:
                    spot_file = sim_spot_dir.joinpath(
                        delivery_period_name
                        + delivery_type_name
                        + '_'
                        + commodity_name
                        + '_'
                        + load_currency_name
                        + ".mat"
                    )
            else:
                if delivery_type_id != 1:
                    raise SimulationError(
                        message=f'The requested Delivery type id {delivery_type_id} is not '
                        f'defined for this commodity.'
                    )

                if load_currency_name == '':
                    spot_file = sim_spot_dir.joinpath(
                        delivery_period_name + '_' + commodity_name + ".mat"
                    )
                else:
                    spot_file = sim_spot_dir.joinpath(
                        delivery_period_name
                        + '_'
                        + commodity_name
                        + '_'
                        + load_currency_name
                        + ".mat"
                    )

            with h5py.File(spot_file, 'r') as f:
                key_list = [key for key in f.keys()]
                key = [key for key in key_list if key != 'dummy'][0]
                raw_data = f[key][()].T

            idx = pd.to_datetime(raw_data[:, 0] - 719529, unit='D')
            spot_prices_df = pd.DataFrame(raw_data[:, 1:]).set_index(idx)

        elif delivery_period_id in [2, 1, 14]:
            if group_name != 'power':
                raise SimulationError(
                    message='There are no hourly simulations for commodity ' + commodity_name + '!'
                )

            if delivery_type_id != 1:
                raise SimulationError(
                    message='Hourly simulations only available for baseload power. '
                    'Only baseload power simulations will be returned'
                )

            chosen_years = range(start_date.year, end_date.year + 1)

            num_cols = nr_simulations + 3
            spot = np.empty((0, num_cols), np.float32)

            # use the granularity to determine the start of the filename containing the simulations
            delivery_period_dict = {
                2: 'Hourly',
                1: 'HalfHourly',
                14: 'QuarterHourly',
            }

            delivery_period_name = delivery_period_dict[delivery_period_id]

            price_type_prefixes = {
                'intraday': 'Intraday_',
                'imbalance-feedin': 'ImbalanceF_',
                'imbalance-take': 'ImbalanceT_',
            }

            price_type = price_type_prefixes.get(price_type, '')
            if price_type:
                db_variable_name = 'SubHourlySpotPower'  # variable name for ID or IB
            else:
                delivery_period_name += 'SpotPower'
                db_variable_name = delivery_period_name  # variable name for hourlyspot files

            for year in chosen_years:
                spot_file = sim_spot_dir.joinpath(
                    'KyPlant',
                    commodity_name + '_Spot',
                    price_type + delivery_period_name + '_' + str(year) + '.mat',
                )
                try:
                    with h5py.File(spot_file, 'r') as f:
                        raw_data = f[db_variable_name][()].T
                        spot = np.append(spot, raw_data, axis=0)
                except:
                    continue

            # Determine how many time units fit in an hour (e.g. 2 half-hours fit in 1 hour)
            units_in_hours = 1
            if delivery_period_id == 1:
                units_in_hours = 2
            elif delivery_period_id == 14:
                units_in_hours = 4

            # Create hourly datetime index from first two columns
            idx = pd.to_datetime(spot[:, 0] - 719529, unit="D") + pd.to_timedelta(
                (spot[:, 1] - 1) / units_in_hours, unit="h"
            )
            # Third column is the mean of simulations. Create data frame from
            # remaining columns and use hourly datetime as index.
            spot_prices_df = pd.DataFrame(spot[:, 3:]).set_index(idx)

        else:
            raise SimulationError(
                message='Granularity ' + str(delivery_period_id) + ' is not supported!'
            )

        if spot_prices_df.empty:
            raise SimulationError(
                message=f'{delivery_period_name} Spot simulations could not be loaded. '
                f'Please check that these simulations were generated by KySim'
            )

        spot_prices_df = spot_prices_df.loc[start_date:end_date]
        # drop NaNs
        spot_prices_df = spot_prices_df.dropna()

        # convert between cents and full currency units
        spot_prices_df = self.adjust_sims_is_cent(spot_prices_df, is_cent, commodity)

        # If simulations are requested in a different currency than the model currency or than
        # commodity currency, the simulations are converted
        if load_currency_id != currency_id:
            spot_prices_df = self.convert_fx(
                simulation_prices=spot_prices_df,
                delivery_period_id=delivery_period_id,
                from_currency_id=load_currency_id,
                to_currency_id=currency_id,
            )

        # rename column to include sim_1,sim_2,...
        spot_prices_df.columns = self.create_sim_i_colum()

        return spot_prices_df

    # method to import forward product (with fixed delivery) simulations
    def get_fwd_product(
        self,
        commodity_name: str,
        fwd_year: int,
        fwd_month: int,
        start_date: datetime = None,
        end_date: datetime = None,
        delivery_period_id: int = 5,
        currency_name: str = None,
        currency_id: int = None,
        is_cent: bool = None,
        delivery_type_id: int = 1,
        carbon_floor: bool = True,
    ) -> pd.DataFrame:
        """
        A Simulation class method to import forward prices simulations (monthly delivery only,
        daily granularity).

        Args:
            commodity_name (str): Name of the commodity for which the forward simulations are to
                be imported, as matching the KYOS platform assigned name.
            fwd_year (int): Year in which the simulated monthly forward contract delivers
            fwd_month (int): Month in which the simulated monthly forward contract delivers
            start_date (datetime, optional): Start date from which to begin importing the forward
                product simulations.
            end_date (datetime, optional): End date until which the simulated spot prices are to
                be imported.
            delivery_period_id (int, optional): Kyos delivery period id matching the product,
                e.g. quarter = 6
            currency_name (str, optional): Name of the currency in which to import the simulations.
                Must be either the name of the model base currency or the commodity currency.
                Defaults to model base currency if not specified.
            currency_id (int): ID of the currency in which to import the simulations
            is_cent (bool): If true, the currency is quoted in cents. False otherwise.
            delivery_type_id (int, optional): ID number of the delivery type of the required
                forward simulation as defined on the KYOS platform i.e. 1 = baseload,
                2 = peakload, 3 = offpeak.
            carbon_floor (bool, optional): Indicates whether the carbon floor adjusted spot
                simulations should be retrieved if the requested commodity belongs to the
                'carbon' group.

        Returns:
            (pd.DataFrame): Dataframe containing the individual simulations per column where
                each row represents a unique day.

        Examples:
            >>> from kyoslib_py.simulation import Simulation
            >>> simulation_obj = Simulation()
            >>> monthly_forward_prices = simulation_obj.get_fwd_product(
                    commodity_name='TTF',
                    fwd_year=2020,
                    fwd_month=11,
                    start_date=dt.datetime(2020, 1, 1),
                    end_date=dt.datetime(2020, 10, 31),
                    currency_name='EUR',
                    del_type_id=1,
                    carbon_floor=False,
                )
            >>> monthly_forward_prices = simulation_obj.get_fwd_product(
                    commodity_name='TTF',
                    fwd_year=2020,
                    fwd_month=11,
                )
        """

        valuation_date = self.get_trading_date() + timedelta(days=1)
        if start_date is None:
            start_date = valuation_date
        if end_date is None:
            end_date = self.get_end_date()

        start_date = max(start_date, valuation_date)
        end_date = min(end_date, self.get_end_date())

        if start_date > end_date:
            raise SimulationError(message='start_date is later than end_date')

        commodity = self.get_commodity(requested_commodity_name=commodity_name)

        if commodity is None:
            raise SimulationError(
                message="Commodity requested not found. Please check the commodity name supplied"
            )

        simulated_trading_dates = pd.date_range(start_date, end_date, freq='d')
        sim_spot_dir = Path(self.get_spot_sim_folder_path())

        group_name = commodity.get_group_name()
        if group_name == 'carbon' and carbon_floor:
            commodity_name = commodity_name + '_Adj'

        load_currency_name, load_currency_id, currency_id = self.get_load_currency_info(
            commodity, currency_id, currency_name
        )

        nr_simulations = self.get_nr_simulations()
        nr_simulated_days = simulated_trading_dates.shape[0]
        delivery_type_name = Simulation.get_delivery_type_name_from_id(
            delivery_type_id, group_name
        )

        if delivery_period_id in [11, 12, 15]:
            raise SimulationError(
                message='Importing Week/Weekend products has not been implemented yet for fixed '
                'delivery product!'
            )
        elif delivery_period_id == 4 or (
            delivery_period_id == 5
            and fwd_year == valuation_date.year
            and fwd_month == valuation_date.month
            and (group_name.lower() == 'power' or group_name.lower() == 'gas')
        ):
            if delivery_type_name == '':
                file_path = sim_spot_dir.joinpath("BOM_" + commodity_name + ".mat")
            else:
                file_path = sim_spot_dir.joinpath(
                    "BOM_" + commodity_name + '_' + delivery_type_name + ".mat"
                )

            try:
                with h5py.File(file_path, 'r') as f:
                    bom_prices = f['BOMPrices_i'][()].T
            except OSError:
                raise SimulationError(
                    message=f'Simulations for the requested delivery year:{fwd_year} and month: '
                    f'{fwd_month} '
                    f'not found. Please check the inputted year and month.'
                )
            """
            BOMPrices:    ( Time Periods x (Nr. Simulations + 3))
                              Col.1 serial MATLAB dates
                              Col.2 start delivery date
                              Col.3 end delivery date
                              Col.4 - End: Simulated BOM prices
            """
            trading_date = pd.to_datetime(bom_prices[:, 0] - 719529, unit='D')
            index = (simulated_trading_dates[0] <= trading_date) & (
                trading_date <= simulated_trading_dates[-1]
            )
            fwd_sims = bom_prices[index, 3:]

        else:
            product_start_mc = (fwd_year - 2000) * 12 + fwd_month
            if delivery_period_id == 5:  # month
                product_end_mc = product_start_mc
            elif delivery_period_id == 6:  # quarter
                product_end_mc = product_start_mc + 2
            elif delivery_period_id == 7:  # season
                product_end_mc = product_start_mc + 5
            elif delivery_period_id == 8:  # calendar year
                product_end_mc = product_start_mc + 11
            elif delivery_period_id == 9:  # gas year
                product_end_mc = product_start_mc + 11
            else:
                raise SimulationError(
                    message=f'Simulation product with delivery period = {delivery_type_id} '
                    f'cannot be loaded.'
                )

            # in python, the last np.arange() doesn't include the last element. Hence, the + 1
            month_codes = np.arange(product_start_mc, product_end_mc + 1)

            # Since it's a fixed delivery product, the start and end date is the same for all
            # days. This is different from a rolling product.
            start_delivery_month_codes = np.array([product_start_mc] * nr_simulated_days)
            end_delivery_month_codes = np.array([product_end_mc] * nr_simulated_days)

            # #### Calculate tradable product #####################################################
            month_sims = self.load_sims_for_all_months(
                month_codes,
                simulated_trading_dates,
                commodity_name,
                delivery_type_name,
                load_currency_name,
            )
            fwd_sims = self.calculate_tradable_product(
                commodity,
                start_delivery_month_codes,
                end_delivery_month_codes,
                month_codes,
                month_sims,
            )
            #######################################################################################

        # NaNs can happen if we have non-base delivery type, e.g.
        #   power peak does not deliver in the weekend, so NaN's are
        #   reported as prices of products which do not contain peak hours, this
        #   can happen with BOM.
        not_nan = ~np.isnan(fwd_sims[:, 0])
        mask = np.ix_(not_nan, np.array([True] * nr_simulations))
        fwd_sims = fwd_sims[mask]

        # create output dataframe and give trading dates as index and names to the columns
        fwd_prices = pd.DataFrame(fwd_sims)
        fwd_prices.index = simulated_trading_dates[not_nan]

        # convert between cents and full currency units
        fwd_prices = self.adjust_sims_is_cent(fwd_prices, is_cent, commodity)

        # if simulations are requested in a different currency than the model currency or than
        # commodity currency, the simulations are converted
        if load_currency_id != currency_id:
            # delivery_period_name='daily', since we have daily prices
            fwd_prices = self.convert_fx(
                simulation_prices=fwd_prices,
                delivery_period_name='daily',
                from_currency_id=load_currency_id,
                to_currency_id=currency_id,
            )

        # create columns: [sim_1,sim_2,...]
        fwd_prices.columns = self.create_sim_i_colum()
        ###########################################################################################

        fwd_prices = fwd_prices.loc[start_date:end_date]
        return fwd_prices

    # method to import forward product (with rolling delivery) simulations
    def get_fwd_product_roll(
        self,
        commodity_name: str,
        delivery_period_id,
        maturity,
        delivery_type_id=1,
        is_cent=None,
        currency_name=None,
        currency_id=None,
        start_date=None,
        end_date=None,
        carbon_floor=False,
    ) -> pd.DataFrame:
        """
        A Simulation class method to import forward rolling prices simulations.

        Args:
            commodity_name (str): Name of the commodity for which the forward simulations are to
                be imported,vas matching the KYOS platform assigned name.
            delivery_period_id (int): delivery period id matching the product, e.g. quarter = 6
            maturity (int): how many periods ahead is the product, e.g. two quarters ahead.
            delivery_type_id (int, optional): ID number of the delivery type of the required
                forward simulation as defined on the KYOS platform i.e. 1 = baseload,
                2 = peakload, 3 = offpeak.
            is_cent (bool, optional): true if you want the simulations in cent instead of whole
                currency unit
            currency_name (str, optional): Name of the currency in which to import the simulations.
                Must be either the name of the model base currency or the commodity currency.
                Defaults to model base currency if not specified.
            currency_id : Id of the currency in which to import the simulations.
                Defaults to model base currency if not specified.
            start_date (datetime, optional): Start date from which to begin importing the forward
                product simulations.
            end_date (datetime, optional): latest simulated trading date.
            carbon_floor (bool, optional): Indicates whether the carbon floor adjusted spot
                simulations should be retrieved if the requested commodity belongs to the
                'carbon' group. Default is False.

        Returns:
            (pd.DataFrame): Dataframe containing the individual simulations where each row
                represents a unique day. \n
                index : simulated trading days \n
                column 1: start delivery date \n
                column 2: end delivery date \n
                column 3->end: simulations
        """
        valuation_date = self.get_trading_date() + timedelta(days=1)
        if start_date is None:
            start_date = valuation_date
        if end_date is None:
            end_date = self.get_end_date()

        start_date = max(start_date, valuation_date)
        end_date = min(end_date, self.get_end_date())

        if start_date > end_date:
            raise SimulationError(message='start_date is later than end_date')

        commodity = self.get_commodity(requested_commodity_name=commodity_name)
        if commodity is None:
            raise SimulationError(
                message="Commodity requested not found. Please check the commodity name supplied"
            )

        load_currency_name, load_currency_id, currency_id = self.get_load_currency_info(
            commodity, currency_id, currency_name
        )

        simulated_trading_dates = pd.date_range(start_date, end_date, freq='d')
        first_requested_simulated_day = simulated_trading_dates[0]
        last_requested_simulated_day = simulated_trading_dates[-1]

        sim_spot_dir = Path(self.get_spot_sim_folder_path())
        group_name = commodity.get_group_name()

        if group_name == 'carbon' and carbon_floor:
            commodity_name = commodity_name + '_Adj'

        delivery_type_name = Simulation.get_delivery_type_name_from_id(
            delivery_type_id, group_name
        )

        nr_simulations = self.get_nr_simulations()
        nr_simulated_days = simulated_trading_dates.shape[0]

        if delivery_period_id in [11, 12, 15]:
            # import simulations for BOW, weeks and weekends
            if delivery_type_id != 1:
                raise SimulationError(
                    message='KySim simulates only baseload BOW/week/weekend products!'
                )

            if delivery_period_id == 11:
                product_name = 'WK'
            elif delivery_period_id == 12:
                product_name = 'WKND'
            elif delivery_period_id == 15:
                product_name = 'BOW'

            if maturity > 0:
                file_path = sim_spot_dir.joinpath(
                    product_name + str(maturity) + '_' + commodity_name + ".mat"
                )
            else:
                file_path = sim_spot_dir.joinpath(product_name + '_' + commodity_name + ".mat")

            try:
                with h5py.File(file_path, 'r') as f:
                    key_list = [key for key in f.keys()]
                    key = [key for key in key_list if key != 'dummy'][
                        0
                    ]  # can we find the key easier?
                    prices = f[key][()].T
            except OSError:
                raise SimulationError(
                    message='The requested simulated product requested cannot be made. '
                    'Please adjust the start and end_date'
                )

            trading_date = pd.to_datetime(prices[:, 0] - 719529, unit='D')
            index = (first_requested_simulated_day <= trading_date) & (
                trading_date <= last_requested_simulated_day
            )

            start_delivery_date = np.array(
                pd.to_datetime(prices[index, 1] - 719529, unit='D'), dtype=object
            )
            end_delivery_date = np.array(
                pd.to_datetime(prices[index, 2] - 719529, unit='D'), dtype=object
            )
            fwd_sims = prices[index, 3:]

        elif delivery_period_id == 4 or (
            delivery_period_id == 5
            and maturity == 0
            and (group_name.lower() == 'power' or group_name.lower() == 'gas')
        ):
            if delivery_type_name == '':
                file_path = sim_spot_dir.joinpath("BOM_" + commodity_name + ".mat")
            else:
                file_path = sim_spot_dir.joinpath(
                    "BOM_" + commodity_name + '_' + delivery_type_name + ".mat"
                )

            try:
                with h5py.File(file_path, 'r') as f:
                    bom_prices = f['BOMPrices_i'][()].T
            except OSError:
                raise SimulationError(
                    message='Bom Simulations cannot be found. Please check the inputted year and '
                    'month.'
                )
            """
            BOMPrices:    ( Time Periods x (Nr. Simulations + 3))
                              Col.1 serial MATLAB dates
                              Col.2 start delivery date
                              Col.3 end delivery date
                              Col.4 - End: Simulated BOM prices
            """
            trading_date = pd.to_datetime(bom_prices[:, 0] - 719529, unit='D')
            index = (first_requested_simulated_day <= trading_date) & (
                trading_date <= last_requested_simulated_day
            )

            start_delivery_date = np.array(
                pd.to_datetime(bom_prices[index, 1] - 719529, unit='D'), dtype=object
            )
            end_delivery_date = np.array(
                pd.to_datetime(bom_prices[index, 2] - 719529, unit='D'), dtype=object
            )
            fwd_sims = bom_prices[index, 3:]

        else:
            # either the product simulations can be loaded from a matfile or will be created
            create_product_from_sim = True

            if delivery_period_id in [5, 6, 7, 8] and (maturity in [1, 2]):
                # check if rolling product is generated by KySim
                # note that only month and year for maturity 1,2 are stored.
                sim_fwd_dir = Path(self.get_forward_sim_folder_path()).joinpath('OutputRolling')

                if delivery_period_id == 5:
                    product_indicator = 'M'
                elif delivery_period_id == 6:
                    product_indicator = 'Q'
                elif delivery_period_id == 7:
                    product_indicator = 'S'
                elif delivery_period_id == 8:
                    product_indicator = 'Y'

                input_file_path = sim_fwd_dir.joinpath(
                    commodity_name
                    + '_'
                    + delivery_type_name
                    + "_"
                    + product_indicator
                    + '0'
                    + str(maturity)
                    + ".mat"
                )
                if input_file_path.exists():
                    # rolling product will be read from matfile
                    create_product_from_sim = False
                    f = h5py.File(input_file_path, 'r')
                    daily_forward_mat = f['Forward'][()].T

                    simulated_trading_dates = np.array(
                        matlab_datenum_to_datetime(daily_forward_mat[:, 0])
                    )
                    start_delivery_date = np.array(
                        matlab_datenum_to_datetime(daily_forward_mat[:, 1])
                    )
                    end_delivery_date = np.array(
                        matlab_datenum_to_datetime(daily_forward_mat[:, 2])
                    )

                    fwd_sims = daily_forward_mat[:, 3:]

            if create_product_from_sim:
                # we need to calculate the products from the monthly simulations
                start_delivery_date = np.zeros((nr_simulated_days), dtype=object)
                end_delivery_date = np.zeros((nr_simulated_days), dtype=object)

                for i in range(nr_simulated_days):
                    # To do: we should take into account the trading calendar. However, where do
                    # we get this? A trading calendar is not commodity specific but exchange
                    # specific.
                    start, end = get_start_end(
                        simulated_trading_dates[i], [delivery_period_id], [maturity]
                    )
                    start_delivery_date[i] = start[0]
                    end_delivery_date[i] = end[0]

                min_delivery_date, max_delivery_date = min(start_delivery_date), max(
                    end_delivery_date
                )
                min_delivery_mc, max_delivery_mc = date_to_mc(min_delivery_date), date_to_mc(
                    max_delivery_date
                )

                month_codes = np.arange(min_delivery_mc, max_delivery_mc + 1)

                start_delivery_month_codes = np.array(
                    [date_to_mc(date) for date in start_delivery_date]
                )
                end_delivery_month_codes = np.array(
                    [date_to_mc(date) for date in end_delivery_date]
                )

                # #### Calculate tradable product #################################################
                month_sims = self.load_sims_for_all_months(
                    month_codes,
                    simulated_trading_dates,
                    commodity_name,
                    delivery_type_name,
                    load_currency_name,
                )

                fwd_sims = self.calculate_tradable_product(
                    commodity,
                    start_delivery_month_codes,
                    end_delivery_month_codes,
                    month_codes,
                    month_sims,
                )
                ###################################################################################
        # NaNs can happen if we have non-base delivery type, e.g.
        #   power peak does not deliver in the weekend, so NaN's are
        #   reported as prices of products which do not contain peak hours, this
        #   can happen with BOM.
        not_nan = ~np.isnan(fwd_sims[:, 0])
        mask = np.ix_(not_nan, np.array([True] * nr_simulations))
        fwd_sims = fwd_sims[mask]

        # create output dataframe and give trading dates as index and names to the columns
        fwd_prices = pd.DataFrame(fwd_sims)
        fwd_prices.index = simulated_trading_dates[not_nan]

        # convert between cents and full currency units
        fwd_prices = self.adjust_sims_is_cent(fwd_prices, is_cent, commodity)

        # If simulations are requested in a different currency than the model currency or than
        # commodity currency, the simulations are converted
        if load_currency_id != currency_id:
            # delivery_period_name='daily', since we have daily prices
            fwd_prices = self.convert_fx(
                simulation_prices=fwd_prices,
                delivery_period_name='daily',
                from_currency_id=load_currency_id,
                to_currency_id=currency_id,
            )

        # add start delivery and end delivery
        fwd_prices = pd.concat(
            [
                pd.DataFrame(
                    np.array([start_delivery_date[not_nan], end_delivery_date[not_nan]]).T,
                    index=fwd_prices.index,
                ),
                fwd_prices,
            ],
            axis=1,
        )

        # create columns: [start_delivery, end_delivery, sim_1,sim_2,...]
        fwd_prices.columns = np.append(
            ['start_delivery', 'end_delivery'], self.create_sim_i_colum()
        )
        ###########################################################################################
        fwd_prices = fwd_prices.loc[start_date:end_date]

        return fwd_prices

    def get_fwd_curve(
        self,
        commodity_name: str,
        delivery_period_name: str,
        start_date: datetime = None,
        end_date: datetime = None,
        del_type_id: int = 1,
        dst: bool = True,
    ) -> pd.DataFrame:
        """
        A Simulation class method to import forward curves used in the simulations.

        Args:
            commodity_name (str): Name of the commodity for which the forward curve it to be
                imported, as matching that given in the XML settings file.
            delivery_period_name (str): Curve granularity requested. half-hourly, hourly, daily
                and monthly supported.
            start_date (datetime, optional): Start date from which to begin the imported forward
                curve.
            end_date (datetime, optional): Date at which the imported forward curve will end
                (inclusive of this date).
            del_type_id (int, optional): ID number of the delivery type of the required forward
                curve as defined on the KYOS platform i.e. 1 = baseload, 2 = peakload, 3 = offpeak.
                Only available for monthly curves.
            dst (bool, optional): Returns an hourly curve with Daylight Savings Time switches
                included (with missing hour and/or averaged double hour) if True, otherwise
                non-DST curve is outputted. Defaults to true; only meaningful with hourly (power)
                curves.

        Returns:
            (pd.DataFrame): Dataframe containing the forward curve prices, where each row
                represents a new time period corresponding to the granularity supplied.

        Note:
            Forward curve are always imported in the currency of the commodity (which may be
            different from the model currency).

        Examples:
            >>> from kyoslib_py.simulation import Simulation
            >>> simulation_obj = Simulation()
            >>> hourly_fwd_curve = simulation_obj.get_fwd_curve(
                commodity_name='UK Power',
                delivery_period_name='hourly',
                start_date=None,
                end_date=None,
                del_type_id=1,
                dst=True,
            )
            >>> daily_fwd_curve = simulation_obj.get_fwd_curve(
                commodity_name='TTF',
                delivery_period_name='daily'
            )
        """

        # Input validation
        if start_date is None:
            start_date = self.trading_date
        if end_date is None:
            end_date = self.end_date

        # Ensure the gran inputs are case-insensitive
        delivery_period_name = str.casefold(delivery_period_name)

        # Get forward curves directory
        subfolder_fwd_curve_path = Path(self.spot_folder[:-6] + 'ForwardCurves')

        trad_year = str(self.trading_date.year)
        trad_month = self.trading_date.month
        trad_day = self.trading_date.day
        if trad_month < 10:
            trad_month = '0' + str(trad_month)
        else:
            trad_month = str(trad_month)
        if trad_day < 10:
            trad_day = '0' + str(trad_day)
        else:
            trad_day = str(trad_day)

        trading_date = trad_year + trad_month + trad_day

        # Find forward curve id
        selected_commodity = next((x for x in self.commodities if x.name == commodity_name), None)
        if selected_commodity is None:
            raise SimulationError(
                message='Commodity not found; please check the spelling and note that commodity '
                'names are case sensitive'
            )
        commodity_id = selected_commodity.id
        commodity_group = selected_commodity.group_name
        selected_commodity = next(
            (x for x in self.curve_info if x['commodity_id'] == commodity_id), None
        )
        fwd_curve_id = selected_commodity['fwd_curve_id']
        filename_end = '_' + str(fwd_curve_id) + '_' + trading_date

        if delivery_period_name == 'hourly' and commodity_group != 'power':
            raise SimulationError(
                message='Input delivery_period supplied not available for this commodity type.'
            )

        if delivery_period_name != 'monthly' and del_type_id != 1:
            raise SimulationError(
                message='Delivery type requested not available for this delivery_period'
            )

        if del_type_id != 1 and commodity_group != 'power':
            raise SimulationError(
                message='Delivery type specified not available for this commodity type. '
                'Curve with standard (baseload) delivery will be returned'
            )

        if delivery_period_name == 'quarter-hour' and dst is True:
            curve_file_name = 'ForwardCurveQuarterHourlyDST' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(
                    fwd_curve_path, sep=';', header=None, names=['date', 'quarter-hour', 'value']
                )
            except:
                raise SimulationError(
                    message='Curve requested not found. Please check the path and trading date to '
                    'confirm the requested curve exists.'
                )

            forward_curve_csv.index.name = 'date'
            melted_curve = forward_curve_csv.reset_index().melt(
                id_vars='date', var_name='quarter_hour', value_name='value'
            )
            melted_curve = melted_curve.set_index("date")
            melted_curve['datetime'] = pd.to_datetime(melted_curve.index) + pd.to_timedelta(
                melted_curve["quarter_hour"] * 15, unit='m'
            )
            melted_curve = melted_curve.set_index('datetime')['value'].sort_index()
            forward_curve_df = pd.DataFrame(melted_curve.loc[start_date:end_date])

        if delivery_period_name == 'quarter-hour' and dst is False:
            curve_file_name = 'ForwardCurveQuarterHourlyNoDST' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(fwd_curve_path, sep=';', header=None)
            except:
                raise SimulationError(
                    message="Curve requested not found. Please check the path and trading date "
                    "to confirm the requested curve exists."
                )

            curve_array = forward_curve_csv.to_numpy()
            first_date = dt.datetime.strptime(curve_array[0, 0], "%Y-%m-%d")
            last_date = dt.datetime.strptime(curve_array[-1, 0], "%Y-%m-%d")
            # Creating timedeltas with a step size of 15 minutes
            date_list = [
                first_date + dt.timedelta(minutes=15 * x)
                for x in range(0, ((last_date - first_date).days * 24 + 24) * 4)
            ]
            date_list = pd.DataFrame(date_list)
            quarter_hourly_prices = pd.DataFrame(forward_curve_csv[2])
            data_for_concat = [date_list, quarter_hourly_prices]
            forward_curve_csv = pd.concat(
                data_for_concat, axis=1
            )  # Concatenate date_list and quarter_hour_prices
            forward_curve_csv.columns = ['date', 'values']
            forward_curve_csv.set_index(forward_curve_csv['date'], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])

        if delivery_period_name == 'halfhourly' and dst is True:
            curve_file_name = 'ForwardCurveHalfHourly' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(fwd_curve_path, sep=';', header=None, index_col=0)
            except:
                raise SimulationError(
                    message='Curve requested not found. Please check the path and trading date to '
                    'confirm the requested curve exists.'
                )

            forward_curve_csv.index.name = 'date'
            melted_curve = forward_curve_csv.reset_index().melt(
                id_vars='date', var_name='half_hour', value_name='value'
            )
            melted_curve = melted_curve.set_index("date")
            melted_curve['datetime'] = pd.to_datetime(melted_curve.index) + pd.to_timedelta(
                melted_curve["half_hour"] * 30, unit='m'
            )
            melted_curve = melted_curve.set_index('datetime')['value'].sort_index()

            forward_curve_df = pd.DataFrame(melted_curve.loc[start_date:end_date])

        if delivery_period_name == 'halfhourly' and dst is False:
            curve_file_name = 'ForwardCurveHalfHourlyNoDST' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(fwd_curve_path, sep=';', header=None)
            except:
                raise SimulationError(
                    message="Curve requested not found. Please check the path and trading date "
                    "to confirm the requested curve exists."
                )
            curve_array = forward_curve_csv.to_numpy()
            first_date = dt.datetime.strptime(curve_array[0, 0], "%Y-%m-%d")
            last_date = dt.datetime.strptime(curve_array[-1, 0], "%Y-%m-%d")
            # Creating timedeltas with a stepsize of 30 minutes
            date_list = [
                first_date + dt.timedelta(minutes=30 * x)
                for x in range(0, ((last_date - first_date).days * 24 + 24) * 2)
            ]
            date_list = pd.DataFrame(date_list)
            half_hourly_prices = pd.DataFrame(forward_curve_csv[2])
            data_for_concat = [date_list, half_hourly_prices]
            forward_curve_csv = pd.concat(
                data_for_concat, axis=1
            )  # Concatenate date_list and hourly_prices
            forward_curve_csv.columns = ['date', 'values']
            forward_curve_csv.set_index(forward_curve_csv['date'], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])

        if delivery_period_name == 'hourly' and dst is True:
            curve_file_name = 'ForwardCurveHourlyDST' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(
                    fwd_curve_path, sep=';', header=None, names=['date', 'hour', 'value']
                )
            except:
                raise SimulationError(
                    message='Curve requested not found. Please check the path and trading date '
                    'to confirm the requested curve exists.'
                )
            hours_delta = pd.to_timedelta(forward_curve_csv.iloc[:, 1].values, unit='h')
            forward_curve_csv.iloc[:, 0] = pd.to_datetime(forward_curve_csv.iloc[:, 0])
            forward_curve_csv.iloc[:, 0] = forward_curve_csv.iloc[:, 0] + hours_delta
            forward_curve_csv.set_index(forward_curve_csv['date'], inplace=True)
            forward_curve_csv.drop(columns=['date', 'hour'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])

        if delivery_period_name == 'hourly' and dst is False:
            curve_file_name = 'ForwardCurveHourly' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(fwd_curve_path, sep=';', header=None)
            except:
                raise SimulationError(
                    message="Curve requested not found. Please check the path and trading date "
                    "to confirm the requested curve exists."
                )
            curve_array = forward_curve_csv.to_numpy()
            hourly_prices = np.reshape(
                curve_array[:, 1:], [24 * forward_curve_csv.shape[0], 1]
            )  # Adjust input format
            first_date = dt.datetime.strptime(curve_array[0, 0], "%Y-%m-%d")
            last_date = dt.datetime.strptime(curve_array[-1, 0], "%Y-%m-%d")
            date_list = [
                first_date + dt.timedelta(hours=x)
                for x in range(0, (last_date - first_date).days * 24 + 24)
            ]
            date_list = pd.DataFrame(date_list)
            hourly_prices = pd.DataFrame(hourly_prices)
            data_for_concat = [date_list, hourly_prices]
            forward_curve_csv = pd.concat(
                data_for_concat, axis=1
            )  # Concatenate date_list and hourly_prices
            forward_curve_csv.columns = ['date', 'values']
            forward_curve_csv.set_index(forward_curve_csv['date'], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])
        if delivery_period_name == 'daily':
            curve_file_name = 'ForwardCurveDaily' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(
                    fwd_curve_path, sep=';', header=None, names=['date', 'value']
                )
            except:
                SimulationError(
                    message="Curve requested not found. Please check the path and trading date "
                    "to confirm the requested curve exists."
                )
            forward_curve_csv.iloc[:, 0] = pd.to_datetime(forward_curve_csv.iloc[:, 0])
            forward_curve_csv.set_index(forward_curve_csv.iloc[:, 0], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])
        if delivery_period_name == 'daily':
            curve_file_name = 'ForwardCurveDaily' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            try:
                forward_curve_csv = pd.read_csv(
                    fwd_curve_path, sep=';', header=None, names=['date', 'value']
                )
            except:
                SimulationError(
                    message="Curve requested not found. Please check the path and trading date "
                    "to confirm the requested curve exists."
                )
            forward_curve_csv.iloc[:, 0] = pd.to_datetime(forward_curve_csv.iloc[:, 0])
            forward_curve_csv.set_index(forward_curve_csv.iloc[:, 0], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])
        if delivery_period_name == 'monthly':
            curve_file_name = 'ForwardCurveMonthly' + filename_end + '.csv'
            fwd_curve_path = subfolder_fwd_curve_path.joinpath(curve_file_name)
            if commodity_group == 'power':
                try:
                    forward_curve_csv = pd.read_csv(
                        fwd_curve_path, sep=';', header=None, names=['date', '1', '2', '3']
                    )
                except:
                    SimulationError(
                        message="Curve requested not found. Please check the path and trading "
                        "date to confirm the requested curve exists."
                    )
                all_del_types = np.array([1, 2, 3])
                not_del_types = all_del_types[del_type_id != all_del_types]
                forward_curve_csv.drop(
                    columns=[str(not_del_types[0]), str(not_del_types[1])], inplace=True
                )
            else:
                try:
                    forward_curve_csv = pd.read_csv(
                        fwd_curve_path, sep=';', header=None, names=['date', 'value']
                    )
                except:
                    SimulationError(
                        message="Curve requested not found. Please check the path and trading "
                        "date to confirm the requested curve exists."
                    )
            forward_curve_csv.iloc[:, 0] = pd.to_datetime(forward_curve_csv.iloc[:, 0])
            forward_curve_csv.set_index(forward_curve_csv.iloc[:, 0], inplace=True)
            forward_curve_csv.drop(columns=['date'], inplace=True)
            forward_curve_df = pd.DataFrame(forward_curve_csv.loc[start_date:end_date])
        return forward_curve_df

    def get_fx(
        self,
        term_currency_id: int,
        base_currency_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> pd.DataFrame:
        """
        Get the daily FX simulated prices in a given period. The FX base currency is by default
        the KySim model currency, but can be adjusted via the base_currency_id argument.

        Args:
            term_currency_id: The currency id to which you want to convert the prices.
            base_currency_id (optional, int): id of the base currency. By default, this is the
                model currency id
            start_date (datetime, optional): Start date from which to begin importing the fx
                simulations.
            end_date (datetime, optional): End date until which the simulated fx prices are to
                be imported.

        Returns:
            (pd.DataFrame): Dataframe containing the daily simulated prices, datetime as index and
                the fx per simulation in the columns.

        Examples:
                   >>> from kyoslib_py.simulation import Simulation
                   >>> simulation_obj = Simulation()
                   >>> fx_sims = simulation_set.get_fx(2)
        """
        model_currency = self.get_model_currency()
        model_currency_id = model_currency.get_id()
        if base_currency_id is None:
            base_currency_id = model_currency_id

        # not all fx are simulated, hence we need to find a list with all simulated currencies
        simulated_currency_id_list = self.get_currency_id_list()

        if model_currency_id not in simulated_currency_id_list:
            simulated_currency_id_list.insert(0, model_currency_id)

        # find the unique values, by first converting to a set then back to the list format
        simulated_currency_id_list = list(set(simulated_currency_id_list))

        if (term_currency_id not in simulated_currency_id_list) or (
            base_currency_id not in simulated_currency_id_list
        ):
            raise SimulationError(message='error, requested fx is not simulated')

        base_currency = self.get_currency(base_currency_id)
        term_currency = self.get_currency(term_currency_id)

        # in case base and term currencies do not belong to the commodities
        if base_currency is None:
            base_currency = model_currency
        elif term_currency is None:
            term_currency = model_currency

        base_currency_name = base_currency.get_name()
        term_currency_name = term_currency.get_name()
        model_currency_name = model_currency.get_name()

        # create path object
        forward_folder_path = Path(self.forward_folder)

        def load_fx(forward_folder_path, base_currency_name, term_currency_name):
            file_to_load = forward_folder_path.joinpath(
                'FX_' + base_currency_name + '_' + term_currency_name + '.mat'
            )
            try:
                with h5py.File(file_to_load, 'r') as f:
                    fx_matrix = f['FX'][()].T
            except:
                msg = (
                    'FX simulations with currency pair '
                    + base_currency_name
                    + '_'
                    + term_currency_name
                    + ' could not be loaded!'
                )
                raise SimulationError(message=msg)
            # [matlab datenum, sim_1, sim_2, ...]
            return fx_matrix

        if base_currency_id == model_currency_id:
            fx_matrix = load_fx(forward_folder_path, model_currency_name, term_currency_name)
        elif term_currency_id == model_currency_id:
            fx_matrix = load_fx(forward_folder_path, term_currency_name, base_currency_name)
            fx_matrix[:, 1:] = 1 / fx_matrix[:, 1:]

        else:
            # we need to get two fx and compute the requested fx

            # load base_currency / model_currency pair
            model_base_fx = load_fx(forward_folder_path, model_currency_name, base_currency_name)

            # load term_currency / model_currency pair
            model_term_fx = load_fx(forward_folder_path, model_currency_name, term_currency_name)

            fx_matrix = np.append(
                model_base_fx[:, 0][np.newaxis].T,
                model_term_fx[:, 1:] / model_base_fx[:, 1:],
                axis=1,
            )

        time_index = pd.to_datetime(fx_matrix[:, 0] - 719529, unit='D')

        fx_matrix = pd.DataFrame(fx_matrix[:, 1:])
        fx_matrix.set_index(time_index, inplace=True)
        fx_matrix = fx_matrix.loc[start_date:end_date]

        # rename column to include sim_1,sim_2,...
        fx_matrix.columns = self.create_sim_i_colum()

        return fx_matrix

    def convert_fx(
        self,
        simulation_prices: pd.DataFrame,
        from_currency_id: int,
        to_currency_id: int,
        delivery_period_name: str = None,
        delivery_period_id: int = None,
    ) -> pd.DataFrame:
        """
        Function which converts a set of simulations from one currency to another.

        Args:
            simulation_prices (pd.DataFrame): pd.DataFrame with simulated prices
            delivery_period_name (str, optional): granularity requested. hourly, daily and
                monthly supported.
            delivery_period_id (int, optional): Kyos delivery period id. hourly, daily and
                monthly supported. For example: if the simulations are in hourly format you
                should prodivde 2, if daily you should provide 3.
            from_currency_id (int): ID number of the currency of simulations.
            to_currency_id (int): ID number of the currency to which the currency should be
                converted.

        Returns:
            (pd.DataFrame): Dataframe containing the simulated prices, where each row
                represents a time period corresponding to the delivery_period supplied.

        Assumption:
          - All "values" are consecutive (no gaps in time steps).
          - Currently, the method can convert only from/to the KySim model currency

        Examples:
            >>> from kyoslib_py.simulation import Simulation
            >>> simulation_obj = Simulation()
            >>> fwd_sims = simulation_set.get_fwd_product(
                    commodity_name='TTF',
                    fwd_year=2021,
                    fwd_month=5,
                )
            >>> simulation_set.convert_fx(
                    simulation_prices=fwd_sims,
                    delivery_period_name='monthly',
                    from_currency_id=1,
                    to_currency_id=2,
                )
        """
        # copy the pd.dataframe, so that will not manipulate the input data
        simulation_prices = simulation_prices.copy()

        if from_currency_id == to_currency_id:
            # no conversion necessary
            return simulation_prices

        # check if number of sims of the simulation object is equal to the simulations in the df
        nr_sims_in_object = self.get_nr_simulations()
        nr_sims_in_df = simulation_prices.shape[1]

        if nr_sims_in_object != nr_sims_in_df:
            msg = (
                'No FX conversion can be executed: The number of simulations in the KySim '
                'profile does not match the simulation paths in values.'
            )
            raise SimulationError(message=msg)

        # Calculate mean of FX Prices which gives us the FX forward curve the calculation done
        # based on KySim methodology (See : SimLib\ SpotModel\ SaveStrike.m)
        start_date = simulation_prices.index.min()
        end_date = simulation_prices.index.max()

        # get fx = base / term
        fx_prices = self.get_fx(
            base_currency_id=from_currency_id,
            term_currency_id=to_currency_id,
            start_date=start_date,
            end_date=end_date,
        )

        # take the mean over the simulations so that we get a daily forward curve
        fx_prices = fx_prices.mean(axis=1)

        if (delivery_period_id is None) & (delivery_period_name is None):
            raise ValueError('Either a delivery period id or name should be provided.')

        granularity_id = delivery_period_id
        if granularity_id is None:
            # convert string to int
            granularity_id = delivery_period_id_from_name(delivery_period_name)

        if granularity_id == 3:
            intersection_index = simulation_prices.index.intersection(fx_prices.index)
            # fx_prices has fx prices on every day, however, it could be that simulation_prices
            # doesn't have prices everyday due to delivery_type such as peakload. We keep only
            # the days that are common in both dataframes
            simulation_prices = simulation_prices.loc[intersection_index]
            fx_prices = fx_prices.loc[intersection_index]
            fx_prices = fx_prices.to_numpy()[np.newaxis].T
        elif granularity_id == 5:
            # Take the average of all the days in the month. We resample with MS, which stands for
            # month start, so that the time index is the first of the month.
            # See https://stackoverflow.com/questions/17001389/pandas-resample-documentation
            fx_prices = fx_prices.resample('MS').mean().to_numpy()[np.newaxis].T
        elif granularity_id in [14, 1, 2]:
            fx_prices = fx_prices.to_numpy()[np.newaxis].T
            if granularity_id == 1:
                periods_per_day = 48
            elif granularity_id == 14:
                periods_per_day = 96
            elif granularity_id == 2:
                periods_per_day = 24
            # convert daily fx to quarter, half or hourly price.
            # Note we just copy daily fx for each period in a day
            fx_prices = np.kron(fx_prices, np.ones((periods_per_day, 1)))

        # if prices are in euro,
        # and the fx = eur / usd,
        # => prices_in_usd = prices_in_eur * eur / usd
        return simulation_prices.multiply(fx_prices)

    def get_weather_volume_sim(
        self, series_identifier, delivery_period_name, series_type, start_date=None, end_date=None
    ) -> pd.DataFrame:
        """
        A Simulation class method to import weather/volume/renewable simulations.

        Args:
            series_type (srting - choice between "weather" / "volume" / "renewable"): Type of the
                simulations. Volume and Weather simulations supported. Renewable is also a
                volume sim, it comes from recently introduced Renewable Asset object, which is a
                wrapper for holding more information related to Weather & Volume.
            series_identifier (int|string): \n
                if series_type = "weather" => (int) the id of the historical weather time-series
                    used by KySim \n
                if series_type = "volume" => (string) the user defined (in KySim) of the
                    simulated volume simulations \n
                if series_type = "renewable" => (int) the user defined (in KySim) Renewable
                    Asset id
            delivery_period_name (str): Curve delivery_period requested. Hourly and Daily
                supported.
            start_date (datetime, optional): Start date from which to begin the imported
                weather/volume simulations.
            end_date (datetime, optional): End date at which the imported weather/volume
                simulations will end (inclusive of this date).

        Returns:
            (pd.DataFrame): (weather_volume_simulations). Size: (start_date:end_date,
                NumSim+1). Containing the individual simulations per column where each row
                represents a unique day/hour. The first column represents the average of the
                weather/volume simulations.

        Examples:
            >>> from kyoslib_py.simulation import Simulation
            >>> import datetime as dt
            >>> simulation_obj = Simulation()
            >>> start_date = dt.datetime(2020, 3, 24)
            >>> end_date = dt.datetime(2020, 12, 31, 23)
            >>> volume_simulations = simulation_obj.get_weather_volume_sim(
                    series_identifier="Dutch_Offshore",
                    elivery_period_name='Hourly',
                    series_type='Volume',
                    start_date=start_date,
                    end_date=end_date,
                )
            >>> end_date = dt.datetime(2020, 12, 31)
            >>> weather_simulations = simulation_obj.get_weather_volume_sim(
                    series_identifier=25,
                    delivery_period_name='Daily',
                    series_type='Weather',
                    start_date=start_date,
                    end_date=end_date,
                )
        """
        weather_volume_simulations = {}
        if (
            series_identifier is not None
            and delivery_period_name is not None
            and series_type is not None
        ):
            # Input validation
            # Start Date
            if start_date is None:
                start_date = self.get_trading_date()
            # End Date
            if end_date is None:
                end_date = self.get_end_date()

            sim_other_dir = Path(self.get_other_sim_folder_path())
            if not sim_other_dir.exists():
                SimulationError(message=sim_other_dir.name + ' does not not exist!')

            if series_type.lower() == 'volume' or series_type.lower() == "renewable":
                suffix = ""
                if series_type.lower() == "renewable":
                    suffix = "RenewableAsset_"
                elif series_type.lower() == "volume" and isinstance(series_identifier, int):
                    suffix = "Volume_Series"  # this is the case with volumes generated from timeseries and
                    # "generate_auto_volumes" in kysim is set to AUTO
                    # and capture rates are set to YES
                else:
                    # series_type.lower() == "volume" and isinstance(series_identifier,str)
                    pass

                # Declare input file name and the path
                inputFilePath = sim_other_dir.joinpath(
                    f'VolumeSims_{suffix}{str(series_identifier)}.mat'
                )

                if not inputFilePath.exists():
                    SimulationError(message=f'{inputFilePath} does not exist!')

                # Import Volume Simulations
                try:
                    f = h5py.File(inputFilePath, 'r')
                    raw_data = f['VolumeSim'][()].T
                    raw_data = pd.DataFrame(raw_data)
                except:
                    raise SimulationError(
                        message='Volume '
                        + suffix
                        + ' simulations for the requested series id could not be found'
                    )

            elif series_type.lower() == 'weather':
                if delivery_period_name.lower() == 'hourly':
                    # Declare input file name and the path
                    inputFilePath = sim_other_dir.joinpath(
                        'WeatherSimsHourly_' + 'Series' + str(series_identifier) + '.mat'
                    )
                    # Import Hourly Weather Simulations
                    try:
                        f = h5py.File(inputFilePath, 'r')
                        raw_data = f['WeatherSimsHourly'][()].T
                        raw_data = pd.DataFrame(raw_data)
                    except:
                        raise SimulationError(
                            message='Hourly weather simulations for the requested series id could '
                            'not be found.'
                        )
                elif delivery_period_name.lower() == 'daily':
                    # Declare input file name and the path
                    inputFilePath = sim_other_dir.joinpath(
                        'WeatherSimsDaily_' + 'Series' + str(series_identifier) + '.mat'
                    )
                    # Import Daily Weather Simulations
                    try:
                        f = h5py.File(inputFilePath, 'r')
                        raw_data = f['WeatherSimsDaily'][()].T
                        raw_data = pd.DataFrame(raw_data)
                    except:
                        raise SimulationError(
                            message='Daily weather simulations for the requested series id could '
                            'not be found.'
                        )
                else:
                    raise SimulationError(
                        message='The delivery period requested was not simulated. Please choose '
                        'Daily or Hourly.'
                    )
            else:
                raise SimulationError(
                    message="The series type requested was not simulated. Please choose 'Volume' "
                    "or 'Weather'"
                )

            # Process Weather/Volume Simulations
            volume_sims = raw_data.loc[:, 4:]
            # calculate average of the simulations over the hours for the intrinsic valuation
            avg_volume = volume_sims.mean(axis=1, skipna=True)

            dates_df = pd.DataFrame(
                {
                    'year': raw_data.loc[:, 0],
                    'month': raw_data.loc[:, 1],
                    'day': raw_data.loc[:, 2],
                    'hour': raw_data.loc[:, 3],
                }
            )
            dates_df = pd.DataFrame.astype(dates_df, dtype='int')

            dates = pd.to_datetime(dates_df)

            # combine date , avg volume and volume simulations
            weather_volume_simulations = pd.concat(
                [dates, avg_volume, volume_sims], axis=1, ignore_index=True
            )
            # Set row index as dates
            weather_volume_simulations.set_index(
                weather_volume_simulations.iloc[:, 0], inplace=True
            )
            weather_volume_simulations.drop(columns=[0], inplace=True)
            # del weather_simulations[0]
            weather_volume_simulations = weather_volume_simulations.loc[start_date:end_date]

            # add column names [average, sim_1,sim_2,..]
            nr_simulations = self.get_nr_simulations()
            sim_ = np.repeat('sim_', nr_simulations)
            i = np.arange(1, nr_simulations + 1).astype(str)
            sim_i = np.char.add(sim_, i)
            column_names = np.array(['sim_average'])
            column_names = np.append(column_names, sim_i)

            weather_volume_simulations.columns = column_names

        return weather_volume_simulations

    def load_sims_for_all_months(
        self,
        month_codes,
        simulated_trading_dates,
        commodity_name,
        delivery_type_name,
        currency_name,
    ):
        """
        This method creates a 3d np array of simulations, based on the product (start, end
        delivery), commodity and delivery type.

        Args:
            month_codes (np.array(): vector of relevant month codes, sorted from small to big
            simulated_trading_dates (np.array(): vector of trading days
            commodity_name (str): name of the commodity
            delivery_type_name (str): name of the delivery type
            currency_name (str): currency name

        Returns:
            month_sims (np.array): (nr_simulated_days x nr_simulations x  nr_months)
        """
        nr_simulations = self.get_nr_simulations()
        sim_fwd_dir = Path(self.get_forward_sim_folder_path())
        year_from_mc, month_from_mc = mc_to_year_month(month_codes)

        first_requested_simulated_day = simulated_trading_dates[0]
        last_requested_simulated_day = simulated_trading_dates[-1]

        nr_months = year_from_mc.shape[0]
        nr_simulated_days = simulated_trading_dates.shape[0]

        month_sims = np.empty((nr_simulated_days, nr_simulations, nr_months))
        month_sims.fill(np.nan)
        # Load several simulations and store them in a 3d array ###################################
        for i in range(nr_months):
            choose_year_d = str(year_from_mc[i])
            # format months to two numbers, i.e. '9'-> '09' and '10' -> '10'
            forward_month = str(month_from_mc[i]).zfill(2)
            # remove first two characters from the string, i.e. 2019->19, so it matches the .mat
            # files.
            choose_year_d = choose_year_d[2:]

            if delivery_type_name == '':
                file_path = sim_fwd_dir.joinpath(
                    commodity_name + currency_name + "_m" + choose_year_d + forward_month + ".mat"
                )
            else:
                file_path = sim_fwd_dir.joinpath(
                    commodity_name
                    + '_'
                    + delivery_type_name
                    + currency_name
                    + "_m"
                    + choose_year_d
                    + forward_month
                    + ".mat"
                )

            if not file_path.exists():
                # if file doesn't exist we continue
                break

            try:
                with h5py.File(file_path, 'r') as f:
                    daily_forward_mat = f['Forward'][()].T
            except OSError:
                raise SimulationError(
                    message=f'Simulations for the requested delivery year: {year_from_mc[i]} '
                    f'and month: {month_from_mc[i]} not found. Please check the inputted '
                    f'year and month.'
                )

            time_index = np.array(matlab_datenum_to_datetime(daily_forward_mat[:, 0]))
            ind_in = (first_requested_simulated_day <= time_index) & (
                time_index <= last_requested_simulated_day
            )
            ind_out = simulated_trading_dates.isin(time_index)

            month_sims[ind_out, :, i] = daily_forward_mat[
                ind_in, 3:
            ]  # (nr_simulated_days x nr_simulations x  nr_months)
        ###########################################################################################
        return month_sims

    def calculate_tradable_product(
        self, commodity, start_delivery_mc, end_delivery_mc, month_codes, month_sims
    ):
        """
        This function calculates the tradable product. E.g. if product is quarter ahead we will
        have data in the following format (days, simulations, month_products). Month products
        will be 3 for a quarter.

        Args:
            commodity (Commodity): an instance of the commodity object
            start_delivery_mc (np.array): vector of month codes of the start delivery month
            end_delivery_mc (np.array): vector of month codes of the end delivery month
            month_codes (np.array): vector of month codes
            month_sims (np.array): three-dimensional array with

        Returns:
            (np.array):  2d vector (days, simulations) of days on the rows and simulations in
                the columns.
        """

        @jit(nopython=True, parallel=True)
        def weight_sims_by_hours(nr_months, month_sims, hours_delivery_month):
            for i in range(nr_months):
                month_sims[:, :, i] = month_sims[:, :, i] * hours_delivery_month[i]
            return month_sims

        nr_months = month_codes.shape[0]

        # To do: create COMMODITY.countDeliveryHours(delivery_type, OutGranul, MCStartDate,
        # MCEndDate), as in kyoslib

        # declare the delivery start and end date of the given product
        start_delivery_year, start_delivery_month = mc_to_year_month(month_codes.min())
        end_delivery_year, end_delivery_month = mc_to_year_month(month_codes.max())
        startP = dt.datetime(year=start_delivery_year, month=start_delivery_month, day=1)

        # Declare the product end date
        # Shift one month to define end of the mont
        if end_delivery_month == 12:
            end_delivery_month = 1
            end_delivery_year += 1
        else:
            end_delivery_month += 1
        endP = datetime(year=end_delivery_year, month=end_delivery_month, day=1) - timedelta(
            days=1
        )

        # get the delivery hours per month within the delivery period of the given product
        outputGranularity = 5  # Monthly data
        hours_delivery_month = commodity.count_delivery_hours(
            output_granularity=outputGranularity,
            delivery_type_id=1,
            start_date=startP,
            end_date=endP,
        )[0]

        month_sims = weight_sims_by_hours(nr_months, month_sims, hours_delivery_month)

        fixed_product_mc = np.unique(np.vstack((start_delivery_mc, end_delivery_mc)).T, axis=0)

        nr_days = month_sims.shape[0]
        nr_simulations = month_sims.shape[1]
        nr_delivery_moments = fixed_product_mc.shape[0]

        fwd_sims = np.zeros((nr_days, nr_simulations))
        for i in range(nr_delivery_moments):
            months_j = (fixed_product_mc[i, 0] <= month_codes) & (
                month_codes <= fixed_product_mc[i, 1]
            )
            days_i = (start_delivery_mc == fixed_product_mc[i, 0]) & (
                end_delivery_mc == fixed_product_mc[i, 1]
            )
            # numpy needs some help with advanced indexing, hence we use np.ix_, which creates a
            # tuple of the 1d arrays
            mask = np.ix_(days_i, np.array([True] * nr_simulations), months_j)

            # we multiplied price with number of hours so that we can create a hourly weighted
            # average
            product_delivery_hours = np.sum(hours_delivery_month[months_j])
            product_simulations = np.sum(month_sims[mask], axis=2)
            fwd_sims[days_i, :] = product_simulations / product_delivery_hours
        return fwd_sims

    def adjust_sims_is_cent(
        self, df_sims: pd.DataFrame, request_is_cent: bool, commodity: object
    ) -> pd.DataFrame:
        """
        Adjusts the simulations from or to cents.

        Args:
            df_sims (pd.DataFrame): A dataframe with simulations. Note that all the columns should
                contain simulations
            request_is_cent (bool): is the request to have the simulations in cent?
            commodity (kyoslib_py.settings.commodity): commodity object of the simulations. For
                this we can see if the simulations are in_cent or not.

        Returns:
            (pd.DataFrame): pd.DataFrame with if necessary converted simulations.
        """
        is_cent_sims = commodity.get_is_cent()
        if (request_is_cent is not None) and (request_is_cent != is_cent_sims):
            # we know that is_cent_sims is not equal to is_cent. Hence, one check is enough
            if request_is_cent:
                df_sims = df_sims.multiply(100)
            else:
                df_sims = df_sims.multiply(0.01)
        return df_sims

    def get_load_currency_info(
        self, commodity: object, currency_id: int = None, currency_name: str = None
    ) -> Tuple[str, int, int]:
        """
        Determine in what currency simulations should be loaded based on a choice of currency_name
        or currency_id. This is necessary because KySim outputs simulations only in the model
        currency and in the commodity currency.

        Args:
            commodity (kyoslib_py.settings.commodity): the commodity for this the prices are
                simulated.
            currency_name (str, optional): Name of the currency in which to import the
                simulations. Must be in currency which is simulated. Defaults to model base
                currency.
            currency_id (int, optional): currency of the currency in which to import the
                simulations. Must be in currency which is simulated. Defaults to model base
                currency.

        Returns:
            load_currency_name (str): The name of the currency in which the simulations will be
                loaded. This relevant if the simulations are simulated in the commodity currency.
                If the request is not commodity currency the simulations are loaded in the model
                currency. Then, later this can be converted via the .convert_fx() method.
            load_currency_id (int): the currency id in which the simulations should be loaded
                initially
            currency_id (int): the currency id in which the simulation should be outputted finally
        """
        commodity_currency_id = commodity.get_currency_id()
        model_currency = self.get_model_currency()
        model_currency_id = model_currency.get_id()

        if currency_id is not None:
            currency = self.get_currency(requested_currency_id=currency_id)
        elif currency_name is not None:
            currency = self.get_currency(requested_currency_name=currency_name)
        else:
            currency = None

        if currency is None:
            currency = model_currency

        currency_id = currency.get_id()

        currency_is_not_model_currency = currency_id != model_currency_id

        if (currency_id == commodity_currency_id) and currency_is_not_model_currency:
            # requested currency is commodity currency.
            commodity_currency = self.get_currency(requested_currency_id=commodity_currency_id)
            load_currency_name = commodity_currency.get_name()
            load_currency_id = commodity_currency.get_id()
        else:
            # load simulations are done in model currency.
            # If conversion is necessary is it will be done later converted to requested currency
            load_currency_name = str()
            load_currency_id = model_currency_id

        return load_currency_name, load_currency_id, currency_id

    def create_sim_i_colum(self) -> np.array:
        """
        Returns:
             (np.array): with [sim_1,sim_2,...]
        """
        nr_simulations = self.get_nr_simulations()
        sim_ = np.repeat('sim_', nr_simulations)
        i = np.arange(1, nr_simulations + 1).astype(str)
        sim_i = np.char.add(sim_, i)
        return sim_i

    @staticmethod
    def get_delivery_type_name_from_id(delivery_type_id: int, group_name: str) -> str:
        """
        Returns:
             delivery_type_name (str): used in fwd products to find file name
        """
        # Name of commodity includes base in the name for powers:
        if group_name == 'power':
            if delivery_type_id == 1:
                delivery_type_name = "Base"
            elif delivery_type_id == 2:
                delivery_type_name = "Peak"
            elif delivery_type_id == 3:
                delivery_type_name = "OffPk"
            else:
                raise SimulationError(
                    message=f'Delivery type: {delivery_type_id} supplied not supported'
                )
        else:
            delivery_type_name = ""
        return delivery_type_name
