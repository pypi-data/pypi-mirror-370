import operator
import re
from typing import Any, Callable, List, Literal, Optional, Self, Union

import pandas as pd
from numpy import ndarray
from pandas import DataFrame, Series

from dakit.dtyping import Number


def tolist(obj, method=lambda x: [x], na=None):
    if obj is not None:
        if isinstance(obj, list):
            return obj
        else:
            return method(obj)
    return na if na is not None else []


def arg2pairs(*args):
    if len(args) % 2 != 0:
        raise RuntimeError('Invalid length of args.')
    return dict(zip(args[::2], args[1::2]))


class DataFrameManipulator(DataFrame):
    opmap = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        'in': Series.isin
    }

    def colmatch(self, pattern: str, **kwargs) -> List[str]:
        regex = re.compile(pattern, **kwargs)
        return [col for col in self.columns if regex.search(col)]

    def locmin(self, col: str) -> Self:
        return self[self[col] == self[col].min()]

    def locmax(self, col: str) -> Self:
        return self[self[col] == self[col].max()]

    def locnearest(self,
                col: str,
                value: Number,
                direction: Literal['left', 'right', None] = None) -> Self:
        if direction is None:
            diff = (self[col] - value).abs()
            return self[diff == diff.min()]
        
        elif direction == 'left':
            left_subset = self[self[col] <= value]
            if left_subset.empty:
                return self.iloc[:0]
            left_diff = (value - left_subset[col]).abs()
            return left_subset[left_diff == left_diff.min()]
        
        elif direction == 'right':
            right_subset = self[self[col] >= value]
            if right_subset.empty:
                return self.iloc[:0]
            right_diff = (right_subset[col] - value).abs()
            return right_subset[right_diff == right_diff.min()]
        
        else:
            raise ValueError(f"Invalid direction: '{direction}'. Use 'left', 'right' or None.")

    def coleq(self, col: str, val: Any) -> Self:
        return type(self)(self[self[col] == val])

    def loceq(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.coleq(col, val)
        return data

    def loc0(self, *args) -> Self:
        data = self
        for col in args:
            data = data.coleq(col, 0)
        return data

    def loc1(self, *args) -> Self:
        data = self
        for col in args:
            data = data.coleq(col, 1)
        return data

    def colne(self, col: str, val: Any) -> Self:
        return type(self)(self[self[col] != val])

    def locne(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colne(col, val)
        return data

    def colin(self, col: str, vals: list) -> Self:
        return type(self)(self[self[col].isin(vals)])

    def locin(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colin(col, val)
        return data

    def colnotin(self, col: str, vals: list) -> Self:
        return type(self)(self[~self[col].isin(vals)])

    def notin(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colnotin(col, val)
        return data

    def colge(self, col: str, val: float) -> Self:
        return type(self)(self[self[col] >= val])

    def locge(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colge(col, val)
        return data

    def colgt(self, col: str, val: float) -> Self:
        return type(self)(self[self[col] > val])

    def locgt(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colgt(col, val)
        return data

    def colle(self, col: str, val: float) -> Self:
        return type(self)(self[self[col] <= val])

    def locle(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.colle(col, val)
        return data

    def collt(self, col: str, val: float) -> Self:
        return type(self)(self[self[col] < val])

    def loclt(self, *args) -> Self:
        kv = arg2pairs(*args)  # dict
        data = self
        for col, val in kv.items():
            data = data.collt(col, val)
        return data

    def colbetween(
        self,
        col: str,
        left,
        right,
        inclusive: Literal['left', 'right', 'both',
                           'neither'] = 'both') -> Self:
        return type(self)(self[self[col].between(left,
                                                 right,
                                                 inclusive=inclusive)])

    def locbetween(
        self,
        col: str,
        left,
        right,
        inclusive: Literal['left', 'right', 'both',
                           'neither'] = 'both') -> Self:
        return type(self)(self[self[col].between(left,
                                                 right,
                                                 inclusive=inclusive)])

    locbt = locbetween

    def colna(self, col: str, na_vals=None) -> Self:
        return type(self)(self[self[col].isna()])

    locna = colna

    def narate(self, *cols) -> Union[float, dict]:
        if len(cols) == 1:
            return float(self[cols[0]].isna().mean())
        return {col: float(self[cols].isna().mean()) for col in cols}

    def loccontains(self,
                    col: str,
                    contains: str,
                    case: bool = False,
                    na=False,
                    **kwargs) -> Self:
        return type(self)(self[self[col].str.contains(contains,
                                                      case=case,
                                                      na=na,
                                                      **kwargs)])

    def reglike(self,
                col: str,
                pattern: str,
                case: bool = False,
                na=False,
                **kwargs) -> Self:
        return type(self)(self[self[col].str.contains(pattern,
                                                      case=case,
                                                      na=na,
                                                      regex=True,
                                                      **kwargs)])

    def locstartswith(self, col: str, prefix: str) -> Self:
        return type(self)(self[self[col].str.startswith(prefix)])

    def locendswith(self, col: str, suffix: str) -> Self:
        return type(self)(self[self[col].str.endswith(suffix)])

    def with_strftime(self, name: str, col: str, format: str) -> Self:
        ser = self[col] if pd.api.types.is_datetime64_any_dtype(
            self[col]) else pd.to_datetime(self[col])
        self[name] = ser.dt.strftime(format)
        return self

    def with_year_month_day(self,
                            name: str,
                            col: str,
                            format='%Y-%m-%d') -> Self:
        if format not in {'%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y%m%d'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_year_month(self, name: str, col: str, format='%Y-%m') -> Self:
        if format not in {
                '%Y%m', '%Y-%m', '%Y.%m', '%Y%b', '%Y%B', '%y%m', '%y%b',
                '%y%B'
        }:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_year_week(self, name: str, col: str, format='%Y%V') -> Self:
        """
        %U:Week number of the year (Sunday as the first day of the week) as a zero padded decimal number. 
        All days in a new year preceding the first Sunday are considered to be in week 0.
        %W:Week number of the year (Monday as the first day of the week) as a decimal number. 
        All days in a new year preceding the first Monday are considered to be in week 0.
        %V:ISO 8601 week as a decimal number with Monday as the first day of the week. 
        Week 01 is the week containing Jan 4.
        """
        if format not in {'%Y%V', '%Y%U', '%Y%W'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_year(self, name: str, col: str, format='%Y') -> Self:
        """
        %Y
        """
        if format not in {'%Y', '%y'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_weekday(self, name: str, col: str, format='%A') -> Self:
        """
        %Y
        """
        if format not in {'%A', '%a', '%w', '%u'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_day(self, name: str, col: str, format='%d') -> Self:
        """
        %Y
        """
        if format not in {'%d', '%j'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def with_hour(self, name: str, col: str, format='%H') -> Self:
        """
        %Y
        """
        if format not in {'%H', '%I', '%I %p'}:
            raise ValueError(f"Invalid format {format!r}.")
        return self.with_strftime(name, col, format=format)

    def retain(self, cols: list[str]) -> Self:
        return type(self)(self[cols])

    def find_unique_columns(self, strict: bool = True) -> list:
        if strict:
            return [c for c in self.columns if self[c].nunique() == len(self)]
        return [
            c for c in self.columns
            if self[c].dropna().nunique() == len(self[c].dropna())
        ]

    def find_uniform_columns(self, strict: bool = True) -> list:
        result_cols = []
        for col in self.columns:
            series = self[col]
            if series.isnull().all():
                result_cols.append(col)
            elif strict:
                if series.notnull().all() and series.nunique() == 1:
                    result_cols.append(col)
            else:
                if series.dropna().nunique() == 1:
                    result_cols.append(col)
        return result_cols

    def drop_uniform_columns(self,
                             strict: bool = True,
                             keep: Union[str, list] = None,
                             drop: Union[str, list] = None,
                             fillna=None) -> list:
        keepcols = []
        for col in self.columns:
            series = self[col]
            if series.isnull().all():
                continue
            elif strict:
                if series.dropna().nunique() == 1:
                    continue
                keepcols.append(col)
            else:
                if fillna:
                    series = series.fillna(fillna)
                    keepcols.append(col)
        if keep is not None:
            keepcols += [c for c in tolist(keep) if c not in keepcols]
        if drop is not None:
            keepcols = [c for c in keepcols if c not in tolist(drop)]
        return type(self)(self[keepcols])

    def find_nonuniform_columns(self, strict=True):
        uniform_or_allnull = self.find_uniform_columns(strict=strict)
        return [c for c in self.columns if c not in uniform_or_allnull]

    def nunique(self, *cols):
        if len(cols) == 1:
            return self[cols[0]].nunique()
        return {col: self[col].nunique() for col in cols}

    def uvalues(self, col: str, tolist=True) -> list:
        uvals = self[col].unique()
        if tolist:
            return uvals.tolist()
        return uvals

    def value_counts(self,
                     col: str,
                     with_pct: bool = True,
                     bins=None,
                     dropna=True,
                     reset_index: bool = True) -> Series:
        if with_pct:
            counts = self[col].value_counts(bins=bins, dropna=dropna)
            ratios = self[col].value_counts(normalize=True,
                                            bins=bins,
                                            dropna=dropna)
            result = DataFrame({'count': counts, 'ratio': ratios})
            if reset_index:
                result = result.reset_index()
            return type(self)(result)
        return self[col].value_counts()

    def top_value_counts(self,
                         col,
                         n=10,
                         r=None,
                         dropna=True,
                         digits: int = 2):
        vc = self[col].value_counts(dropna=dropna)
        total = vc.sum()
        prop = vc / total
        cum_prop = prop.cumsum()

        result = pd.DataFrame({
            col:
            vc.index,
            'count':
            vc.values,
            'percent': (prop.values * 100).round(digits),
            'cumpercent': (cum_prop.values * 100).round(digits)
        })
        if r is not None:
            mask = result['cumpercent'] < r * 100
            if not mask.any():
                mask.iloc[0] = True
            main_df = result[mask]
        else:
            main_df = result.iloc[:n]

        other_count = total - main_df['count'].sum()
        other_prop = 100 - main_df['percent'].sum()
        other_cum_prop = 100.0

        if other_count > 0:
            other_row = pd.DataFrame({
                col: ['Other'],
                'count': [other_count],
                'percent': [round(other_prop, 2)],
                'cumpercent': [other_cum_prop]
            })
            result_out = pd.concat([main_df, other_row], ignore_index=True)
        else:
            result_out = main_df.reset_index(drop=True)

        return result_out

    def vregmatch(self, col: str, pattern: str):
        uvals = self[col].dropna().unique()
        regex = re.compile(pattern)
        return [item for item in uvals if regex.search(str(item))]

    @property
    def preview(self):
        if len(self) > 5:
            return type(self)(pd.concat([self.head(3), self.tail(2)]))
        return self

    def exclude(self,
                index: Union[Series, ndarray] = None,
                conditions: list[tuple] = None):
        if index is not None:
            if isinstance(index, Series):
                return type(self)(self[~index])
            elif isinstance(index, ndarray):
                return type(self)(self.drop(index))
            else:
                raise ValueError(f"invalid value of `index`: {index}")
        if conditions is not None:
            if not (isinstance(conditions)
                    and all([isinstance(c, tuple) for c in conditions])):
                raise ValueError(
                    f"invalid value of `conditions`: {conditions}")
            data = self.copy()
            for col, op, value in conditions:
                cond = self.opmap[op](self[col], value)
                data = data[~cond]
            return type(self)(data)

    @classmethod
    def csv(cls, path, **kwargs):
        return cls(pd.read_csv(path, **kwargs))

    @classmethod
    def excel(cls, path, **kwargs):
        return cls(pd.read_excel(path, **kwargs))

    xlsx = excel

    @classmethod
    def pkl(cls, path, **kwargs):
        return cls(pd.read_pickle(path, **kwargs))

    def sortcols(self,
                 key: Optional[Callable[[Series], float]] = None,
                 ascending: bool = False) -> Self:
        if key is None:
            key = lambda s: s.mean()
        sortedcols = sorted(self.columns,
                            key=lambda col: key(self[col]),
                            reverse=not ascending)
        return type(self)(self[sortedcols])
