import copy
import datetime
import decimal
import functools
import json
import re
import warnings
import xml.etree.ElementTree as ET
from functools import reduce
from io import BytesIO
from sys import getsizeof
from typing import Any, Dict, Union

str_default_date = "%Y-%m-%dT%H:%M:%S"


class ReachDateUtils:
    @staticmethod
    def chunk_date_range(start_date, end_date, days_per_chunk):
        """
        Divides the interval between start_date and end_date into blocks of days_to_request days.
        Returns a list of tuples, each representing a date range.
        Each new range starts the day after the end of the previous range.
        """
        ranges = []
        current_start_date = start_date

        while current_start_date < end_date:
            current_end_date = current_start_date + datetime.timedelta(
                days=days_per_chunk - 1
            )

            # Ensure that the final interval does not exceed end_date
            if current_end_date > end_date:
                current_end_date = end_date
            ranges.append((current_start_date, current_end_date))

            # Updating current_start_date to the day after current_end_date
            current_start_date = current_end_date + datetime.timedelta(days=1)

        return ranges

    @staticmethod
    def convert_datetime_to_isoformat(obj: Union[Dict[str, Any], list]):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, datetime.datetime):
                    obj[key] = value.isoformat()
                elif isinstance(value, dict):
                    ReachDateUtils.convert_datetime_to_isoformat(value)
                elif isinstance(value, list):
                    for item in value:
                        ReachDateUtils.convert_datetime_to_isoformat(item)
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                if isinstance(item, datetime.datetime):
                    obj[index] = item.isoformat()
                elif isinstance(item, dict):
                    ReachDateUtils.convert_datetime_to_isoformat(item)
                elif isinstance(item, list):
                    ReachDateUtils.convert_datetime_to_isoformat(item)
        return obj

    @staticmethod
    def date_to_str(date: datetime, strf_format: str = None) -> str:
        return date.strftime(strf_format or str_default_date)

    @staticmethod
    def str_to_date(date: str, strf_format: str = None) -> datetime:
        return datetime.datetime.strptime(date, strf_format or str_default_date)


class ReachChunkObjectsUtils:
    MAX_FIREHOSE_SIZE = 900000

    @staticmethod
    def set_dict_value(obj, path, value):
        """

        :param obj: root object
        :param path:
        :param value:
        :return:
        """
        *path, last = path.split(".")
        for bit in path:
            obj = obj.setdefault(bit, {})
        obj[last] = value

    @staticmethod
    def chunk_list_items(
        obj_to_split: dict, path_of_array: str, max_size=MAX_FIREHOSE_SIZE
    ) -> list:
        """
        Function created to split a dict into smaller dict's, keeping the properties default.
        :param obj_to_split: root object to split.
        :param path_of_array: array path, separated by dots.
        :param max_size: maximum size in bytes to each
        :return: list
        """
        if path_of_array:
            map_list = path_of_array.split(".")
            edges = reduce(
                lambda d, key: d.get(key) if isinstance(d, dict) else None,
                map_list,
                obj_to_split,
            )
            if not edges:
                edges = [obj_to_split]
                path_of_array = None
        elif isinstance(obj_to_split, list):
            edges = obj_to_split
        else:
            raise Exception("path_of_array cannot be None for dict")
        list_of_items = []
        current_items = []
        for elem in edges:
            current_items.append(elem)

            if len(json.dumps(current_items).encode("utf-8")) >= max_size:
                current_edge = copy.deepcopy(obj_to_split)
                if path_of_array:
                    ReachChunkObjectsUtils.set_dict_value(
                        current_edge, path_of_array, current_items
                    )
                list_of_items.append(current_edge)
                current_items = []
        if current_items:
            current_edge = copy.deepcopy(obj_to_split)
            if path_of_array:
                ReachChunkObjectsUtils.set_dict_value(
                    current_edge, path_of_array, current_items
                )
            list_of_items.append(current_edge)
        return list_of_items

    @staticmethod
    def chunk_xml_by_tag(content: str, header: str, footer: str, tag_name):
        context = ET.iterparse(BytesIO(content.encode("utf-8")))
        list_xml = []

        for event, elem in context:
            if elem.tag in tag_name:
                list_xml.append(
                    f"{header}{ET.tostring(elem, encoding='unicode')}{footer}"
                )
        return list_xml

    @staticmethod
    def chunk_xml(content: str, header: str, footer: str, tag_name, max_size):
        context = ET.iterparse(BytesIO(content.encode("utf-8")))
        list_xml = []

        current_xml: str = ""
        for event, elem in context:
            if elem.tag in tag_name:
                current_xml += ET.tostring(elem, encoding="unicode")
            if getsizeof(current_xml) >= max_size:
                list_xml.append(f"{header}{current_xml}{footer}")
                current_xml = ""
        if not list_xml:
            list_xml.append(f"{header}{current_xml}{footer}")
            current_xml = ""
        if current_xml:
            list_xml.append(f"{header}{current_xml}{footer}")
        return list_xml

    @staticmethod
    def split_list_into_chunks(items, chunk_size):
        list_of_chunks = []
        for i in range(0, len(items), chunk_size):
            list_of_chunks.append(items[i : i + chunk_size])
        return list_of_chunks


def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                f"{func.__name__} está obsoleta: {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func(*args, **kwargs)

        return new_func

    return decorator


def remove_nulls(data):
    if isinstance(data, dict):
        return {k: remove_nulls(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nulls(item) for item in data if item is not None]
    else:
        return data


def build_update_params_for_attributes(attributes_to_update):
    """
    Constructs the parameters needed for an update operation in DynamoDB, specifically
    for the provided attributes. It handles reserved words by using attribute name aliases.

    :param attributes_to_update: A dictionary containing the attribute names and their new values.
    :return: A tuple containing the UpdateExpression, ExpressionAttributeValues, and
             ExpressionAttributeNames for the update operation.
    """
    update_expression = "SET " + ", ".join(
        f"#{k} = :val{k}" for k in attributes_to_update.keys()
    )

    expression_attribute_values = {
        f":val{k}": v for k, v in attributes_to_update.items()
    }

    expression_attribute_names = {f"#{k}": k for k in attributes_to_update.keys()}

    return update_expression, expression_attribute_values, expression_attribute_names


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)


def is_valid_email(v):
    import re

    regex = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.match(regex, v)


def clean_phone_number(phone_number):
    return re.sub(r"\D", "", phone_number)
