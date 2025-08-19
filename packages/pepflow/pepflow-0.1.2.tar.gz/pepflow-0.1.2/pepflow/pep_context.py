# Copyright: 2025 The PEPFlow Developers
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import natsort
import pandas as pd

if TYPE_CHECKING:
    from pepflow.constraint import Constraint
    from pepflow.function import Function, Triplet
    from pepflow.point import Point
    from pepflow.scalar import Scalar

# A global variable for storing the current context that is used for points or scalars.
CURRENT_CONTEXT: PEPContext | None = None


def get_current_context() -> PEPContext | None:
    return CURRENT_CONTEXT


def set_current_context(ctx: PEPContext | None):
    global CURRENT_CONTEXT
    assert ctx is None or isinstance(ctx, PEPContext)
    CURRENT_CONTEXT = ctx


class PEPContext:
    def __init__(self):
        self.points: list[Point] = []
        self.scalars: list[Scalar] = []
        self.triplets: dict[Function, list[Triplet]] = defaultdict(list)
        self.opt_conditions: dict[Function, list[Constraint]] = defaultdict(list)

    def add_point(self, point: Point):
        self.points.append(point)

    def add_scalar(self, scalar: Scalar):
        self.scalars.append(scalar)

    def add_triplet(self, function: Function, triplet: Triplet):
        self.triplets[function].append(triplet)

    def add_opt_condition(self, function: Function, opt_condition: Constraint):
        self.opt_conditions[function].append(opt_condition)

    def get_by_tag(self, tag: str) -> Point | Scalar:
        for p in self.points:
            if p.tag == tag:
                return p
        for s in self.scalars:
            if s.tag == tag:
                return s
        raise ValueError("Cannot find the point or scalar of given tag")

    def clear(self):
        self.points.clear()
        self.scalars.clear()
        self.triplets.clear()
        self.opt_conditions.clear()

    def tracked_point(self, func: Function) -> list[Point]:
        return natsort.natsorted(
            [t.point for t in self.triplets[func]], key=lambda x: x.tag
        )

    def tracked_grad(self, func: Function) -> list[Point]:
        return natsort.natsorted(
            [t.gradient for t in self.triplets[func]], key=lambda x: x.tag
        )

    def tracked_func_value(self, func: Function) -> list[Scalar]:
        return natsort.natsorted(
            [t.function_value for t in self.triplets[func]], key=lambda x: x.tag
        )

    def order_of_point(self, func: Function) -> list[str]:
        return natsort.natsorted([t.point.tag for t in self.triplets[func]])

    def triplets_to_df_and_order(
        self,
    ) -> tuple[dict[Function, pd.DataFrame], dict[Function, list[str]]]:
        func_to_df: dict[Function, pd.DataFrame] = {}
        func_to_order: dict[Function, list[str]] = {}

        def name_to_point_tuple(c_name: str) -> list[str]:
            _, points = c_name.split(":")
            return points.split(",")

        for func, triplets in self.triplets.items():
            order = self.order_of_point(func)
            df = pd.DataFrame(
                [
                    (
                        constraint.name,
                        *name_to_point_tuple(constraint.name),
                    )
                    for constraint in func.get_interpolation_constraints(self)
                ],
                columns=["constraint_name", "col_point", "row_point"],
            )
            df["row"] = df["row_point"].map(lambda x: order.index(x))
            df["col"] = df["col_point"].map(lambda x: order.index(x))
            func_to_df[func] = df
            func_to_order[func] = order

        return func_to_df, func_to_order
