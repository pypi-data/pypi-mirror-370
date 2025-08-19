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

import numpy as np

from pepflow import expression_manager as exm
from pepflow import function as fc
from pepflow import pep as pep


def test_function_repr():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        f = fc.Function(is_basis=True, reuse_gradient=False)
        print(f)  # it should be fine without tag
        f.add_tag("f")
        assert str(f) == "f"


def test_stationary_point():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=False, tags=["f"])
        f.add_stationary_point("x_star")

        assert len(ctx.triplets) == 1
        assert len(ctx.triplets[f]) == 1

        f_triplet = ctx.triplets[f][0]
        assert f_triplet.name == "x_star_f(x_star)_gradient_f(x_star)"
        assert f_triplet.gradient.tag == "gradient_f(x_star)"
        assert f_triplet.function_value.tag == "f(x_star)"

        em = exm.ExpressionManager(ctx)
        np.testing.assert_allclose(
            em.eval_point(f_triplet.gradient).vector, np.array([0])
        )
        np.testing.assert_allclose(em.eval_point(f_triplet.point).vector, np.array([1]))


def test_stationary_point_scaled():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=False, tags=["f"])
        g = 5 * f
        g.add_stationary_point("x_star")

        assert len(ctx.triplets) == 1
        assert len(ctx.triplets[f]) == 1

        f_triplet = ctx.triplets[f][0]
        assert f_triplet.name == "x_star_f(x_star)_gradient_f(x_star)"
        assert f_triplet.gradient.tag == "gradient_f(x_star)"
        assert f_triplet.function_value.tag == "f(x_star)"

        em = exm.ExpressionManager(ctx)
        np.testing.assert_allclose(
            em.eval_point(f_triplet.gradient).vector, np.array([0])
        )
        np.testing.assert_allclose(em.eval_point(f_triplet.point).vector, np.array([1]))


def test_stationary_point_additive():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=False)
        f.add_tag("f")
        g = fc.Function(is_basis=True, reuse_gradient=False)
        g.add_tag("g")
        h = f + g
        h.add_tag("h")

        h.add_stationary_point("x_star")
        assert len(ctx.triplets) == 2
        assert len(ctx.triplets[f]) == 1
        assert len(ctx.triplets[g]) == 1

        f_triplet = ctx.triplets[f][0]
        g_triplet = ctx.triplets[g][0]
        assert f_triplet.name == "x_star_f(x_star)_gradient_f(x_star)"
        assert g_triplet.name == "x_star_g(x_star)_gradient_g(x_star)"

        em = exm.ExpressionManager(ctx)
        np.testing.assert_allclose(
            em.eval_point(f_triplet.gradient).vector, np.array([0, 1])
        )
        np.testing.assert_allclose(
            em.eval_point(g_triplet.gradient).vector, np.array([0, -1])
        )


def test_stationary_point_linear_combination():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=False)
        f.add_tag("f")
        g = fc.Function(is_basis=True, reuse_gradient=False)
        g.add_tag("g")
        h = 3 * f + 2 * g
        h.add_tag("h")

        h.add_stationary_point("x_star")
        assert len(ctx.triplets) == 2
        assert len(ctx.triplets[f]) == 1
        assert len(ctx.triplets[g]) == 1

        f_triplet = ctx.triplets[f][0]
        g_triplet = ctx.triplets[g][0]
        assert f_triplet.name == "x_star_f(x_star)_gradient_f(x_star)"
        assert g_triplet.name == "x_star_g(x_star)_gradient_g(x_star)"

        em = exm.ExpressionManager(ctx)
        np.testing.assert_allclose(
            em.eval_point(f_triplet.gradient).vector, np.array([0, 1])
        )
        np.testing.assert_allclose(
            em.eval_point(g_triplet.gradient).vector, np.array([0, -1.5])
        )
