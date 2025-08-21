import datetime as dt
import json
from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd

from kyoslib_py.kyos_api import call_kyos_api_v1


class HistoricalPrice:
    """
    The HistoricalPrice class allows the storing and loading of historical price spot and forward
    data sent to a model in csv format, in addition to historical_data_info.json.

    Attributes:
        id (int): Price source id
        commodity_id (int): Id number of the corresponding commodity
        type (string): spot' or 'forward'
        delivery_type (str): base', 'peak' or 'other' for forward prices, otherwise an empty list
        delivery_period_id (int): Id number of the delivery period for spot prices, otherwise an empty list
        prices (pd.DataFrame): Pandas dataframe containing the price data. Empty list until
            loaded with a method (see below).

    Notes:
        All historical price profiles contained with the json file in the HistoricalData directory are loaded at the same
        time and stored within the class variable all_price_sources. The path of the subdirectory is also saved as a class
        variable (price_path).

    Examples:
        >>> from kyoslib_py.historical_price import HistoricalPrice
        >>> HistoricalPrice()
        >>> HistoricalPrice.all_price_sources[0].id
        >>> 33
    """

    all_price_sources = []
    price_path = []

    def __init__(self, base_path=None):
        """
        Constructor method.

        Args:
            base_path (str, optional): String of the path of the main job directory. The HistoricalData subdirectory is assumed to be one level down.
        """

        if base_path is None:
            #  Assume main directory
            base_path = Path().absolute()
        else:
            base_path = Path(base_path)

        historical_price_path = base_path / 'HistoricalData'
        HistoricalPrice.price_path = copy(historical_price_path)  # Set class variable

        # Load and read json file
        full_path = historical_price_path / 'historical_data_info.json'
        with open(full_path) as f:
            data = json.load(f)

        # Assign objects
        num_sources = len(data)
        for i in range(num_sources):
            self.id = data[i]['id']
            self.commodity_id = data[i]['commodityId']
            self.type = data[i]['type']
            self.prices = []
            try:
                self.delivery_type = data[i]['deliveryType']
            except KeyError:
                self.delivery_type = []
            try:
                self.delivery_period_id = data[i]['deliveryPeriodId']
            except KeyError:
                self.delivery_period_id = []
            new_instance = copy(self)
            HistoricalPrice.all_price_sources.append(new_instance)

    def load_all_prices(self):
        """
        Method to load all price data in the associated csv file for a given price source id and store it as a
        DataFrame within the object.

        Returns:
            (HistoricalPrice): Instance of the HistoricalPrice class with prices field populated with a DataFrame; date columns are sent as type DateTime.

        Examples:
            >>> from kyoslib_py.historical_price import HistoricalPrice
            >>> HistoricalPrice()
            >>> HistoricalPrice.all_price_sources[0].load_all_prices()
        """

        csv_name = 'historical_data_' + str(self.id) + '.csv'
        full_path = self.price_path / csv_name
        prices_pd = pd.read_csv(full_path)
        if self.type == 'forward':
            prices_pd['trading_date'] = pd.to_datetime(
                prices_pd['trading_date'], format='%Y-%m-%d'
            )
        prices_pd['start_delivery'] = pd.to_datetime(
            prices_pd['start_delivery'], format='%Y-%m-%d'
        )
        self.prices = prices_pd

    def get_historical_prices(
        self,
        start_date=None,
        end_date=None,
        start_delivery_date=None,
        delivery_type_id=None,
        delivery_period_id=None,
        maturity=None,
    ):
        """
        Method to load specific price data for a given price source id. If already stored in the object, reads it
        directly otherwise loads it using the load_all_prices method.

        Args:
            start_date (Datetime, optional): Start date from which to return prices. For forward prices, the trading date is used. For spot, the delivery
                date is used. Defaults to the earliest date if not provided.
            end_date (Datetime, optional): End date before which to return prices. For forward prices, the trading date is used. For spot, the delivery
                date is used. Defaults to the latest date if not provided.
            start_delivery_date (Datetime, optional): Only return prices with delivery that starts on this date (relevant for forward prices only, otherwise use
                start_date and end_date). All delivery starts returned if not provided.
            delivery_type_id (list, optional): List of delivery type ids for which to return historical prices. Only relevant for forward prices. All
                delivery types returned if not provided.
            delivery_period_id (list, optional): List of delivery period ids for which to return historical prices. Only relevant for forward prices. All
                delivery periods returned if not provided.
            maturity (list, optional): List of maturities for which to return historical prices. Only relevant for forward prices. All
                maturities returned if not provided

        Returns:
            (pd.DataFrame): DataFrame of the relevant price data. Returned in same format as the
                input data, which depends on the data being of type 'forward' or 'spot'.

        Examples:
            --------
            >>> from kyoslib_py.historical_price import HistoricalPrice
            >>> HistoricalPrice()
            >>> HistoricalPrice.all_price_sources[0].get_historical_prices()
            >>> HistoricalPrice.all_price_sources[0].get_historical_prices(start_date=dt.datetime(2019,1,1),
                delivery_period_id = [1 2])
        """

        # Check if prices already loaded, otherwise load them
        all_prices = self.prices
        if len(all_prices) == 0:
            self.load_all_prices()
            all_prices = self.prices

        #  Keep prices between start and end dates if provided
        if self.type == 'forward':
            #  Trading date range
            if start_date is None:
                start_date = all_prices['trading_date'].min()
            if end_date is None:
                end_date = all_prices['trading_date'].max()
            #  Remove prices outside these dates
            id_post_dates = all_prices['trading_date'] >= start_date
            id_pre_dates = all_prices['trading_date'] <= end_date
        elif self.type == 'spot':
            #  Delivery date range
            if start_date is None:
                start_date = all_prices['start_delivery'].min()
            if end_date is None:
                end_date = all_prices['start_delivery'].max()
            #  Remove prices outside these dates
            id_post_dates = all_prices['start_delivery'] >= start_date
            id_pre_dates = all_prices['start_delivery'] <= end_date
        else:
            exit('Failed to load historical price data: price type not recognised')

        id_dates = id_post_dates & id_pre_dates
        prices_out = all_prices[id_dates]

        # Filter out other parameters if provided
        if self.type == 'forward':
            if start_delivery_date is not None:
                id_start_del = prices_out['start_delivery'] == start_delivery_date
                prices_out = prices_out[id_start_del]

            if delivery_type_id is not None:
                prices_out = prices_out[prices_out.delivery_type_id.isin(delivery_type_id)]

            if delivery_period_id is not None:
                prices_out = prices_out[prices_out.delivery_period_id.isin(delivery_period_id)]

            if maturity is not None:
                prices_out = prices_out[prices_out.maturity.isin(maturity)]

        return prices_out

    @staticmethod
    def get_historical_prices_api(
        profile_id,
        price_type,
        csv_write=False,
        start_date=None,
        end_date=None,
        products=None,
        delivery_start_date=None,
        maturity=None,
    ):
        """
        Static method to load spot or forward price data for a specific price source ID via API, with option to save to
        disk as csv file & json (as per the format expected by the HistoricalPrice class).

        Args:
            profile_id (int): price source ID number
            price_type (string): Type of prices being requested, must be either 'forward' or 'spot'. Case insensitive.
            csv_write (Boolean, optional): If true, writes data to csv and JSON in specific format. Defaults to False.
            start_date (string, optional): YYYY-MM-DD format, start date for API request.
            end_date (string, optional): YYYY-MM-DD format, start date for API request.
            products (list, optional): List of products being requested (strings). Relevant for forward data only. Must
                be one of the following: day, month, quarter, season, calyear, gasyear, weekend, week, bow, wdnw or bom.
            delivery_start_date (string, optional): Delivery start date of requested price data in YYYY-MM-DD format.
                Relevant for forward data only. Can only be used in combination with one product and not with maturity.
            maturity (int, optional): Maturity of requested data. Relevant for forward data only. Can only be used in
                combination with one product and cannot be used with maturity.

        Returns:
            (pd.DataFrame): DataFrame of the relevant price data in specific format which varies
                depending on the data being spot or forward.

        Examples:
            --------
            >>> from kyoslib_py.historical_price import HistoricalPrice as Hp
            >>> prices = Hp.get_historical_prices_api(profile_id=15, price_type='spot')
            >>> prices = Hp.get_historical_prices_api(profile_id=27, price_type='forward', csv_write=True)
            >>> prices = Hp.get_historical_prices_api(profile_id=15, price_type='spot', start_date='2020-07-20',
            >>>                                       end_date='2020-08-01')

        """

        def create_df_from_dict(input_dict, price_type):
            """
            Function to convert a dictionary of price data into a DataFrame (either forward or spot) as received from
            the API get request for historical price data.

            Final format corresponds to the standard csv data format for historical prices (forward and spot). i.e. the
            DataFrame is csv-write ready,
            """

            # Spot data
            if str.casefold(price_type) == 'spot':
                input_dict_list = input_dict.get(
                    'dates'
                )  # get list of dicts (one per trading date)
                price_data = [
                    x['prices'] for x in input_dict_list
                ]  # get list of lists with prices
                spot_prices = [y['price'] for x in price_data for y in x]  # unpack prices
                start_del_dates = [
                    y['start_delivery'] for x in price_data for y in x
                ]  # unpack start delivery dates

                # Combine and store in dataframe
                spot_data = {'start_delivery': start_del_dates, 'price': spot_prices}
                final_df = pd.DataFrame(spot_data, columns=['start_delivery', 'price'])

            # Forward data
            elif str.casefold(price_type) == 'forward':
                nr_delivery_types = len(input_dict.get('delivery_types'))
                if nr_delivery_types > 0:
                    del_type_dict = input_dict.get('delivery_types')[
                        0
                    ]  # Dict with high level info
                    fwd_del_type_id = del_type_dict.get('delivery_type_id')
                    dates_list = del_type_dict.get('dates')  # List of dicts
                    trading_date_list = [
                        x['trading_date'] for x in dates_list
                    ]  # unique trading dates
                    del_period_list = [
                        x['delivery_periods'] for x in dates_list
                    ]  # one item per trading date

                    # Get number of unique delivery periods per trading date & build list of trading dates of matching
                    # length
                    trading_date_lens = [len(x) for x in del_period_list]
                    prelim_trading_date_list = []
                    for t, u in enumerate(trading_date_list):
                        prelim_trading_date_list.extend(
                            [u] * trading_date_lens[t]
                        )  # overload multiplication

                    # Unpack delivery periods and prices from lists/dicts & make lists of the correct size with correct
                    # delivery period and trading dates (order is important and automatically preserved).
                    del_periods = [y['delivery_period_id'] for x in del_period_list for y in x]
                    prices_list = [y['prices'] for x in del_period_list for y in x]
                    prices_lens = [
                        len(x) for x in prices_list
                    ]  # number of prices per delivery period
                    final_del_period_list = []
                    final_trading_date_list = []
                    for r, s in enumerate(del_periods):
                        final_del_period_list.extend(
                            [s] * prices_lens[r]
                        )  # overload multiplication (i.e. duplication)
                        final_trading_date_list.extend(
                            [prelim_trading_date_list[r]] * prices_lens[r]
                        )  # overload multi
                    fwd_prices = [y['price'] for x in prices_list for y in x]
                    start_delivery_dates = [y['start_delivery'] for x in prices_list for y in x]
                    fwd_maturity = [y['maturity'] for x in prices_list for y in x]
                    num_prices = len(fwd_prices)
                    del_type_ids = [fwd_del_type_id] * num_prices  # overload multiplication

                    # Combined and store in DataFrame
                    final_df = pd.DataFrame(
                        zip(
                            final_trading_date_list,
                            start_delivery_dates,
                            final_del_period_list,
                            fwd_maturity,
                            del_type_ids,
                            fwd_prices,
                        ),
                        columns=[
                            'trading_date',
                            'start_delivery',
                            'delivery_period_id',
                            'maturity',
                            'delivery_type_id',
                            'price',
                        ],
                    )
                else:
                    return

            return final_df

        # Preliminary checks on input parameters
        if str.casefold(price_type) == 'spot':
            if products is not None:
                print(
                    'Products filter cannot be used with spot price data request. It will be ignored'
                )
            if delivery_start_date is not None:
                print(
                    'Delivery start date filter cannot be used with spot price data request. It will be ignored'
                )
            if maturity is not None:
                print(
                    'Maturity filter cannot be used with spot price data request. It will be ignored'
                )

        # Process start and end dates if provided & start building URL
        start = ''
        end = ''
        if start_date is not None:
            start = f'from={start_date}'
        if end_date is not None:
            end = f'to={end_date}'

        url_options = ''
        if start or end:
            if start and end:
                url_options = f'{start}&{end}'
            elif start and not end:
                url_options = f'{start}'
            elif not start and end:
                url_options = f'{end}'

        # Filters for forward products
        if str.casefold(price_type) == 'forward':
            # Products filter
            if products is not None:
                prod_str = f'{products[0].lower()}'
                for p, q in enumerate(products):
                    if p == 0:
                        continue
                    else:
                        prod_str = f'{prod_str},{products[p].lower()}'
                amp = '&'
                if len(url_options) == 0:
                    amp = ''
                url_options = f'{url_options}{amp}filter[products]={prod_str}'

            # Maturity filter
            if maturity is not None:
                if delivery_start_date is not None:
                    print(
                        'Maturity and delivery start date filters cannot be used together. They will both be ignored'
                    )
                else:
                    if products is not None:
                        if len(products) != 1:
                            print(
                                'Maturity filter can only used in conjunction with one product type. '
                                'Maturity will be ignored'
                            )
                        else:
                            url_options = f'{url_options}&filter[maturity]={maturity}'
                    else:
                        print(
                            'One product type must be specified to use the maturity filter. It will be ignored'
                        )

            # Delivery start date filter
            if delivery_start_date is not None:
                if maturity is None:
                    if products is not None:
                        if len(products) != 1:
                            print(
                                'Delivery start date filter can only used in conjunction with one product type. '
                                'It will be ignored'
                            )
                        else:
                            url_options = (
                                f'{url_options}&filter[delivery_start_date]={delivery_start_date}'
                            )
                    else:
                        print(
                            'One product type must be specified to use the delivery start date filter. It will be '
                            'ignored'
                        )

        # Build final URL request and call API
        if str.casefold(price_type) == 'spot':
            url = f"/pricedata/spotprices/{profile_id}?{url_options}"
            status, data = call_kyos_api_v1(url, method='get', payload={}, timeout=20)
        elif str.casefold(price_type) == 'forward':
            url = f"/pricedata/forwardprices/{profile_id}?{url_options}"
            status, data = call_kyos_api_v1(url, method='get', payload={}, timeout=30)
        else:
            print("Input price type must be either 'forward' or 'spot'")
            return

        # Process request if successful
        if 200 >= status < 300:
            commodity_list = (data.get('relationships')).get('commodity')
            commodity_id = commodity_list[0].get('id')
            prices = data.get('data')
        else:
            print("An error was encountered")
            return

        # Convert dictionary data from JSON into DataFrame of required format
        prices_df = create_df_from_dict(input_dict=prices, price_type=price_type)

        if prices_df is None:
            print(
                'The request was successful but no prices were found with the requested parameters'
            )
            return

        # Write to csv if required
        if csv_write:

            def create_price_json(
                profile_id, commodity_id, price_type, delivery_period_id=None, delivery_type=None
            ):
                """
                Function that writes price source profile information to json in the agreed format (either appended to
                 existing file or creates a new file if it does not exist). Stored in the HistoricalData subdirectory in
                 historical_data_info.json
                """

                json_file_path = Path('HistoricalData') / 'historical_data_info.json'

                # Build dictionary to write to JSON. Format is different for spot and forward sources.
                price_dict = {'id': profile_id}
                price_dict['commodityId'] = commodity_id
                price_dict['type'] = str.casefold(price_type)
                if str.casefold(price_type) == 'spot':
                    price_dict['deliveryPeriodId'] = delivery_period_id
                elif str.casefold(price_type) == 'forward':
                    price_dict['deliveryType'] = delivery_type
                pass

                # If JSON exists, append data. Otherwise, create a new json.
                if json_file_path.is_file():
                    with open(json_file_path, "r+") as file:
                        data = json.load(file)
                        data.append(price_dict)
                        file.seek(0)
                        json.dump(data, file)
                else:
                    # Create a new file
                    price_list = [price_dict]
                    with open(json_file_path, 'w') as fp:
                        json.dump(price_list, fp)

            # Prepare directory and file paths. Write price data to CSV.
            Path('HistoricalData').mkdir(parents=True, exist_ok=True)
            file_name = f'historical_data_{profile_id}.csv'
            file_path = Path('HistoricalData') / file_name
            prices_df.to_csv(path_or_buf=file_path, sep=',', index=False)

            # Find delivery period and type of the price data
            del_period_id = None
            del_type = None
            if str.casefold(price_type) == 'spot':
                # TODO: the following code can be removed when the API request includes delivery period information.
                # Detect delivery period by checking number of unique periods per day in the data. May not work in all
                # cases, due to missing data etc.
                dates = prices.get('dates')
                lens = [len(x.get('prices')) for x in dates]
                unique_periods_per_day = list(set(lens))
                hourly_periods = [23, 24, 25]
                half_hourly_periods = [46, 48, 50]
                daily_periods = [1, 2, 3]
                if any(np.in1d(half_hourly_periods, unique_periods_per_day)):
                    del_period_id = 1
                elif any(np.in1d(hourly_periods, unique_periods_per_day)):
                    del_period_id = 2
                elif any(np.in1d(daily_periods, unique_periods_per_day)):
                    del_period_id = 3
                else:
                    print(
                        'Delivery period could not be determined! It will be set to daily by default'
                    )
                    del_period_id = 3
            else:
                # Must be forward data at this point
                del_type_id = prices.get('delivery_types')[0].get('delivery_type_id')
                if del_type_id == 1:
                    del_type = 'base'
                elif del_type_id == 2:
                    del_type = 'peak'
                else:
                    del_type = 'other'

            # Create or append relevant profile data to historical_data_info.json
            create_price_json(
                profile_id=profile_id,
                commodity_id=commodity_id,
                price_type=price_type,
                delivery_period_id=del_period_id,
                delivery_type=del_type,
            )

        return prices_df
