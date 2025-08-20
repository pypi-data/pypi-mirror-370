from __future__ import annotations

import copy
import itertools
from numbers import Number
from typing import List, Dict

import pandas as pd
from sqlalchemy import create_engine, text

from .AggregateFunction import AggregateFunction
from .Attribute import Attribute
from .Axis import Axis
from .BaseCube import BaseCube
from .BooleanConnective import BooleanConnective
from .Hierarchy import Hierarchy
from .LevelMember import LevelMember
from .LevelMemberType import LevelMemberType
from .Measure import Measure
from .NonTopLevel import NonTopLevel
from .PredicateOperator import PredicateOperator

from .Predicate import Predicate
from ..engines.engine import Engine
from ..engines.postgres import Postgres
from ..timers import DBTimer


class View:
    def __init__(self,
                 axes: List[Axis] = None,
                 measures: List[Measure] = None,
                 predicates: Predicate = None,
                 cube: BaseCube = None,
                 name: str = "",
                 order_byes: list[tuple[Attribute, bool]] = None) -> None:
        self.axes: List[Axis] = axes if axes else []
        self._measures: List[Measure] = measures if measures else []
        self.predicates: Predicate = predicates if predicates else Predicate(None, "", None)
        self.cube: BaseCube = cube
        self.name: str = name
        self.order_byes: list[tuple[Attribute, bool]] = order_byes

    # Checks not implemented
    # All level members same
    def axis(self, ax: int, lms: List[LevelMember]) -> View:
        if not type(lms) is list: raise Exception("Level Member list must be a list")
        if not lms: raise Exception("Empty Level Member list")

        lm = lms[0]
        new_axis = Axis(lm.attribute.level.dimension, level=lm.attribute.level, attribute=lm.attribute,
                        level_member=lms)

        new_axes = copy.copy(self.axes)
        if len(self.axes) < ax + 1:
            new_axes = new_axes + [None] * (ax - len(self.axes) + 1)
            new_axes[ax] = new_axis
        else:
            new_axes[ax] = new_axis

        return View(axes=new_axes, measures=self._measures, predicates=self.predicates, cube=self.cube, name=self.name)


    def columns(self, lms: List[LevelMember]) -> View:
        return self.axis(0, lms)

    def rows(self, lms: List[LevelMember]) -> View:
        return self.axis(1, lms)

    def pages(self, lms: List[LevelMember]) -> View:
        return self.axis(2, lms)

    def sections(self, lms: List[LevelMember]) -> View:
        return self.axis(3, lms)

    def chapters(self, lms: List[LevelMember]) -> View:
        return self.axis(4, lms)

    def where(self, predicate: Predicate) -> View:
        return View(axes=self.axes, measures=self._measures, predicates=predicate, cube=self.cube, name=self.name)

    def using(self, *args: Measure, **kwargs: Dict[str, str | AggregateFunction]) -> View:
        measures = list(args)
        if kwargs:
            calculated_measures: List[Measure] = []
            for k, v in kwargs.items():
                calculated_measures.append(Measure(k, v["function"], v["sqlname"]))
            measures += calculated_measures
        return View(axes=self.axes, measures=measures, predicates=self.predicates, cube=self.cube, name=self.name)

    def order_by(self, *args: tuple[Attribute, bool]) -> View:
        if any([True for x in args if type(x[0]) is Measure]):
            raise Exception(f"Cannot use Measure in order_by: {args}")
        return View(axes=self.axes, measures=self._measures, predicates=self.predicates, cube=self.cube, name=self.name,
                    order_byes=list(args))

    @property
    def measures(self):
        return self.cube.measures

    @property
    def dimensions(self):
        return self.cube.dimensions

    def output(self) -> pd.DataFrame:
        if not all(self.axes):
            raise Exception(f"If axis n is specified then axis n - 1 must also be specified. Current specified axes {self.axes}")
        query: str = self._create_sql_query()
        result = self._convert_to_df(query)
        return result

    def __getattr__(self, item):
        return self.cube.__getattribute__(item)

    def _create_sql_query(self) -> str:
        from_clause: str = self._create_from_clause()
        select_clause: str = self._create_select_clause()
        where_clause: str = self._create_where_clause()
        group_by_clause: str = self._create_group_by_clause()
        # test: str = self._create_order_by_clause()
        return select_clause + " " + from_clause + " " + where_clause + " " + group_by_clause + ";"# " " + test + ";"

    def _create_select_clause(self) -> str:
        # levels: List[str] = list(map(lambda x: f"{x.level.alias}.{x.attribute.name} AS {x.level.alias}", self.axes))
        levels: List[str] = list(map(lambda x: f"{x[1].level.alias}.{x[1].level.key} AS {x[1].level.key}_{x[0]}, {x[1].level.alias}.{x[1].attribute.name} AS {x[1].level.alias}", enumerate(self.axes)))
        if self._measures:
            measures: List[str] = list(
                map(lambda x: f"{x.aggregate_function.name}({x.sqlname}) AS {x.name}", self._measures))
        else:
            measure: Measure = self._get_default_measure()
            measures: List[str] = [f"{measure.aggregate_function.name}({measure.sqlname}) AS {measure.name}"]
        if levels and measures:
            return "SELECT " + ", ".join(levels) + ", " + ", ".join(measures)
        if levels:
            return "SELECT " + ", ".join(levels)
        if measures:
            return "SELECT " + ", ".join(measures)
        else:
            return "SELECT "

    def _create_from_clause(self) -> str:
        subset_clauses: List[str] = []
        axis_lvls: List[NonTopLevel] = [x.level for x in self.axes]

        all_pred_lvls: List[NonTopLevel] = list(set(self._get_all_pred_levels(self.predicates)))
        pred_lvls: List[NonTopLevel] = [lvl for lvl in all_pred_lvls if lvl.dimension
                                        not in [x.dimension for x in axis_lvls]]

        for i, level in enumerate(axis_lvls + pred_lvls):
            subset_clauses.append(self._create_from_subset_clause(level, i))

        return f"FROM {self.cube.fact_table_name} " + " ".join(subset_clauses)

    def _get_all_pred_levels(self, pred: Predicate) -> List[NonTopLevel]:
        if isinstance(pred.value, Number):
            return []
        elif isinstance(pred.value, str):
            return []
        elif isinstance(pred.value, Measure):
            return []
        elif isinstance(pred.value, Attribute):
            return [pred.value.level]
        else:
            return self._get_all_pred_levels(pred.left_child) + self._get_all_pred_levels(pred.right_child)

    def _create_where_clause(self) -> str:
        axes: List[str] = self._create_axes_where_clause()
        axes: str = " AND ".join(axes) if axes else ""

        predicates: str = self._create_predicates_where_clause()
        if axes and predicates:
            return "WHERE " + axes + " AND " + predicates
        elif axes:
            return "WHERE " + axes
        elif predicates:
            return "WHERE " + predicates
        else:
            return ""

    def _create_group_by_clause(self) -> str:
        result: List[str] = []
        for x in self.axes:
            result.append(f"{x.level.alias}.{x.attribute.name}")
            result.append(f"{x.level.alias}.{x.level.key}")
        return "GROUP BY " + ", ".join(result) if result else ""

    def _create_order_by_clause(self) -> str:
        a: list[tuple[Attribute, bool]] = [(x.attribute, x.attribute.order_asc)
                                           for x in self.axes if x.attribute.order_by is not None]
        intermediary: list[tuple[Attribute, bool]] = [x for x in a if x[0] not in
                                                      [x[0] for x in self.order_byes]]
        order_byes: str = ", ".join([
            f"{attr.level.alias}.{attr.name} {'ASC' if asc else 'DESC'}"
            for attr, asc in self.order_byes + intermediary
        ])

        return "ORDER BY " + order_byes if order_byes else ""

    # def _make_values_key(self, df: pd.DataFrame, size: int) -> pd.DataFrame:
    #     if size < 1: return df
    #     key_cols = df.columns[:size:2]
    #     val_cols = df.columns[1:size:2]

    #     val_cols_count = df.groupby(val_cols.to_list()).size()
    #     val_cols_key = (val_cols_count == 1).all()
    #     new_val_cols = {}
    #     checked_columns = []
    #     while not val_cols_key:
    #         columns_to_check = [x for x in zip(val_cols, key_cols) if x[0] not in checked_columns]
    #         for val_col, key_col in columns_to_check:
    #             if (df.groupby(val_col).size() == 1).all():
    #                 continue
    #             else:
    #                 new_val_cols[val_col] = df[val_col].where(
    #                     df.groupby(val_col).size() == 1,
    #                     df[val_col].astype(str) + "_" + df[key_col].astype(str))
    #                 checked_columns.append(val_col)
    #                 break
    #         df = df.assign(**new_val_cols)
    #         val_cols_count = df.groupby(val_cols.to_list()).size()
    #         val_cols_key = (val_cols_count == 1).all()

    #     return df

    def _make_values_key(self, df: pd.DataFrame, size: int) -> pd.DataFrame:
        if size < 1: return df
        key_cols = df.columns[:size:2]
        val_cols = df.columns[1:size:2]

        val_cols_count = df.groupby(val_cols.to_list()).size()
        val_cols_key = (val_cols_count == 1).all()
        new_val_cols = {}
        from collections import deque
        columns_left = deque((x, y) for x, y in zip(key_cols, val_cols))
        while not val_cols_key:
            key_col, val_col = columns_left.popleft()
            new_val_cols[val_col] = df[val_col].where(
                df.groupby(val_col).size() == 1,
                df[val_col].astype(str) + "_" + df[key_col].astype(str))
            df = df.assign(**new_val_cols)
            val_cols_count = df.groupby(val_cols.to_list()).size()
            val_cols_key = (val_cols_count == 1).all()

        return df

    def _convert_to_df(self, query: str) -> pd.DataFrame:
        engine = create_engine(self._get_connection_string())
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, timer=DBTimer)
            columns = [ax.attribute.level.alias for ax in [ax for i, ax in enumerate(self.axes) if i % 2 == 0]]
            rows = [ax.attribute.level.alias for ax in [ax for i, ax in enumerate(self.axes) if i % 2 == 1]]
            measures = [m.name for m in self._measures]
            df = self._make_values_key(df, len(columns + rows) * 2)
            if not rows:
                row_id = "row_id"
                df[row_id] = 1
                rows = [row_id]
            if not measures:
                measures = [self._get_default_measure().name]

            df = df.pivot(columns=columns, index=rows, values=measures)

            if columns:
                df = df.reorder_levels(range(len(columns), -1, -1), axis=1)
                column_values = []
                for i in range(len(columns) + 1):
                    column_values.append(list(df.columns.get_level_values(i).unique()))
                new_column_idx = list(itertools.product(*column_values))
                valid_col_idx = [col for col in new_column_idx if col in df.columns]
                df = df.reindex(columns=valid_col_idx)
            if self.order_byes:
                ordering: list[tuple[int, int | None, bool]] = []
                for order in self.order_byes:
                    for idx, ax in enumerate(df.axes):
                        if isinstance(ax, pd.MultiIndex):
                            for nidx, name in enumerate(ax.names):
                                if name == order[0].level.alias:
                                    ordering.append((idx, nidx, order[1]))
                        elif isinstance(ax, pd.Index):
                            if ax.name == order[0].level.alias:
                                ordering.append((idx, None, order[1]))

                for order in ordering:
                    df.sort_index(axis=order[0], level=order[1], ascending=order[2], inplace=True)
        engine.dispose()
        return df

    def _create_axes_where_clause(self) -> List[str]:
        def format_level_members(a: Axis, lms: List[LevelMember]) -> str:
            if a.type == LevelMemberType.STR:
                return ", ".join(list(map(lambda x: f"'{x.name}'", lms)))
            elif a.type == LevelMemberType.INT:
                return ", ".join(list(map(lambda x: f"{x.name}", lms)))


        return list(
            map(lambda x: f"{x.level.alias}.{x.attribute.name} IN ({format_level_members(x, x.level_members)})",
                [x for x in self.axes if not len(x.attribute.level_members) == len(x.level_members)]))

        # return list(
        #     map(lambda x: f"{x.level.alias}.{x.attribute.name} IN ({format_level_members(x, x.level_members)})",
        #         [x for x in self.axes]))

    def _create_predicates_where_clause(self) -> str:
        pred_list: List[str] = self._create_predicates_where_clause_aux(self.predicates)
        return " ".join(pred_list)

    def _create_predicates_where_clause_aux(self, pred: Predicate) -> List[str]:
        if isinstance(pred.value, BooleanConnective):
            left_child: List[str] = self._create_predicates_where_clause_aux(pred.left_child)
            right_child: List[str] = self._create_predicates_where_clause_aux(pred.right_child)
            return ["("] + left_child + [pred.value.value] + right_child + [")"]
        elif isinstance(pred.value, PredicateOperator):
            left_child: List[str] = self._create_predicates_where_clause_aux(pred.left_child)
            right_child: List[str] = self._create_predicates_where_clause_aux(pred.right_child)
            return left_child + [pred.value.value] + right_child
        else:
            return [self._format_predicate_value(pred)]

    def _format_predicate_value(self, pred: Predicate) -> str:
        if isinstance(pred.value, Attribute):
            return f"{pred.value.level.alias}.{pred.value.name}"
        elif isinstance(pred.value, Measure):
            return f"{pred.value.sqlname}"
        elif isinstance(pred.value, str):
            return f"'{pred.value}'" if pred.value else ""
        elif isinstance(pred.value, int):
            return str(pred.value)

    def _create_from_subset_clause(self, level: NonTopLevel, counter: int) -> str:
        # The order in hierarchy is the lowest level first and highest last
        hierarchy: List[NonTopLevel] = self._get_children(level) + [level] + self._get_parents(level)
        try:
            result: List[str] = [
                self._create_on_condition_for_fact_table(self.cube.fact_table_name, hierarchy[0], counter)
            ]
            for i in range(len(hierarchy) - 1):
                result.append(self._create_on_condition(hierarchy[i], hierarchy[i + 1], counter))
        except IndexError as e:
            print(f"IndexError: {e}")
            return ""
        return "JOIN " + " JOIN ".join(result)

    def _create_on_condition_for_fact_table(self, fact_table: str, level: NonTopLevel, counter: int) -> str:
        level.alias = f"{level.name}{counter}"
        return f"{level.name} AS {level.alias} ON {fact_table}.{level.dimension.fact_table_fk} = {level.alias}.{level.key}"

    def _get_children(self, level: NonTopLevel) -> List[NonTopLevel]:
        result: List[NonTopLevel] = []
        while level != level.child:
            level: NonTopLevel = level.child
            result.append(level)
        return list(reversed(result))

    def _get_parents(self, level: NonTopLevel) -> List[NonTopLevel]:
        result: List[NonTopLevel] = []
        while level != level.parent:
            level = level.parent
            if isinstance(level, NonTopLevel):
                result.append(level)
        return list(result)

    def _create_on_condition(self, child: NonTopLevel, parent: NonTopLevel, counter: int) -> str:
        parent.alias = f"{parent.table_name}{counter}"
        return f"{parent.table_name} AS {parent.alias} ON {child.alias}.{child.fk_name} = {parent.alias}.{parent.key}"

    def _get_default_axes(self) -> list[Axis]:
        axes: List[Axis] = []
        for dimension in self.cube.dimensions():
            hierarchy: Hierarchy = dimension.hierarchies[0]
            level: NonTopLevel = hierarchy.lowest_level
            attribute: Attribute = level.level_member_attr
            level_members: List[LevelMember] = attribute.members()
            axes.append(Axis(dimension, hierarchy, level, attribute, level_members))
        return axes

    def _get_default_measure(self) -> Measure:
        return self.cube.measure_list[0] if self.cube.measure_list else None

    def _get_connection_string(self) -> str:
        engine: Engine = self.cube.engine
        match engine:
            case Postgres():
                return f"postgresql+psycopg2://{engine.user}:{engine.password}@{engine.host}/{engine.dbname}"
            case _:
                raise Exception(f"Unsupported engine {engine}")

    def __str__(self):
        return f"{self.name}"

