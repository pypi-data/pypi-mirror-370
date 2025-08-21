import collections.abc
import os
from datetime import datetime, timedelta

import numpy as np
from postmarker.core import PostmarkClient


def dict_merge(initial_dict, *args, overwrite_existing=False):
    """
    Instead of updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into ``dct``.

    Args:
        initial_dict (dict): Dict onto which the merge is executed
        *args (dict): Any number of dictonaries to be merged into initial_dict
        overwrite_existing (bool): Display the column name in bold font when showing it in the platform front-end

    Returns:
        rtn_dct (dict): merged dictonary

    Examples:
        >>> initial = {"accumulator": {"knock_out_price": 150, "trigger_price": 130, "accumulation_price": 110}}
        >>> new_key_dict = {"accumulator": {"sim": {"id": 10}}}
        >>> final = dict_merge(initial, new_key_dict)
        {"accumulator": {"knock_out_price": 150, "trigger_price": 130, "accumulation_price": 110, "sim": {"id": 10}}}
    """
    assert (
        initial_dict is not None and len(args) >= 1
    ), "dict_merge method requires at least two dicts to merge"
    merge_dicts = args[0:]
    rtn_dct = initial_dict.copy()
    for merge_dct in merge_dicts:
        for k, v in merge_dct.items():
            if not rtn_dct.get(k):
                rtn_dct[k] = v
            elif k in rtn_dct and type(v) != type(rtn_dct[k]) and not overwrite_existing:
                raise TypeError(
                    f"Overlapping keys exist with different types: original is {type(rtn_dct[k])}, new value is {type(v)}"
                )
            elif isinstance(rtn_dct[k], dict) and isinstance(
                merge_dct[k], collections.abc.Mapping
            ):
                rtn_dct[k] = dict_merge(
                    rtn_dct[k], merge_dct[k], overwrite_existing=overwrite_existing
                )
            elif isinstance(v, list):
                for list_value in v:
                    if list_value not in rtn_dct[k]:
                        rtn_dct[k].append(list_value)
            else:
                if overwrite_existing:
                    rtn_dct[k] = v
    return rtn_dct


def matlab_datenum_to_datetime(datenums) -> list:
    """
    Args:
        datenums (list or 1d np.array): Vector of matlab datenums.

    Returns:
        (list): List of dates in datetime format.
    """

    def datenum_to_datetime_scalar(datenum: float) -> datetime:
        """
        Convert Matlab datenum into Python datetime.

        Args:
             datenum (float): Date in datenum format

        Returns:
            Datetime object corresponding to datenum.

        Note: Be careful when you use this function or pd.to_datetime(datenum- 719529, unit='D') with half hourly data.
            it maybe that result come out incorrect due to rounding issues
        """
        # see http://sociograph.blogspot.com/2011/04/how-to-avoid-gotcha-when-converting.html
        # https://stackoverflow.com/questions/13965740/converting-matlabs-datenum-format-to-python/13965852#13965852

        datenum = float(datenum)
        days = datenum % 1
        datetime_obj = (
            datetime.fromordinal(int(datenum)) + timedelta(days=days) - timedelta(days=366)
        )
        if datetime_obj.second:
            raise ValueError("function can't deal with level of precision in datenum.")
        return datetime_obj

    return [datenum_to_datetime_scalar(x) for x in datenums]


def mc_to_year_month(mc: np.array) -> np.array:
    month = (mc - 1) % 12 + 1
    year = (mc - month) / 12 + 2000
    return year.astype(int), month.astype(int)


def date_to_mc(date):
    return (date.year - 2000) * 12 + date.month


def stop_model(msg: str = None, exception=Exception):
    """
    Stops the current model run and prints the user-input error. The error message is also stored
    in a Status.txt file so that PHP can display it in the front end.

    Args:
        msg (str): Error message.
        exception (Exception): Python exception (e.g. ValueError, ImportError, etc.).

    Raises:
        Exception: Raises the user-input exception and error message.
    """
    if msg is not None:
        with open("Status.txt", "w") as f:
            f.write(msg)
    raise exception(msg)


def add_to_log(message: str):
    """
    Short function to add a message and the message's timestamp to the log file RunLog.txt.

    Args:
        message (str): Message to add to the logs.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def send_email_notification(
    subject: str,
    message: list,
    sender: str,
    receivers: list,
    token: str,
    customer_name: str = "customer",
    server_name: str = None,
):
    """
    Function to send out an email notification to a specified list of receivers.

    Args:
        subject (str): Subject of the email.
        message (list): Body of the email, provided as a list of strings. A line break will be
            inserted after every item in the list. Use empty strings ("") to create blank lines.
        sender (str): Email address that will send the message.
        receivers (list): List of email addresses that will receive the message.
        token (str): Token to connect to the smtp server.
        customer_name (str): Name to append at the beginning of the message after "Dear";
            defaults to "customer" if not provided
        server_name (str): Name of the server to specify at the end of the message; defaults to
            None if not provided

    """

    # Add prefix to email subject
    subject = f"[Automatic Model Notification] {subject}"

    # Define beginning of the email
    body = f"Dear {customer_name},<br><br>"

    # Add user-defined lines to the email
    for line in message:
        body = f"{body}{line}<br>"

    # Add signature
    body = (
        f"{body}<br>"
        f"Best regards,<br>"
        f"KYOS Energy Analytics<br><br>"
        f"--<br>"
        f"KYOS Energy Analytics | Niewue Gracht 49 | 2011 ND Haarlem | the "
        f"Netherlands | T: +31 (0)23 5510221 | www.kyos.com<br>"
        f"--<br><br>"
    )

    # Add server name to signature if it exists.
    if server_name is None:
        # When the job is running on the server, the environment variable "PLATFORM_HOSTNAME"
        # (which is always set to the real server name when running the job locally) is
        # automatically set to "kyos-nginx" for all servers. For this reason, DevOps was asked
        # to add the real server name in the environment variables' list; they decided it will
        # be named "NGINX_HOST".
        server_name = os.getenv('NGINX_HOST')

    if server_name is None:
        end_of_signature = ""
    else:
        end_of_signature = f" on the server {server_name}"

    body = (
        f"{body}"
        f"<i>Note: This email was automatically generated by a KYOS model{end_of_signature}.</i>"
    )

    postmark = PostmarkClient(server_token=token)

    for receiver in receivers:
        postmark.emails.send(From=sender, To=receiver, Subject=subject, HtmlBody=body)
