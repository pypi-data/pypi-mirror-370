import datetime as dt

import numpy as np

"""
Module which contains functionality related to tradable products:
- For example, calculating start-end delivery date of a rolling tradable product, such as month-ahead.
"""


def add_month_year(date, years=0, months=0):
    """Add time-delta of months/years to a datetime:

    Args:
        date (datetime): date which should be shifted with days or months.
        years (int): with how many years to shift the date.
        months (int): with how many months to shift the date.

    Returns:
        (tuple): tuple containing:

            - (int): year_shift
            - (int): month_shift

    Note:
        * These can be used to build a new datetime. \n
        * It is not clear how days/hours in a month should be shifted in this case. Thus,
        no shifted day/hour is reported.
    """
    year_orig = date.year
    month_orig = date.month
    mc_shift = (year_orig + years) * 12 + month_orig + months
    month_shift = divmod(mc_shift - 1, 12)[1] + 1
    year_shift = (mc_shift - month_shift) / 12

    return int(year_shift), int(month_shift)


def shift_business_date(date, shift, trading_calendar=None):
    """
    Given a date "start_date", find the business day "lag_days" before it.

    Args:
        date (datetime): a date, can be any date (business and non-business).
        shift (int) != 0: number of shifted business days relative to the "date". For example:
            * shift = 1,  the first business day after the "date".
            * shift = 2,  the second business day after the "date".
            * shift = -1, the first business day before the "date".
            * shift = -2, the business day before the business day prior to the "date".
        trading_calendar (numpy array, optional): List of exchange holiday dates
            * holidays may influence start and end date of tradable products, such as BOM, week ahead.
            [(nHolidays x 1)]

    Returns:
        (datetime): prev_date
    """
    if trading_calendar is None:
        trading_calendar = np.array([None])
    shift = int(shift)

    # shift the date backwards/forwards one business day at a time
    shift_date = date
    for day in range(abs(shift)):
        is_holiday = True  # check if shift_date is a holiday

        if shift < 0:
            # find the previous business day
            shift_date = shift_date - dt.timedelta(days=1)
            while is_holiday is True:
                DoW = shift_date.weekday()
                if DoW == 6:  # Sunday
                    shift_date = shift_date - dt.timedelta(days=2)
                elif DoW == 5:  # Saturday
                    shift_date = shift_date - dt.timedelta(days=1)
                elif any(trading_calendar == shift_date):
                    shift_date = shift_date - dt.timedelta(days=1)
                else:
                    is_holiday = False

        elif shift > 0:
            # find the next business day
            shift_date = shift_date + dt.timedelta(days=1)
            while is_holiday is True:
                DoW = shift_date.weekday()
                if DoW == 6:  # Sunday
                    shift_date = shift_date + dt.timedelta(days=1)
                elif DoW == 5:  # Saturday
                    shift_date = shift_date + dt.timedelta(days=2)
                elif any(trading_calendar == shift_date):
                    shift_date = shift_date + dt.timedelta(days=1)
                else:
                    is_holiday = False

    return shift_date


