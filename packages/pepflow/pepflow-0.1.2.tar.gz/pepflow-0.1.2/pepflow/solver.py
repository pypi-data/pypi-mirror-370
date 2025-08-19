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

import warnings

import cvxpy

from pepflow import constants
from pepflow import constraint as ctr
from pepflow import expression_manager as exm
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils

warnings.filterwarnings(
    "ignore",
    message=".*compressed sparse column.*",
    category=UserWarning,
)


def evaled_scalar_to_cvx_express(
    eval_scalar: sc.EvaluatedScalar, vec_var: cvxpy.Variable, matrix_var: cvxpy.Variable
) -> cvxpy.Expression:
    return (
        vec_var @ eval_scalar.vector
        + cvxpy.trace(matrix_var @ eval_scalar.matrix)
        + eval_scalar.constant
    )


class DualVariableManager:
    def __init__(self, named_constraints: list[tuple[str, cvxpy.Constraint]]):
        self.named_constraints = {}
        for name, c in named_constraints:
            self.add_constraint(name, c)

    def cvx_constraints(self) -> list[cvxpy.Constraint]:
        return list(self.named_constraints.values())

    def clear(self) -> None:
        self.named_constraints.clear()

    def add_constraint(self, name: str, constraint: cvxpy.Constraint) -> None:
        if name in self.named_constraints:
            raise KeyError(f"There is already a constraint named {name}")
        self.named_constraints[name] = constraint

    def dual_value(self, name: str) -> float | None:
        if name not in self.named_constraints:
            return None  # Is this good choice?
        dual_value = self.named_constraints[name].dual_value
        if dual_value is None:
            return None
        return dual_value


class CVXSolver:
    def __init__(
        self,
        perf_metric: sc.Scalar,
        constraints: list[ctr.Constraint],
        context: pc.PEPContext,
    ):
        self.perf_metric = perf_metric
        self.constraints = constraints
        self.dual_var_manager = DualVariableManager([])
        self.context = context

    def build_problem(self) -> cvxpy.Problem:
        em = exm.ExpressionManager(self.context)
        f_var = cvxpy.Variable(em._num_basis_scalars)
        g_var = cvxpy.Variable(
            (em._num_basis_points, em._num_basis_points), symmetric=True
        )

        # Evaluate all poiints and scalars in advance to store it in cache.
        for point in self.context.points:
            em.eval_point(point)
        for scalar in self.context.scalars:
            em.eval_scalar(scalar)

        self.dual_var_manager.clear()
        self.dual_var_manager.add_constraint(constants.PSD_CONSTRAINT, g_var >> 0)
        for c in self.constraints:
            exp = evaled_scalar_to_cvx_express(em.eval_scalar(c.scalar), f_var, g_var)
            if c.comparator == utils.Comparator.GT:
                self.dual_var_manager.add_constraint(c.name, exp >= 0)
            elif c.comparator == utils.Comparator.LT:
                self.dual_var_manager.add_constraint(c.name, exp <= 0)
            elif c.comparator == utils.Comparator.EQ:
                self.dual_var_manager.add_constraint(c.name, exp == 0)
            else:
                raise ValueError(f"Unknown comparator {c.comparator}")

        obj = evaled_scalar_to_cvx_express(
            em.eval_scalar(self.perf_metric), f_var, g_var
        )

        return cvxpy.Problem(
            cvxpy.Maximize(obj), self.dual_var_manager.cvx_constraints()
        )

    def solve(self, **kwargs):
        problem = self.build_problem()
        result = problem.solve(**kwargs)
        return result
