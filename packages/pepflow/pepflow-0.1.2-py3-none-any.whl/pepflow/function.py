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

import attrs

from pepflow import pep_context as pc
from pepflow import point as pt
from pepflow import scalar as sc
from pepflow import utils


@attrs.frozen
class Triplet:
    point: pt.Point
    function_value: sc.Scalar
    gradient: pt.Point
    name: str | None
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)


@attrs.frozen
class AddedFunc:
    """Represents left_func + right_func."""

    left_func: Function
    right_func: Function


@attrs.frozen
class ScaledFunc:
    """Represents scale * base_func."""

    scale: float
    base_func: Function


@attrs.mutable
class Function:
    is_basis: bool
    reuse_gradient: bool

    composition: AddedFunc | ScaledFunc | None = None

    # Human tagged value for the function
    tags: list[str] = attrs.field(factory=list)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.composition is None
        else:
            assert self.composition is not None

    @property
    def tag(self):
        if len(self.tags) == 0:
            raise ValueError("Function should have a name.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

    def __repr__(self):
        if self.tags:
            return self.tag
        return super().__repr__()

    def get_interpolation_constraints(self):
        raise NotImplementedError(
            "This method should be implemented in the children class."
        )

    def add_triplet_to_func(self, triplet: Triplet) -> None:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.triplets[self].append(triplet)

    def add_point_with_grad_restriction(
        self, point: pt.Point, desired_grad: pt.Point
    ) -> Triplet:
        # todo find a better tagging approach.
        if self.is_basis:
            function_value = sc.Scalar(is_basis=True)
            function_value.add_tag(f"{self.tag}({point.tag})")
            triplet = Triplet(
                point,
                function_value,
                desired_grad,
                name=f"{point.tag}_{function_value.tag}_{desired_grad.tag}",
            )
            self.add_triplet_to_func(triplet)
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                next_desired_grad = desired_grad - left_triplet.gradient
                next_desired_grad.add_tag(
                    f"gradient_{self.composition.right_func.tag}({point.tag})"
                )
                right_triplet = (
                    self.composition.right_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    left_triplet.function_value + right_triplet.function_value,
                    desired_grad,
                    name=f"{point.tag}_{self.tag}_{desired_grad.tag}",
                )
            elif isinstance(self.composition, ScaledFunc):
                next_desired_grad = desired_grad / self.composition.scale
                next_desired_grad.add_tag(
                    f"gradient_{self.composition.base_func.tag}({point.tag})"
                )
                base_triplet = (
                    self.composition.base_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    base_triplet.function_value * self.composition.scale,
                    desired_grad,
                    name=f"{point.tag}_{self.tag}_{desired_grad.tag}",
                )
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )
        return triplet

    def add_stationary_point(self, name: str) -> pt.Point:
        # assert we can only add one stationary point?
        point = pt.Point(is_basis=True)
        point.add_tag(name)
        desired_grad = 0 * point
        desired_grad.add_tag(f"gradient_{self.tag}({name})")
        self.add_point_with_grad_restriction(point, desired_grad)
        return point

        # The following the old gradient(opt) =  0 constraint style.
        # It is mathamatically correct but hard for solver so we abandon it.
        #
        # triplet = self.generate_triplet(point)
        # pep_context = pc.get_current_context()
        # pep_context.add_opt_condition(
        #     self,
        #     ((triplet.gradient) ** 2).eq(
        #         0, name=f"{self.tags[0]}({point.tags[0]}) optimality condition"
        #     ),
        # )
        # return point

    def generate_triplet(self, point: pt.Point) -> Triplet:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")

        if self.is_basis:
            generate_new_basis = True
            instances_of_point = 0
            for triplet in pep_context.triplets[self]:
                if triplet.point.uid == point.uid:
                    instances_of_point += 1
                    generate_new_basis = False
                    previous_triplet = triplet

            if generate_new_basis:
                function_value = sc.Scalar(is_basis=True)
                function_value.add_tag(f"{self.tag}({point.tag})")
                gradient = pt.Point(is_basis=True)
                gradient.add_tag(f"gradient_{self.tag}({point.tag})")

                new_triplet = Triplet(
                    point,
                    function_value,
                    gradient,
                    name=f"{point.tag}_{function_value.tag}_{gradient.tag}",
                )
                self.add_triplet_to_func(new_triplet)
            elif not generate_new_basis and self.reuse_gradient:
                function_value = previous_triplet.function_value
                gradient = previous_triplet.gradient
            elif not generate_new_basis and not self.reuse_gradient:
                function_value = previous_triplet.function_value
                gradient = pt.Point(is_basis=True)
                gradient.add_tag(f"gradient_{self.tag}({point.tag})")

                new_triplet = Triplet(
                    point,
                    previous_triplet.function_value,
                    gradient,
                    name=f"{point.tag}_{function_value.tag}_{gradient.tag}_{instances_of_point}",
                )
                self.add_triplet_to_func(new_triplet)
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                right_triplet = self.composition.right_func.generate_triplet(point)
                function_value = (
                    left_triplet.function_value + right_triplet.function_value
                )
                gradient = left_triplet.gradient + right_triplet.gradient
            elif isinstance(self.composition, ScaledFunc):
                base_triplet = self.composition.base_func.generate_triplet(point)
                function_value = self.composition.scale * base_triplet.function_value
                gradient = self.composition.scale * base_triplet.gradient
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )

        return Triplet(point, function_value, gradient, name=None)

    def gradient(self, point: pt.Point) -> pt.Point:
        triplet = self.generate_triplet(point)
        return triplet.gradient

    def subgradient(self, point: pt.Point) -> pt.Point:
        triplet = self.generate_triplet(point)
        return triplet.gradient

    def function_value(self, point: pt.Point) -> sc.Scalar:
        triplet = self.generate_triplet(point)
        return triplet.function_value

    def __add__(self, other):
        assert isinstance(other, Function)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient and other.reuse_gradient,
            composition=AddedFunc(self, other),
            tags=[f"{self.tag}+{other.tag}"],
        )

    def __sub__(self, other):
        assert isinstance(other, Function)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient and other.reuse_gradient,
            composition=AddedFunc(self, -other),
            tags=[f"{self.tag}-{other.tag}"],
        )

    def __mul__(self, other):
        assert utils.is_numerical(other)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[f"{other:.4g}*{self.tag}"],
        )

    def __rmul__(self, other):
        assert utils.is_numerical(other)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[f"{other:.4g}*{self.tag}"],
        )

    def __neg__(self):
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=ScaledFunc(scale=-1, base_func=self),
            tags=[f"-{self.tag}"],
        )

    def __truediv__(self, other):
        assert utils.is_numerical(other)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=ScaledFunc(scale=1 / other, base_func=self),
            tags=[f"1/{other:.4g}*{self.tag}"],
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return self.uid == other.uid


class SmoothConvexFunction(Function):
    def __init__(self, L, is_basis=True, composition=None, reuse_gradient=True):
        super().__init__(
            is_basis=is_basis, composition=composition, reuse_gradient=reuse_gradient
        )
        self.L = L

    def smooth_convex_interpolability_constraints(self, triplet_i, triplet_j):
        point_i = triplet_i.point
        function_value_i = triplet_i.function_value
        grad_i = triplet_i.gradient

        point_j = triplet_j.point
        function_value_j = triplet_j.function_value
        grad_j = triplet_j.gradient

        func_diff = function_value_j - function_value_i
        cross_term = grad_j * (point_i - point_j)
        quad_term = 1 / (2 * self.L) * (grad_i - grad_j) ** 2

        return (func_diff + cross_term + quad_term).le(
            0, name=f"{self.tag}:{point_i.tag},{point_j.tag}"
        )

    def get_interpolation_constraints(self, pep_context: pc.PEPContext | None = None):
        interpolation_constraints = []
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        for i in pep_context.triplets[self]:
            for j in pep_context.triplets[self]:
                if i == j:
                    continue
                interpolation_constraints.append(
                    self.smooth_convex_interpolability_constraints(i, j)
                )
        return interpolation_constraints