def get_start_end(
    trading_date,
    delivery_period,
    maturity,
    roll_days=None,
    trading_calendar=None,
    use_gas_rules=False,
):
    """
    Calculate the start/end dates of a tradable product(s).
    - Implementation is only for baseload (this should be extended in the future).

    Args:
        trading_date (datetime): trading date
        delivery_period (numpy array or list): products' delivery period, e.g. 5 = month, etc.
            * Currently, only the platform assumed delivery type integers are implemented.
            [nProducts x 1]
        maturity (numpy array or list containing integers =>0): products' maturity id.
            [nProducts x 1]
        roll_days (numpy array, optional): roll dates before the end of the calendar product,
            when maturity rolls forward
                * A value of 0 means the product is traded up to the start of the new period.
                * 1 means on last day of the running period, the next period is not traded anymore. Etc.
                * A trading calendar can be used. In which case the "1" will be interpreted as the rolling happening on
                  the last tradable day within the current product, e.g month.
            [nProducts x 1]
        trading_calendar (numpy array, optional): List of exchange holiday dates
            * holidays may influence start and end date of tradable products, such as BOM, week ahead.
            [nHolidays x 1]
        use_gas_rules (bool, optional): should the European gas market rules be used to calculate the
            delivery period of tradable produts. They affect how day-ahead, BOW, BOM are calculated.

    Returns:
        (list of datetimes): all_start_dates / all_end_dates (nProducts x 1): Start/End dates of each tradable product
            * if a product is not traded on the given trading date, then output NaN as start and end.
    """
    # initialize None arguments
    if trading_calendar is None:
        trading_calendar = np.array([None])
    if roll_days is None:
        # assume product maturities roll at the end of the product,
        # e.g. a month ahead rolls on the first day of the consecutive month
        roll_days = np.zeros(shape=len(delivery_period))

    # loop over the products
    trading_year = trading_date.year
    trading_month = trading_date.month
    all_start_dates = list()
    all_end_dates = list()
    for p in range(len(delivery_period)):
        p_maturity = int(maturity[p])
        p_roll_days = int(roll_days[p])  # relevant only for months and higher granularity

        # Day-Ahead ##########
        if delivery_period[p] == 3:
            if use_gas_rules is False:
                # non-working days do not play a role
                start_date = trading_date + dt.timedelta(days=p_maturity)
            else:
                # (N) Day-ahead product = (N) business days ahead:
                start_date = shift_business_date(
                    trading_date, p_maturity, trading_calendar=trading_calendar
                )
            p_start_date = start_date
            p_end_date = p_start_date

        # Weekend(s) ahead ##########
        if delivery_period[p] == 12:
            DoW = trading_date.weekday()
            #  Saturday and Sunday
            shift_days = int((DoW == 6) * 6 + (DoW == 5) * 7 + (DoW < 5) * (5 - DoW)) + int(
                7 * (p_maturity - 1)
            )
            start_date = trading_date + dt.timedelta(days=shift_days)
            end_date = start_date + dt.timedelta(days=1)

            if use_gas_rules:
                # Weekend:
                #  - Saturday + Sunday
                #  - Include  preceding or following holidays (non-working days)

                # Extend start date
                tomorrow = trading_date + dt.timedelta(days=1)
                is_start_holiday = True
                prev_start_date = start_date
                while is_start_holiday is True:
                    prev_start_date = prev_start_date - dt.timedelta(days=1)
                    if prev_start_date >= tomorrow and any(trading_calendar == start_date):
                        start_date = prev_start_date
                    else:
                        is_start_holiday = False

                # Extend end date
                is_end_holiday = True
                next_end_date = end_date
                while is_end_holiday is True:
                    next_end_date = next_end_date + dt.timedelta(days=1)
                    if any(trading_calendar == next_end_date):
                        end_date = next_end_date
                    else:
                        is_end_holiday = False

            p_start_date = start_date
            p_end_date = end_date

        # BOW (balance-of-week) ##########
        if delivery_period[p] == 15 and p_maturity == 0:
            if use_gas_rules is False:
                # From next day to next Sunday
                p_start_date = trading_date + dt.timedelta(days=1)
                DoW = p_start_date.weekday()
                p_end_date = p_start_date + dt.timedelta(days=int(6 - DoW))

            else:  # Use holidays
                # - Only trading on Monday, Tuesday, Wednesday.
                # - Starting at next working day until and including following Friday.
                p_start_date = None
                p_end_date = None
                DoW = trading_date.weekday()
                if 0 <= DoW <= 2:  # trading date is on Monday, Tuesday, Wednesday
                    start_date = trading_date
                    is_holiday = True  # check if day is a holiday
                    existBOW = True  # track if we exceeded following Friday as en end-date
                    while is_holiday is True:
                        start_date = start_date + dt.timedelta(days=1)
                        DoW = start_date.weekday()
                        if not any(trading_calendar == start_date):
                            is_holiday = False  # start date is not a holiday
                        if DoW > 4:  # following Friday
                            # BOW does not exist
                            existBOW = False
                            break
                    if existBOW:
                        p_start_date = start_date
                        p_end_date = start_date + dt.timedelta(
                            days=int(4 - DoW)
                        )  # up to following Friday

        # Week(s) / WDNW ahead ##########
        if delivery_period[p] == 11 or (delivery_period[p] == 13 and use_gas_rules is True):
            # For gases, WDNW is interpreted as a Week.
            day_forward = trading_date + dt.timedelta(days=1)
            DoW = day_forward.weekday()
            # start on Monday
            shift_days = int(1 + (DoW < 6) * (6 - DoW)) + int(7 * (p_maturity - 1))
            start_date = day_forward + dt.timedelta(days=shift_days)

            if use_gas_rules:
                # ICE Definition (treat weeks as gas Working-days next week)
                # - The Working Days Next Week contract (WK/DYNW) is a strip that spans five individual and
                #   consecutive gas days from Monday 6:00 (CET) through to Saturday 06:00 (CET).
                # - UK Bank Holidays are not included in the WK/DY NW contracts in case UK bank holidays runs
                #   sequentially either after Sunday or before Saturday.
                end_date = start_date + dt.timedelta(days=4)  # finish on Friday

                # Move the start_date forward in case Monday is on a holiday
                is_holiday = True
                while is_holiday is True:
                    if any(trading_calendar == start_date):
                        start_date = start_date + dt.timedelta(days=1)
                    else:
                        is_holiday = False

                # Move the end_date backwards in case Friday is on a holiday
                is_end_holiday = True
                prev_end_fate = end_date
                while is_end_holiday is True:
                    if any(trading_calendar == prev_end_fate):
                        prev_end_fate = prev_end_fate - dt.timedelta(days=1)
                    else:
                        is_end_holiday = False
                end_date = prev_end_fate

            else:  # non-gas commodity
                end_date = start_date + dt.timedelta(days=6)  # finish on Sunday

            p_start_date = start_date
            p_end_date = end_date

        # BOM (balance-of-month) ##########
        if delivery_period[p] == 4 and p_maturity == 0:
            day_forward = trading_date + dt.timedelta(days=1)
            year, month = add_month_year(day_forward, months=1)
            end_month = dt.datetime(year=year, month=month, day=1) - dt.timedelta(days=1)

            if use_gas_rules is False:
                p_start_date = day_forward
                p_end_date = end_month
            else:  # Use Gas Market Rules
                # BOM
                # - Ends on the last day of the month.
                # - Starts on second day product forward:
                #   -> each business day counts as one day product.
                #   -> a string of non-business days is treated as one day product.
                #
                # For example:
                #    -> if we are on a Thursday, BOM starts on Saturday,
                #    -> if we’re on a Friday, BOM starts on Monday.
                #    -> if we’re on a Monday, BOM starts on Wednesday.
                #    -> if we’re on Thursday before Easter, BOM starts on Tuesday etc.
                #
                # At some dates at the end of a month, there won’t be a BOM contract,
                # - 2 days before,
                # - day before an don last day of month and if last day of month is on
                #   a weekend day or a bank holiday, Monday there will be
                #   no BOM on the Thursday or Friday.
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # non-business days = Saturday, Sunday, Exchange non-trading day
                DoW = day_forward.weekday()
                is_non_business = DoW == 5 or DoW == 6 or any(trading_calendar == day_forward)
                while is_non_business:
                    next_day = day_forward + dt.timedelta(days=1)
                    DoW = next_day.weekday()
                    is_non_business = DoW == 5 or DoW == 6 or any(trading_calendar == next_day)
                    if is_non_business:
                        day_forward = next_day

                start_date = day_forward + dt.timedelta(days=1)

                if start_date <= end_month:
                    p_start_date = start_date
                    p_end_date = end_month
                else:
                    p_start_date = None
                    p_end_date = None

        # Month(s)-ahead product  ##########
        if delivery_period[p] == 5:
            # calculate the roll date (first day in the consecutive month, possibly shifted with # roll days)
            roll_year, roll_month = add_month_year(trading_date, months=1)
            roll_date = shift_business_date(
                dt.datetime(roll_year, roll_month, 1),
                -p_roll_days - 1,
                trading_calendar=trading_calendar,
            )
            if roll_date < trading_date:
                p_maturity = p_maturity + 1

            # calculate start/end date of the product with desired maturity
            start_year, start_month = add_month_year(trading_date, months=p_maturity)
            p_start_date = dt.datetime(start_year, start_month, 1)
            end_year, end_month = add_month_year(trading_date, months=p_maturity + 1)
            p_end_date = dt.datetime(end_year, end_month, 1) - dt.timedelta(days=1)

        # Quarter(s)-ahead product  ##########
        if delivery_period[p] == 6:
            start_month_curr = int(
                np.floor((trading_month - 1) / 3) * 3 + 1
            )  # start month of the current quarter
            start_product_current = dt.datetime(year=trading_year, month=start_month_curr, day=1)

            # calculate the roll date (first day in the consecutive quarter, possibly shifted with roll # days)
            roll_year, roll_month = add_month_year(start_product_current, months=3)
            roll_date = shift_business_date(
                dt.datetime(roll_year, roll_month, 1),
                -p_roll_days - 1,
                trading_calendar=trading_calendar,
            )
            if roll_date < trading_date:
                p_maturity = p_maturity + 1

            # find start/end date of the product with the desired maturity
            start_year, start_month = add_month_year(start_product_current, months=p_maturity * 3)
            p_start_date = dt.datetime(year=start_year, month=start_month, day=1)
            end_year, end_month = add_month_year(p_start_date, months=3)
            p_end_date = dt.datetime(year=end_year, month=end_month, day=1) - dt.timedelta(days=1)

        # Calendar-year(s) ahead  ##########
        if delivery_period[p] == 8:
            # check if the quoted maturity has already rolled at the end of the current product
            roll_date = shift_business_date(
                dt.datetime(trading_year + 1, 1, 1),
                -p_roll_days - 1,
                trading_calendar=trading_calendar,
            )
            if roll_date < trading_date:
                p_maturity = p_maturity + 1

            # calculate start/end date of the product with desired maturity
            p_start_date = dt.datetime(trading_year + p_maturity, 1, 1)
            p_end_date = dt.datetime(trading_year + p_maturity, 12, 31)

        # Gas-year(s) ahead  ##########
        if delivery_period[p] == 9:
            # find end date of the current gas year
            if trading_month < 10:
                end_year_current = trading_year
            else:
                end_year_current = trading_year + 1
            end_date_current = dt.datetime(end_year_current, 9, 30)

            # check if the quoted maturity has already rolled at the end of the current product
            roll_date = shift_business_date(
                end_date_current + dt.timedelta(days=1),
                -p_roll_days - 1,
                trading_calendar=trading_calendar,
            )
            if roll_date < trading_date:
                p_maturity = p_maturity + 1

            # find start/end date of the product with the desired maturity
            p_start_date = dt.datetime(year=end_year_current + p_maturity - 1, month=10, day=1)
            p_end_date = dt.datetime(year=end_year_current + p_maturity, month=9, day=30)

        # Season(s) ahead  ##########
        if delivery_period[p] == 7:
            # find end date of the current season
            if 4 <= trading_month <= 9:
                end_date_current = dt.datetime(trading_year, 9, 30)
            else:
                if trading_month <= 3:
                    end_date_current = dt.datetime(trading_year, 3, 31)
                elif 10 <= trading_month:
                    end_date_current = dt.datetime(trading_year + 1, 3, 31)

            # check if the quoted maturity has already rolled at the end of the current product
            roll_date = shift_business_date(
                end_date_current + dt.timedelta(days=1),
                -p_roll_days - 1,
                trading_calendar=trading_calendar,
            )
            if roll_date < trading_date:
                p_maturity = p_maturity + 1

            # find start/end date of the product with the desired maturity
            end_year, end_month = add_month_year(end_date_current, months=p_maturity * 6 + 1)
            p_end_date = dt.datetime(year=end_year, month=end_month, day=1) - dt.timedelta(days=1)
            start_year, start_month = add_month_year(p_end_date, months=-5)
            p_start_date = dt.datetime(year=start_year, month=start_month, day=1)

        all_start_dates.append(p_start_date)
        all_end_dates.append(p_end_date)
    return all_start_dates, all_end_dates


