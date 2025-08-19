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

import functools

import numpy as np

from pepflow import pep_context as pc
from pepflow import point as pt
from pepflow import scalar as sc
from pepflow import utils


class ExpressionManager:
    def __init__(self, pep_context: pc.PEPContext):
        self.context = pep_context
        self._basis_points = []
        self._basis_point_uid_to_index = {}
        self._basis_scalars = []
        self._basis_scalar_uid_to_index = {}
        for point in self.context.points:
            if point.is_basis:
                self._basis_points.append(point)
                self._basis_point_uid_to_index[point.uid] = len(self._basis_points) - 1
        for scalar in self.context.scalars:
            if scalar.is_basis:
                self._basis_scalars.append(scalar)
                self._basis_scalar_uid_to_index[scalar.uid] = (
                    len(self._basis_scalars) - 1
                )

        self._num_basis_points = len(self._basis_points)
        self._num_basis_scalars = len(self._basis_scalars)

    def get_index_of_basis_point(self, point: pt.Point):
        return self._basis_point_uid_to_index[point.uid]

    def get_index_of_basis_scalar(self, scalar: sc.Scalar):
        return self._basis_scalar_uid_to_index[scalar.uid]

    @functools.cache
    def eval_point(self, point: pt.Point | float | int):
        if utils.is_numerical(point):
            return point

        array = np.zeros(self._num_basis_points)
        if point.is_basis:
            index = self.get_index_of_basis_point(point)
            array[index] = 1
            return pt.EvaluatedPoint(vector=array)

        op = point.eval_expression.op
        if op == utils.Op.ADD:
            return self.eval_point(point.eval_expression.left_point) + self.eval_point(
                point.eval_expression.right_point
            )
        if op == utils.Op.SUB:
            return self.eval_point(point.eval_expression.left_point) - self.eval_point(
                point.eval_expression.right_point
            )
        if op == utils.Op.MUL:
            return self.eval_point(point.eval_expression.left_point) * self.eval_point(
                point.eval_expression.right_point
            )
        if op == utils.Op.DIV:
            return self.eval_point(point.eval_expression.left_point) / self.eval_point(
                point.eval_expression.right_point
            )

        raise ValueError("This should never happen!")

    @functools.cache
    def eval_scalar(self, scalar: sc.Scalar | float | int):
        if utils.is_numerical(scalar):
            return scalar

        array = np.zeros(self._num_basis_scalars)
        if scalar.is_basis:
            index = self.get_index_of_basis_scalar(scalar)
            array[index] = 1
            return sc.EvaluatedScalar(
                vector=array,
                matrix=np.zeros((self._num_basis_points, self._num_basis_points)),
                constant=float(0.0),
            )
        op = scalar.eval_expression.op
        if op == utils.Op.ADD:
            return self.eval_scalar(
                scalar.eval_expression.left_scalar
            ) + self.eval_scalar(scalar.eval_expression.right_scalar)
        if op == utils.Op.SUB:
            return self.eval_scalar(
                scalar.eval_expression.left_scalar
            ) - self.eval_scalar(scalar.eval_expression.right_scalar)
        if op == utils.Op.MUL:
            if isinstance(scalar.eval_expression.left_scalar, pt.Point) and isinstance(
                scalar.eval_expression.right_scalar, pt.Point
            ):
                return sc.EvaluatedScalar(
                    vector=np.zeros(self._num_basis_scalars),
                    matrix=utils.SOP(
                        self.eval_point(scalar.eval_expression.left_scalar).vector,
                        self.eval_point(scalar.eval_expression.right_scalar).vector,
                    ),
                    constant=float(0.0),
                )
            else:
                return self.eval_scalar(
                    scalar.eval_expression.left_scalar
                ) * self.eval_scalar(scalar.eval_expression.right_scalar)
        if op == utils.Op.DIV:
            return self.eval_scalar(
                scalar.eval_expression.left_scalar
            ) / self.eval_scalar(scalar.eval_expression.right_scalar)

        raise ValueError("This should never happen!")
