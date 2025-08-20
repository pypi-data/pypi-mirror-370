# coding=utf-8

import types
import csv as PyCsv

from typing import Any
TyAny = Any
TyArr = list[Any]
TyAoA = list[TyArr]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPath = str


class Csv:

    @staticmethod
    def write_from_aoa(
            aoa: TyAoA, path_: TyPath, keys_: TyArr, **kwargs) -> None:
        _kwargs = {}
        _kwargs['quotechar'] = kwargs.get('quote', '"')
        _kwargs['quoting'] = PyCsv.QUOTE_NONNUMERIC
        _kwargs['delimiter'] = kwargs.get('delimiter', ',')
        with open(path_, 'w') as fd:
            writer = PyCsv.writer(fd, **_kwargs)
            writer.writerow(keys_)
            for arr in aoa:
                writer.writerow(arr)

    @staticmethod
    def write_from_aod(
            aod: TyAoD, path: str, **kwargs) -> None:
        fieldnames = kwargs.pop('fieldnames', None)
        _kwargs = {}
        _kwargs['quotechar'] = kwargs.get('quote', '"')
        _kwargs['quoting'] = PyCsv.QUOTE_NONNUMERIC
        _kwargs['delimiter'] = kwargs.get('delimiter', ',')
        if isinstance(aod, types.GeneratorType):
            if fieldnames is None:
                aod_first = next(aod, None)
                _kwargs['fieldnames'] = aod_first.keys()
                with open(path, 'w') as fd:
                    writer = PyCsv.DictWriter(fd, **_kwargs)
                    writer.writeheader()
                    writer.writerow(aod_first)
                    writer.writerows(aod)
            else:
                _kwargs['fieldnames'] = fieldnames
                with open(path, 'w') as fd:
                    writer = PyCsv.DictWriter(fd, **_kwargs)
                    writer.writeheader()
                    writer.writerows(aod)
        else:
            aod_first = aod[0]
            _kwargs['fieldnames'] = aod_first.keys()
            with open(path, 'w') as fd:
                writer = PyCsv.DictWriter(fd, **_kwargs)
                writer.writeheader()
                writer.writerows(aod)

    @staticmethod
    def write_from_dic(dic: TyDic, path_: TyPath, keys_: TyArr, **kwargs) -> None:
        _kwargs = {}
        _kwargs['quotechar'] = kwargs.get('quote', '"')
        _kwargs['quoting'] = PyCsv.QUOTE_NONNUMERIC
        _kwargs['delimiter'] = kwargs.get('delimiter', ',')
        with open(path_, 'w') as fd:
            writer = PyCsv.writer(fd, **_kwargs)
            writer.writerow(keys_)
            writer.writerow(dic.values())

    @staticmethod
    def read_2_aod(
            path: TyPath, **kwargs):
        mode = kwargs.get('mode', 'r')
        delimiter = kwargs.get('delimiter', ',')
        quote = kwargs.get('quote', '"')
        with open(path, mode) as fd:
            aod = PyCsv.DictReader(
                fd,
                delimiter=delimiter,
                quotechar=quote
            )
            return aod
        return []

    @staticmethod
    def read_2_arr(
            path: TyPath, **kwargs):
        mode = kwargs.get('mode', 'r')
        delimiter = kwargs.get('delimiter', ',')
        quote = kwargs.get('quote', '"')
        with open(path, mode) as fd:
            reader = PyCsv.reader(
                fd,
                delimiter=delimiter,
                quotechar=quote
            )
            arr = []
            for row in reader:
                arr.append(row)
            return arr

        return []

    @classmethod
    def read_2_dic(
            cls, path: TyPath, **kwargs):
        obj = cls.read_2_arr(path, **kwargs)
        dic = {}
        if isinstance(obj, (tuple, list)):
            for item in obj:
                if isinstance(item, (tuple, list)) and len(item) == 2:
                    key = item[0]
                    value = item[1]
                    dic[key] = value
        else:
            return obj
        return dic

    @staticmethod
    def read_header_to_arr(
            path: TyPath, **kwargs):
        mode = kwargs.get('mode', 'r')
        delimiter = kwargs.get('delimiter', ',')
        quote = kwargs.get('quote', '"')
        with open(path, mode) as fd:
            reader = PyCsv.reader(
                fd,
                delimiter=delimiter,
                quotechar=quote
            )
            header = next(reader)
            return header
        return []
