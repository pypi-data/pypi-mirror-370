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

import uuid
from typing import TYPE_CHECKING, Any

import attrs
import numpy as np

from pepflow import constraint as ctr
from pepflow import pep_context as pc
from pepflow import utils

if TYPE_CHECKING:
    from pepflow.point import Point


def is_numerical_or_scalar(val: Any) -> bool:
    return utils.is_numerical(val) or isinstance(val, Scalar)


def is_numerical_or_evaluatedscalar(val: Any) -> bool:
    return utils.is_numerical(val) or isinstance(val, EvaluatedScalar)


@attrs.frozen
class EvalExpressionScalar:
    op: utils.Op
    left_scalar: Point | Scalar | float
    right_scalar: Point | Scalar | float


@attrs.frozen
class EvaluatedScalar:
    vector: np.ndarray
    matrix: np.ndarray
    constant: float

    def __add__(self, other):
        assert is_numerical_or_evaluatedscalar(other)
        if utils.is_numerical(other):
            return EvaluatedScalar(
                vector=self.vector, matrix=self.matrix, constant=self.constant + other
            )
        else:
            return EvaluatedScalar(
                vector=self.vector + other.vector,
                matrix=self.matrix + other.matrix,
                constant=self.constant + other.constant,
            )

    def __radd__(self, other):
        assert is_numerical_or_evaluatedscalar(other)
        if utils.is_numerical(other):
            return EvaluatedScalar(
                vector=self.vector, matrix=self.matrix, constant=other + self.constant
            )
        else:
            return EvaluatedScalar(
                vector=other.vector + self.vector,
                matrix=other.matrix + self.matrix,
                constant=other.constant + self.constant,
            )

    def __sub__(self, other):
        assert is_numerical_or_evaluatedscalar(other)
        if utils.is_numerical(other):
            return EvaluatedScalar(
                vector=self.vector, matrix=self.matrix, constant=self.constant - other
            )
        else:
            return EvaluatedScalar(
                vector=self.vector - other.vector,
                matrix=self.matrix - other.matrix,
                constant=self.constant - other.constant,
            )

    def __rsub__(self, other):
        assert is_numerical_or_evaluatedscalar(other)
        if utils.is_numerical(other):
            return EvaluatedScalar(
                vector=-self.vector, matrix=-self.matrix, constant=other - self.constant
            )
        else:
            return EvaluatedScalar(
                vector=other.vector - self.vector,
                matrix=other.matrix - self.matrix,
                constant=other.constant - self.constant,
            )

    def __mul__(self, other):
        assert utils.is_numerical(other)
        return EvaluatedScalar(
            vector=self.vector * other,
            matrix=self.matrix * other,
            constant=self.constant * other,
        )

    def __rmul__(self, other):
        assert utils.is_numerical(other)
        return EvaluatedScalar(
            vector=other * self.vector,
            matrix=other * self.matrix,
            constant=other * self.constant,
        )

    def __neg__(self):
        return self.__rmul__(other=-1)

    def __truediv__(self, other):
        assert utils.is_numerical(other)
        return EvaluatedScalar(
            vector=self.vector / other,
            matrix=self.matrix / other,
            constant=self.constant / other,
        )


@attrs.frozen
class Scalar:
    # If true, the scalar is the basis for the evaluations of F
    is_basis: bool

    # Not sure on this yet
    eval_expression: EvalExpressionScalar | None = None

    # Human tagged value for the scalar
    tags: list[str] = attrs.field(factory=list)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.eval_expression is None
        else:
            assert self.eval_expression is not None

        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_scalar(self)

    @property
    def tag(self):
        if len(self.tags) == 0:
            raise ValueError("Scalar should have a name.")
        return self.tags[-1]

    def add_tag(self, tag: str):
        self.tags.append(tag)

    def __repr__(self):
        if self.tags:
            return self.tag
        return super().__repr__()

    def __add__(self, other):
        assert is_numerical_or_scalar(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.ADD, self, other),
        )

    def __radd__(self, other):
        assert is_numerical_or_scalar(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.ADD, other, self),
        )

    def __sub__(self, other):
        assert is_numerical_or_scalar(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.SUB, self, other),
        )

    def __rsub__(self, other):
        assert is_numerical_or_scalar(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.SUB, other, self),
        )

    def __mul__(self, other):
        assert utils.is_numerical(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.MUL, self, other),
        )

    def __rmul__(self, other):
        assert utils.is_numerical(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.MUL, other, self),
        )

    def __neg__(self):
        return self.__rmul__(other=-1)

    def __truediv__(self, other):
        assert utils.is_numerical(other)
        return Scalar(
            is_basis=False,
            eval_expression=EvalExpressionScalar(utils.Op.DIV, self, other),
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Scalar):
            return NotImplemented
        return self.uid == other.uid

    def le(self, other, name: str) -> ctr.Constraint:
        return ctr.Constraint(self - other, comparator=utils.Comparator.LT, name=name)

    def lt(self, other, name: str) -> ctr.Constraint:
        return ctr.Constraint(self - other, comparator=utils.Comparator.LT, name=name)

    def ge(self, other, name: str) -> ctr.Constraint:
        return ctr.Constraint(self - other, comparator=utils.Comparator.GT, name=name)

    def gt(self, other, name: str) -> ctr.Constraint:
        return ctr.Constraint(self - other, comparator=utils.Comparator.GT, name=name)

    def eq(self, other, name: str) -> ctr.Constraint:
        return ctr.Constraint(self - other, comparator=utils.Comparator.EQ, name=name)
