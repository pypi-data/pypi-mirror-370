# Copyright 2025 Eli Lilly and Company
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the `.sample_posterior_predictive()` method."""

from typing import TYPE_CHECKING

import pytest
from conftest import lm
from jax import random
from jax.typing import ArrayLike

from aimz.model import ImpactModel

if TYPE_CHECKING:
    from numpyro.infer import SVI


@pytest.mark.parametrize("vi", [lm], indirect=True)
class TestKernelParameterValidation:
    """Test class for validating parameter compatibility with the kernel."""

    def test_invalid_parameter(
        self,
        synthetic_data: tuple[ArrayLike, ArrayLike],
        vi: "SVI",
    ) -> None:
        """An invalid parameter raise an error."""
        X, y = synthetic_data
        im = ImpactModel(lm, rng_key=random.key(42), inference=vi)
        im.fit(X=X, y=y, batch_size=3)
        with pytest.raises(TypeError):
            im.sample_posterior_predictive(X=X, y=y)


@pytest.mark.parametrize("vi", [lm], indirect=True)
def test_sample_posterior_predictive_lm(
    synthetic_data: tuple[ArrayLike, ArrayLike],
    vi: "SVI",
) -> None:
    """Test the `.sample_posterior_predictive()` method of `ImpactModel`."""
    X, y = synthetic_data
    im = ImpactModel(lm, rng_key=random.key(42), inference=vi)
    im.fit(X=X, y=y, num_samples=99, batch_size=3)
    samples = im.sample_posterior_predictive(X=X)

    assert isinstance(samples, dict)
    assert samples["y"].shape == (99, len(X))