def delivery_period_id_from_name(delivery_period_name: str) -> int:
    """
    Working with id's can make the code more robust. For example when you want to get daily simulations, should you
    provide as delivery_period: daily, Daily, Day, twenty-four hours. This function converts common delivery period names to
    integers \n
        Currently supported: \n
            monthly -> 5 \n
            daily -> 3 \n
            hourly -> 2 \n
            halfhourly -> 1 \n
            quarterhourly -> 14 \n

    Args:
        delivery_period_name (str): granularity in string format, such as monthly or daily

    Returns:
        granularity_id (int) : KYOS platfrom's delivery type id
    """
    if not isinstance(delivery_period_name, str):
        raise TypeError("Input should be a string, such as 'month'")

    # make lowercase
    delivery_period_name = delivery_period_name.lower()

    # convert granularity to int
    if delivery_period_name in ['monthly', 'month']:
        granularity_id = 5
    elif delivery_period_name in ['daily', 'day']:
        granularity_id = 3
    elif delivery_period_name in ['hourly', 'hour']:
        granularity_id = 2
    elif delivery_period_name in ['halfhourly', 'halfhour', 'half-hour']:
        granularity_id = 1
    elif delivery_period_name in ['quarterhourly', 'quarterhour', 'quarter-hour']:
        granularity_id = 14
    else:
        raise ValueError('Input value: ' + delivery_period_name + '  is not supported')

    return granularity_id
