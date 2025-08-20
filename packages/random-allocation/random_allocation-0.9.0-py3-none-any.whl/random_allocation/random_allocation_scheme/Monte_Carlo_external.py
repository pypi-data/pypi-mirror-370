#######################################################################
# This file was coppied from the google-research/dpsgd_batch_sampler_accounting/ git project
# (https://github.com/google-research/google-research/tree/master/dpsgd_batch_sampler_accounting),
# and includes code from the files; dpsgd_bounds, monte_carlo_estimator, and balls_and_bins,
# which was done in order to allow comparison in our plots.
#######################################################################



# coding=utf-8
# Copyright 2024 The Google Research Authors.
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

"""Computes bounds for DP-SGD with various batch samplers.

The source in this file is based on the following papers:

Title: How Private are DP-SGD implementations?
Authors: Lynn Chua, Badih Ghazi, Pritish Kamath, Ravi Kumar, Pasin Manurangsi,
         Amer Sinha, Chiyuan Zhang
Link: https://arxiv.org/abs/2403.17673

Title: Scalable DP-SGD: Shuffling vs. Poisson Subsampling
Authors: Lynn Chua, Badih Ghazi, Pritish Kamath, Ravi Kumar, Pasin Manurangsi,
         Amer Sinha, Chiyuan Zhang
Link: https://arxiv.org/abs/2411.04205

For deterministic batch samplers, the analysis uses the Gaussian mechanism, and
the implementation uses Gaussian CDFs (provided in scipy library). This analysis
is efficient and provides nearly exact bounds.

For Poisson batch samplers, the analysis uses the Poisson subsampled Gaussian
mechanism, and the implementation uses the dp_accounting library. The PLD
based analysis provides upper and lower bounds on the privacy parameters. The
RDP based analysis, while more efficient, only provides an upper bound.

For Shuffle batch samplers, the analysis uses a "cube" set to establish a lower
bound on the hockey stick divergence.
"""

import collections
import functools
import math
from typing import Callable, Sequence

import dp_accounting
from dp_accounting import pld
from dp_accounting import rdp
import numpy as np
from scipy import stats


def inverse_decreasing_function(
    function, value):
  """Returns the smallest x at which function(x) <= value."""
  # A heuristic initial guess of 10 is chosen. This only costs in efficiency.
  search_params = pld.common.BinarySearchParameters(0, np.inf, 10)
  value = pld.common.inverse_monotone_function(function, value, search_params)
  if value is None:
    raise ValueError(f'No input x found for {value=}.')
  return value


class DeterministicAccountant:
  """Privacy accountant for ABLQ with deterministic batch sampler."""

  def __init__(self):
    pass

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_deltas(self,
                 sigma,
                 epsilons,
                 num_epochs = 1):
    """Returns delta values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      epsilons: A list or numpy array of epsilon values for which to compute the
        hockey stick divergence.
      num_epochs: The number of epochs.

    Returns:
      A list of hockey stick divergence values corresponding to each epsilon.
    """
    sigma = sigma / np.sqrt(num_epochs)
    epsilons = np.atleast_1d(epsilons)
    upper_cdfs = stats.norm.cdf(0.5 / sigma - sigma * epsilons)
    lower_log_cdfs = stats.norm.logcdf(-0.5 / sigma - sigma * epsilons)
    return list(upper_cdfs - np.exp(epsilons + lower_log_cdfs))

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_epsilons(self,
                   sigma,
                   deltas,
                   num_epochs = 1):
    """Returns epsilon values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      deltas: The privacy parameters delta.
      num_epochs: The number of epochs.
    """
    delta_from_epsilon = lambda epsilon: self.get_deltas(
        sigma, (epsilon,), num_epochs)[0]
    return [
        inverse_decreasing_function(delta_from_epsilon, delta)
        for delta in deltas
    ]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_sigma(self,
                epsilon,
                delta,
                num_epochs = 1):
    """Returns the scale of the Gaussian noise for (epsilon, delta)-DP."""
    delta_from_sigma = lambda sigma: self.get_deltas(
        sigma, (epsilon,), num_epochs)[0]
    return inverse_decreasing_function(delta_from_sigma, delta)


class PoissonPLDAccountant:
  """Privacy accountant for ABLQ with Poisson batch sampler using PLD analysis.

  Attributes:
    discretization: The discretization interval to be used in computing the
      privacy loss distribution.
    pessimistic_estimate: When True, an upper bound on the hockey stick
      divergence is returned. When False, a lower bound on the hockey stick
      divergence is returned.
  """

  def __init__(self,
               pessimistic_estimate = True):
    self.pessimistic_estimate = pessimistic_estimate

  def _get_pld(
      self,
      sigma,
      num_compositions,
      sampling_prob,
      discretization = 1e-3,
  ):
    """Returns the composed PLD for ABLQ_P.

    Args:
      sigma: The scale of the Gaussian noise.
      num_compositions: The number of compositions.
      sampling_prob: The sampling probability in each step.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
    """
    pl_dist = pld.privacy_loss_distribution.from_gaussian_mechanism(
        sigma,
        pessimistic_estimate=self.pessimistic_estimate,
        value_discretization_interval=discretization,
        sampling_prob=sampling_prob,
        use_connect_dots=self.pessimistic_estimate,
    )
    return pl_dist.self_compose(num_compositions)

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_deltas(self,
                 sigma,
                 epsilons,
                 num_steps_per_epoch,
                 num_epochs = 1,
                 discretization = 1e-3):
    """Returns delta values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      epsilons: A list or numpy array of epsilon values.
      num_steps_per_epoch: The number of steps per epoch. The subsampling
        probability is set to be 1 / num_steps_per_epoch.
      num_epochs: The number of epochs.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.

    Returns:
      A list of hockey stick divergence estimates corresponding to each epsilon.
    """
    pl_dist = self._get_pld(
        sigma=sigma,
        num_compositions=num_steps_per_epoch * num_epochs,
        sampling_prob=1.0/num_steps_per_epoch,
        discretization=discretization)
    return list(pl_dist.get_delta_for_epsilon(epsilons))

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_epsilons(self,
                   sigma,
                   deltas,
                   num_steps_per_epoch,
                   num_epochs = 1,
                   discretization = 1e-3):
    """Returns epsilon values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      deltas: The privacy parameters delta.
      num_steps_per_epoch: The number of steps per epoch. The subsampling
        probability is set to be 1 / num_steps_per_epoch.
      num_epochs: The number of epochs.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
    """
    pl_dist = self._get_pld(
        sigma=sigma,
        num_compositions=num_steps_per_epoch * num_epochs,
        sampling_prob=1.0/num_steps_per_epoch,
        discretization=discretization)
    return [pl_dist.get_epsilon_for_delta(delta) for delta in deltas]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_sigma(self,
                epsilon,
                delta,
                num_steps_per_epoch,
                num_epochs = 1,
                discretization = 1e-3):
    """Returns the scale of the Gaussian noise for (epsilon, delta)-DP."""
    delta_from_sigma = lambda sigma: self.get_deltas(
        sigma, (epsilon,), num_steps_per_epoch, num_epochs, discretization)[0]
    return inverse_decreasing_function(delta_from_sigma, delta)


class PoissonRDPAccountant:
  """Privacy accountant for ABLQ with Poisson batch sampler using RDP analysis.
  """

  def __init__(self):
    pass

  def _get_rdp_accountant(
      self,
      sigma,
      num_compositions,
      sampling_prob
  ):
    """Returns RDP accountant after composition of Poisson subsampled Gaussian.

    Args:
      sigma: The scale of the Gaussian noise.
      num_compositions: The number of compositions.
      sampling_prob: The sampling probability in each step.
    """
    accountant = rdp.RdpAccountant()
    event = dp_accounting.dp_event.PoissonSampledDpEvent(
        sampling_prob, dp_accounting.dp_event.GaussianDpEvent(sigma)
    )
    accountant.compose(event, num_compositions)
    return accountant

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_deltas(self,
                 sigma,
                 epsilons,
                 num_steps_per_epoch,
                 num_epochs = 1):
    """Returns delta values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      epsilons: A list or numpy array of epsilon values.
      num_steps_per_epoch: The number of steps per epoch. The subsampling
        probability is set to be 1 / num_steps_per_epoch.
      num_epochs: The number of epochs.

    Returns:
      A list of hockey stick divergence estimates corresponding to each epsilon.
    """
    accountant = self._get_rdp_accountant(
        sigma=sigma,
        num_compositions=num_steps_per_epoch * num_epochs,
        sampling_prob=1.0/num_steps_per_epoch)
    return [accountant.get_delta(epsilon) for epsilon in epsilons]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_epsilons(self,
                   sigma,
                   deltas,
                   num_steps_per_epoch,
                   num_epochs = 1):
    """Returns epsilon values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      deltas: The privacy parameters delta.
      num_steps_per_epoch: The number of steps per epoch. The subsampling
        probability is set to be 1 / num_steps_per_epoch.
      num_epochs: The number of epochs.
    """
    accountant = self._get_rdp_accountant(
        sigma=sigma,
        num_compositions=num_steps_per_epoch * num_epochs,
        sampling_prob=1.0/num_steps_per_epoch)
    return [accountant.get_epsilon(delta) for delta in deltas]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_sigma(self,
                epsilon,
                delta,
                num_steps_per_epoch,
                num_epochs = 1):
    """Returns the scale of the Gaussian noise for (epsilon, delta)-DP."""
    delta_from_sigma = lambda sigma: self.get_deltas(
        sigma, (epsilon,), num_steps_per_epoch, num_epochs)[0]
    return inverse_decreasing_function(delta_from_sigma, delta)


class ShuffleAccountant:
  """Accountant for ABLQ with shuffling; only provides lower bounds.

  This class only provides a lower bound on the privacy parameters. The hockey
  stick divergence is computed for the pair (P, Q), where P and Q are mixtures
  of Gaussian distributions P = MoG(mean_upper) and Q = MoG(mean_lower), where
  MoG(mean) := sum_{t=1}^T (1/T) * N(mean * e_t, sigma^2 * I_t),
  where T refers to the number of steps in a single epoch.

  Multiple epochs are analyzed as compositions of the single epoch mechanism.
  """

  def __init__(self,
               mean_upper = 2.0,
               mean_lower = 1.0):
    self.mean_upper = mean_upper
    self.mean_lower = mean_lower

  def _log_in_cube_mass(self,
                        sigma,
                        num_steps,
                        caps,
                        mean):
    """Returns log probability that max_t x_t <= cap, under MoG(mean).

    Args:
      sigma: The scale of the Gaussian noise.
      num_steps: The number of steps of composition.
      caps: The parameter defining the cube E_C given as {x : max_t x_t <= C}.
      mean: The mean parameter of MoG distribution.
    """
    return (
        stats.norm.logcdf((caps - mean) / sigma) +
        (num_steps - 1) * stats.norm.logcdf(caps / sigma)
    )

  def _out_cube_mass(self,
                     sigma,
                     num_steps,
                     caps,
                     mean):
    """Returns mass assigned by mixture of Gaussians to complement of a cube.

    Args:
      sigma: The scale of the Gaussian noise.
      num_steps: The number of steps of composition, denoted as T above.
      caps: The parameter defining the cube E_C given as {x : max_t x_t <= C}.
      mean: The mean parameter of MoG distribution.
    """
    return - np.expm1(self._log_in_cube_mass(sigma, num_steps, caps, mean))

  def _log_slice_mass(self,
                      sigma,
                      num_steps,
                      caps_1,
                      caps_2,
                      mean):
    """Returns log probability of cap_1 <= max_t x_t <= cap_2 under MoG(mean).

    For all (cap_1, cap_2) in zip(caps_1, caps_2). Requires that all coordinates
    of caps_1 are smaller than corresponding coordinates of caps_2.

    Args:
      sigma: The scale of the Gaussian noise.
      num_steps: The number of steps of composition.
      caps_1: The lower bounds of the slice.
      caps_2: The upper bounds of the slice.
      mean: The mean parameter of MoG distribution.

    Raises:
      ValueError if caps_1 is not coordinate-wise less than caps_2.
    """
    if np.any(caps_1 >= caps_2):
      raise ValueError('caps_1 must be coordinate-wise less than caps_2. '
                       f'Found {caps_1=} and {caps_2=}.')
    log_cube_mass_1 = self._log_in_cube_mass(sigma, num_steps, caps_1, mean)
    log_cube_mass_2 = self._log_in_cube_mass(sigma, num_steps, caps_2, mean)
    return log_cube_mass_1 + np.log(np.expm1(log_cube_mass_2 - log_cube_mass_1))

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_deltas_single_epoch(
      self,
      sigma,
      epsilons,
      num_steps,
      caps = None,
      verbose = True,
  ):
    """Returns lower bounds on delta values for corresponding epsilons.

    Args:
      sigma: The scale of the Gaussian noise.
      epsilons: A list or numpy array of epsilon values.
      num_steps: The number of steps of the mechanism.
      caps: The parameter defining the cube E_C given as {x : max_t x_t <= C}.
      verbose: When True, prints the optimal C value for each epsilon.
    """
    caps = np.arange(0, 100, 0.01) if caps is None else np.asarray(caps)
    upper_masses = self._out_cube_mass(
        sigma, num_steps, caps, self.mean_upper)
    lower_masses = self._out_cube_mass(
        sigma, num_steps, caps, self.mean_lower)
    epsilons = np.atleast_1d(epsilons)
    if verbose:
      print('Shuffle hockey stick divergence logs:')
      ans = []
      for epsilon in epsilons:
        hsd = upper_masses - np.exp(epsilon) * lower_masses
        i = np.argmax(hsd)
        print(f'* optimal C for {epsilon=} is: {caps[i]}')
        ans.append(hsd[i])
    else:
      ans = [
          np.max(upper_masses - np.exp(epsilon) * lower_masses)
          for epsilon in epsilons
      ]
    return ans

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_epsilons_single_epoch(
      self,
      sigma,
      deltas,
      num_steps,
      caps = None,
  ):
    """Returns epsilon values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      deltas: The privacy parameters delta.
      num_steps: The number of steps of the mechanism.
      caps: The parameter defining the cube E_C given as {x : max_t x_t <= C}.

    Returns:
      The epsilon value for which ABLQ_S satisfies (epsilon, delta)-DP.
    """
    delta_from_epsilon = lambda epsilon: self.get_deltas_single_epoch(
        sigma, (epsilon,), num_steps, caps, verbose=False)[0]
    return [
        inverse_decreasing_function(delta_from_epsilon, delta)
        for delta in deltas
    ]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_sigma_single_epoch(self,
                             epsilon,
                             delta,
                             num_steps,
                             caps = None):
    """Returns the scale of the Gaussian noise for (epsilon, delta)-DP."""
    delta_from_sigma = lambda sigma: self.get_deltas_single_epoch(
        sigma, (epsilon,), num_steps, caps, verbose=False)[0]
    return inverse_decreasing_function(delta_from_sigma, delta)

  def _get_single_epoch_pld(
      self,
      sigma,
      num_steps,
      discretization = 1e-3,
      pessimistic_estimate = False,
      log_truncation_mass = -40,
      verbose = False,
  ):
    """Returns Privacy Loss Distribution for a single epoch.

    Args:
      sigma: The scale of the Gaussian noise.
      num_steps: The number of steps of the mechanism in a single epoch.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
      pessimistic_estimate: When True, an upper bound on the hockey stick
        divergence is returned. When False, a lower bound on the hockey stick
        divergence is returned.
      log_truncation_mass: The log of the truncation mass.
      verbose: When True, intermediate computations of the single-epoch PLD
        construction are printed.
    """
    log_truncation_mass -= math.log(2)
    truncation_mass = math.exp(log_truncation_mass)
    lower_cap = sigma * stats.norm.ppf(
        math.exp(log_truncation_mass / num_steps)
    )
    upper_cap = self.mean_upper + sigma * stats.norm.isf(
        -1.0 * math.expm1(math.log1p(-truncation_mass) / num_steps)
    )

    pmf = collections.defaultdict(lambda: 0.0)
    sigma_square = sigma ** 2
    # We use a heuristic value of gap that ensures that max_t x_t / sigma^2
    # changes by `discretization` between two consecutive slices.
    gap = discretization * sigma_square

    caps_1 = np.arange(lower_cap, upper_cap, gap)
    caps_2 = caps_1 + gap
    upper_cap = caps_2[-1]

    if verbose:
      print(
          f'truncating to {lower_cap=}, {upper_cap=}\n'
          'lower log mass truncated: '
          f'{self._log_in_cube_mass(sigma, num_steps, lower_cap, 2)}\n'
          'upper log mass truncated: '
          f'{math.log(self._out_cube_mass(sigma, num_steps, upper_cap, 2))}\n'
          f'num intervals = {len(caps_1)}'
      )

    if pessimistic_estimate:
      log_upper_probs = self._log_slice_mass(
          sigma, num_steps, caps_1, caps_2, self.mean_upper)
      # The following is an upper bound on the privacy loss anywhere in the
      # slice between cap_1 and cap_2.
      rounded_privacy_losses = np.ceil(
          (self.mean_upper - self.mean_lower)
          * (caps_2 - (self.mean_upper + self.mean_lower) / 2)
          / (sigma_square * discretization)
      ).astype(int)

      # max_t x_t >= upper_cap
      infinity_mass = self._out_cube_mass(
          sigma, num_steps, upper_cap, self.mean_upper)

      # max_t x_t <= lower_cap
      rounded_privacy_loss = math.ceil(
          (self.mean_upper - self.mean_lower)
          * (lower_cap - (self.mean_upper + self.mean_lower) / 2)
          / (sigma_square * discretization)
      )
      pmf[rounded_privacy_loss] += math.exp(
          self._log_in_cube_mass(sigma, num_steps, lower_cap, self.mean_upper))
    else:
      log_upper_probs = self._log_slice_mass(
          sigma, num_steps, caps_1, caps_2, self.mean_upper)
      log_lower_probs = self._log_slice_mass(
          sigma, num_steps, caps_1, caps_2, self.mean_lower)
      rounded_privacy_losses = np.floor(
          (log_upper_probs - log_lower_probs) / discretization
      ).astype(int)

      # max_t x_t >= upper_C
      infinity_mass = 0
      upper_out_cube_mass = self._out_cube_mass(
          sigma, num_steps, upper_cap, self.mean_upper)
      lower_out_cube_mass = self._out_cube_mass(
          sigma, num_steps, upper_cap, self.mean_lower)
      rounded_privacy_loss = math.floor(
          (math.log(upper_out_cube_mass) - math.log(lower_out_cube_mass))
          / discretization
      )
      pmf[rounded_privacy_loss] += upper_out_cube_mass

      # max_t x_t <= lower_C
      upper_log_in_cube_mass = self._log_in_cube_mass(
          sigma, num_steps, lower_cap, self.mean_upper)
      lower_log_in_cube_mass = self._log_in_cube_mass(
          sigma, num_steps, lower_cap, self.mean_lower)
      rounded_privacy_loss = math.floor(
          (upper_log_in_cube_mass - lower_log_in_cube_mass)
          / discretization
      )
      pmf[rounded_privacy_loss] += math.exp(upper_log_in_cube_mass)

    upper_probs = np.exp(log_upper_probs)
    for rounded_priv_loss, prob in zip(rounded_privacy_losses, upper_probs):
      pmf[rounded_priv_loss] += prob

    return pld.privacy_loss_distribution.PrivacyLossDistribution(
        pld.pld_pmf.SparsePLDPmf(
            pmf, discretization, infinity_mass, pessimistic_estimate
        )
    )

  def _get_multi_epoch_pld(
      self,
      sigma,
      num_steps_per_epoch,
      num_epochs = 1,
      discretization = 1e-3,
      pessimistic_estimate = False,
      log_truncation_mass = -40,
      verbose = False,
  ):
    """Returns Privacy Loss Distribution for multiple epochs.

    Args:
      sigma: The scale of the Gaussian noise.
      num_steps_per_epoch: The number of steps of the mechanism in a single
        epoch.
      num_epochs: The number of epochs.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
      pessimistic_estimate: When True, an upper bound on the hockey stick
        divergence is returned. When False, a lower bound on the hockey stick
        divergence is returned.
      log_truncation_mass: The log of the truncation mass.
      verbose: When True, intermediate computations of the single-epoch PLD
        construction are printed.
    """
    pl_dist = self._get_single_epoch_pld(
        sigma, num_steps_per_epoch, discretization, pessimistic_estimate,
        log_truncation_mass - math.log(num_epochs), verbose)
    return pl_dist.self_compose(num_epochs)

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_deltas(
      self,
      sigma,
      epsilons,
      num_steps_per_epoch,
      num_epochs = 1,
      reshuffle = True,
      discretization = 1e-3,
      pessimistic_estimate = False,
      log_truncation_mass = -40,
      verbose = False,
  ):
    """Returns lower bounds on delta values for corresponding epsilons.

    Args:
      sigma: The scale of the Gaussian noise.
      epsilons: A list or numpy array of epsilon values.
      num_steps_per_epoch: The number of steps of the mechanism per epoch.
      num_epochs: The number of epochs.
      reshuffle: When True, the shuffle mechanism is assumed to employ
        reshuffle between different epochs. When False, it is assumed that
        the same shuffled order is used in all epochs.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
      pessimistic_estimate: When False, a lower bound on the hockey stick
        divergence is returned. When True, an upper bound estimate is returned;
        but since we do not know for sure that the pair we consider is
        dominating, this may not be an upper bound on the hockey stick
        divergence.
      log_truncation_mass: The log of the truncation mass.
      verbose: When True, intermediate computations of the single-epoch PLD
        construction are printed.
    """
    if not reshuffle or num_epochs == 1:
      return self.get_deltas_single_epoch(
          sigma / math.sqrt(num_epochs), epsilons, num_steps_per_epoch,
          verbose=verbose
      )
    pl_dist = self._get_multi_epoch_pld(
        sigma, num_steps_per_epoch, num_epochs, discretization,
        pessimistic_estimate, log_truncation_mass, verbose)
    return list(pl_dist.get_delta_for_epsilon(epsilons))

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_epsilons(
      self,
      sigma,
      deltas,
      num_steps_per_epoch,
      num_epochs = 1,
      reshuffle = True,
      discretization = 1e-3,
      pessimistic_estimate = False,
      log_truncation_mass = -40,
      verbose = False,
  ):
    """Returns epsilon values for which (epsilon, delta)-DP is satisfied.

    Args:
      sigma: The scale of the Gaussian noise.
      deltas: The privacy parameters delta.
      num_steps_per_epoch: The number of steps of the mechanism per epoch.
      num_epochs: The number of epochs.
      reshuffle: When True, the shuffle mechanism is assumed to employ
        reshuffle between different epochs. When False, it is assumed that
        the same shuffled order is used in all epochs.
      discretization: The discretization interval to be used in computing the
        privacy loss distribution.
      pessimistic_estimate: When False, a lower bound on the hockey stick
        divergence is returned. When True, an upper bound estimate is returned;
        but since we do not know for sure that the pair we consider is
        dominating, this may not be an upper bound on the hockey stick
        divergence.
      log_truncation_mass: The log of the truncation mass.
      verbose: When True, intermediate computations of the single-epoch PLD
        construction are printed.
    """
    if not reshuffle or num_epochs == 1:
      return self.get_epsilons_single_epoch(
          sigma / math.sqrt(num_epochs), deltas, num_steps_per_epoch,
      )
    pl_dist = self._get_multi_epoch_pld(
        sigma, num_steps_per_epoch, num_epochs, discretization,
        pessimistic_estimate, log_truncation_mass, verbose)
    return [pl_dist.get_epsilon_for_delta(delta) for delta in deltas]

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_sigma(self,
                epsilon,
                delta,
                num_steps_per_epoch,
                num_epochs = 1,
                reshuffle = True,
                discretization = 1e-3,
                pessimistic_estimate = False,
                log_truncation_mass = -40):
    """Returns the scale of the Gaussian noise for (epsilon, delta)-DP."""
    delta_from_sigma = lambda sigma: self.get_deltas(
        sigma, (epsilon,), num_steps_per_epoch, num_epochs, reshuffle,
        discretization, pessimistic_estimate, log_truncation_mass,
        verbose=False)[0]
    return inverse_decreasing_function(delta_from_sigma, delta)

# coding=utf-8
# Copyright 2024 The Google Research Authors.
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

"""Library for Monte-Carlo Estimation."""

import dataclasses
import math
from typing import Callable, Sequence

from dp_accounting import pld
import numpy as np


def get_batch_splits(
    sample_size, max_batch_size = None
):
  """Returns a list of batch sizes to use for Monte Carlo sampling.

  Args:
    sample_size: The total number of samples to generate.
    max_batch_size: An upper bound on all batch sizes. If None, all samples are
      assigned to a single batch.
  Returns:
    A list of batch sizes to use for sampling. If there is more than one batch,
    then all batches except the last one will have size `max_batch_size`, and
    the last batch will have size `sample_size % max_batch_size`. For example,
    if `sample_size = 70` and `max_batch_size = 30`, then the returned list will
    be [30, 30, 10].
  """
  if max_batch_size is None:
    return [sample_size]

  # Split the sample size into values each being at most max_batch_size.
  sample_size_sequences = [max_batch_size] * (sample_size // max_batch_size)
  if sample_size % max_batch_size > 0:
    sample_size_sequences.append(sample_size % max_batch_size)
  return sample_size_sequences


def bernoulli_kl_divergence(q, p):
  """Returns the KL divergence between two Bernoulli distributions.

  It is assumed that q and p are probabilities, that is, they are in [0, 1].
  This is not enforced for efficiency.

  Args:
    q: The probability of success of the first Bernoulli distribution.
    p: The probability of success of the second Bernoulli distribution.
  Returns:
    The KL divergence D(Ber(q) || Ber(p)).
  """
  if q == 0:
    if p == 1:
      return math.inf
    return -math.log1p(-p)  # equivalent to - log(1 - p)
  if q == 1:
    if p == 0:
      return math.inf
    return - math.log(p)
  if p == 0 or p == 1:
    return math.inf
  return q * math.log(q / p) + (1 - q) * math.log((1 - q) / (1 - p))


def find_p_above_kl_bound(q, kl_bound):
  """Returns the smallest p s.t. KL(q || p) >= kl_bound or 1 if none exists."""
  # We want to search for a `p` in the interval [q, 1].
  search_params = pld.common.BinarySearchParameters(q, 1)
  # inverse_monotone_function finds a value of p such that f(p) <= value
  # that is, - KL(q || p) <= - kl_bound, that is, KL(q || p) >= kl_bound.
  f = lambda p: - bernoulli_kl_divergence(q, p)
  optimal_p = pld.common.inverse_monotone_function(
      f, - kl_bound, search_params, increasing=False)
  return 1.0 if optimal_p is None else optimal_p


@dataclasses.dataclass
class Estimate:
  """Monte Carlo estimate from samples.

  Attributes:
    mean: The mean of the estimate.
    std: The standard deviation of the estimate.
    sample_size: The number of samples used to estimate the mean and std.
    scale: A worst case upper bound on the quantity whose mean is estimated.
      A smaller scale will result in tighter upper confidence bound.
  """
  mean: float
  std: float
  sample_size: int
  scale: float = 1.0

  @classmethod
  def from_values_and_scale(cls, values, scale = 1.0):
    """Returns an Estimate from values and scale."""
    if values.ndim != 1:
      raise ValueError(f'{values.shape=}; expected (sample_size,).')
    sample_size = values.shape[0]
    mean = np.mean(values)
    std = (
        np.sqrt(np.sum((values - mean)**2) / (sample_size * (sample_size - 1)))
    )
    return Estimate(mean, std, sample_size, scale)

  @classmethod
  def from_combining_independent_estimates(
      cls, estimates
  ):
    """Returns an Estimate from combining independent estimates.

    Given means m_1, ... , m_k and standard deviations s_1, ... , s_k of
    independent estimates with sample sizes n_1, ... , n_k, the mean and
    standard deviation of the combined estimate are given by:
    mean = sum(m_i * n_i) / sum(n_i)
    std = sqrt(sum(s_i**2 * n_i * (n_i - 1)) / (sum(n_i) * (sum(n_i) - 1)))

    Args:
      estimates: A sequence of estimates to combine.
    Returns:
      An Estimate from combining the given independent estimates.
    Raises:
      ValueError: If estimates is an empty list or have different scales.
    """
    if not estimates:
      raise ValueError('estimates must be non-empty.')

    scale = estimates[0].scale
    if any(est.scale != scale for est in estimates):
      raise ValueError(f'Estimates have different scales: {estimates=}')

    means = np.array([est.mean for est in estimates])
    stds = np.array([est.std for est in estimates])
    sample_sizes = np.array([est.sample_size for est in estimates])
    total_sample_size = np.sum(sample_sizes)

    mean = np.dot(means, sample_sizes / total_sample_size)
    std = np.linalg.norm(
        stds * np.sqrt(sample_sizes * (sample_sizes - 1))
        / math.sqrt(total_sample_size * (total_sample_size - 1))
    )
    return Estimate(mean, std, total_sample_size, scale)

  def get_upper_confidence_bound(self, error_prob):
    """Returns an upper confidence bound for the estimate.

    For `n` = sample_size, let `X_1, ... , X_n` be drawn from some distribution
    over [0, C]. And let q := (X_1 + ... + X_n) / n.

    Then for `p` such that KL(q/C || p/C) * n >= log(1 / error_prob), we have
    Pr[E[X] <= p] >= 1 - error_prob, where the probability is over the random
    draw of X_1, ... , X_n.

    Proof: For simplicity, assume that C = 1. Suppose the true mean of the
    distribution is `m`. By Chernoff's bound, we have that for any q
    Pr[(X_1 + ... + X_n) / n <= q] <= exp(-KL(q || m) n).
    For the returned value `p` to be smaller than `m`, the realized `q` must be
    such that KL(q || m) > KL(q || p) >= log(1 / error_prob) / n.
    Hence, probability of realizing such a `q` is at most error_prob.

    Args:
      error_prob: The desired probability of error that the true mean is not
      smaller than the returned value.
    Returns:
      An upper confidence bound for the estimate.
    """
    if self.scale == 0:
      return 0.0
    kl_bound = - np.log(error_prob) / self.sample_size
    return self.scale * find_p_above_kl_bound(self.mean / self.scale, kl_bound)


def get_monte_carlo_estimate_with_scaling(
    sampler,
    f,
    scaling_factor,
    sample_size,
    max_batch_size = None,
):
  """Monte-Carlo estimate of expected value of a function with scaling.

  Args:
    sampler: A method that returns a sample of specified size as numpy array.
      The sample can be multi-dimensional, but should have the first dimension
      length equal to specified sample size.
    f: A function that maps samples to corresponding function values. The return
      value of `f` must be 1-dimensional with shape (sample_size,).
    scaling_factor: A float value to multiply the `mean` and `std` by.
    sample_size: The number of times to repeat the sampling.
    max_batch_size: The maximum size to use in a single call to `sampler`.
      If None, then all samples are obtained in a single call to `sampler`.
  Returns:
    Estimate of E[f(x) * scaling] for x ~ sampler.
  Raises:
    RuntimeError: If the return value of `f` is not a one-dimensional vector
      of length equal to the length of the first dimension of its input.
  """
  if scaling_factor == 0:
    # No need to actually sample if scaling factor is 0.
    return Estimate(mean=0, std=0, sample_size=sample_size,
                    scale=scaling_factor)

  sample_size_sequences = get_batch_splits(sample_size, max_batch_size)

  f_values = []
  for size in sample_size_sequences:
    samples = sampler(size)
    f_values.append(f(samples))
    del samples  # Explicitly delete samples to free up memory.
  f_values = np.concatenate(f_values)

  if f_values.shape != (sample_size,):
    raise RuntimeError(f'{f_values.shape=}; expected ({sample_size},).')

  return Estimate.from_values_and_scale(f_values * scaling_factor,
                                        scaling_factor)

# coding=utf-8
# Copyright 2024 The Google Research Authors.
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

"""Monte-Carlo estimate based accounting for Ball-and-Bins Sampler.

The source in this file is based on the following paper:

Title: Balls-and-Bins Sampling for DP-SGD
Authors: Lynn Chua, Badih Ghazi, Charlie Harrison, Ethan Leeman, Pritish Kamath,
         Ravi Kumar, Pasin Manurangsi, Amer Sinha, Chiyuan Zhang
Link: https://arxiv.org/abs/2412.16802

For the Balls and Bins batch sampler, the analysis is performed using Monte
Carlo sampling to get an estimate and an upper confidence bound on the hockey
stick divergence. Additionally a lower bound is obtained using ideas similar to
that for the Shuffle batch sampler in `dpsgd_bounds.py`.
"""

import enum
import math
from typing import Sequence

import numpy as np
from scipy import special
from scipy import stats

class MaxOfGaussians:
  """Class for max of i.i.d. Gaussian random variables.

  M_{sigma, dim} is the random variable sampled as max(X_1, ... , X_dim)
  where each X_i is drawn from N(0, sigma^2), that is Gaussian with standard
  deviation sigma. We use X_{sigma} to denote the random variable drawn from
  N(0, sigma^2).

  Attributes:
    sigma: The standard deviation of each Gaussian random variable.
    dim: The number of Gaussian random variables.
  """

  def __init__(self, sigma, dim):
    if sigma <= 0:
      raise ValueError(f'sigma must be positive. Found {sigma=}')
    if dim < 1:
      raise ValueError(f'dim must be a positive integer. Found {dim=}')
    self.sigma = sigma
    self.dim = dim

  def logcdf(self, x):
    """Returns log of the cumulative density function of M_{sigma, dim}.

    Pr[M_{sigma, dim} <= x] = Pr[X_{sigma} <= x]^dim

    Args:
      x: The input value at which to compute the CDF.
    Returns:
      The log of the probability that M_{sigma, dim} <= x.
    """
    return self.dim * stats.norm.logcdf(x, scale=self.sigma)

  def sf(self, x):
    """Returns the survival function of M_{sigma, dim}.

    Pr[M_{sigma, dim} > x] = 1 - (1 - Pr[X_{sigma} > x])^dim

    Args:
      x: The input value at which to compute the SF.
    Returns:
      The probability that M_{sigma, dim} > x.
    """
    return -np.expm1(self.dim * np.log1p(-stats.norm.sf(x, scale=self.sigma)))

  def logsf(self, x):
    """Returns log of the SF of M_{sigma, dim}.

    Pr[M_{sigma, dim} > x] = 1 - (1 - Pr[X_{sigma} > x])^dim

    Args:
      x: The value of the return value.
    Returns:
      The log of the probability that M_{sigma, dim} > x.
    """
    return np.log(self.sf(x))

  def cdf(self, x):
    """Returns CDF of max of Gaussians."""
    return np.exp(self.logcdf(x))

  def ppf(self, q):
    """Returns inverse of the CDF of M_{sigma, dim}.

    Recall: Pr[M_{sigma, dim} <= x] = Pr[X_{sigma} <= x]^dim
    And hence, Pr[X_{sigma} <= x] = Pr[M_{sigma, dim} > x]^{1/dim}

    Args:
      q: The CDF value(s) of the return value.
    Returns:
      Values x such that Pr[M_{sigma, dim} <= x] = q.
    """
    cumulative_probs_1d = np.exp(np.log(q) / self.dim)
    return stats.norm.ppf(cumulative_probs_1d, scale=self.sigma)

  def isf(self, q):
    """Returns inverse SF of max of Gaussians.

    Recall: Pr[M_{sigma, dim} > x] = 1 - (1 - Pr[X_{sigma} > x])^dim
    And hence, Pr[X_{sigma} > x] = 1 - (1 - Pr[M_{sigma, dim} > x])^{1/dim}

    Args:
      q: The SF value(s) of the return value.
    Returns:
      Values x such that Pr[M_{sigma, dim} > x] = q.
    """
    survival_probs_1d = - np.expm1(np.log1p(-q) / self.dim)
    return stats.norm.isf(survival_probs_1d, scale=self.sigma)

  def rvs(
      self, size, min_value = -np.inf
  ):
    """Returns samples from M_{sigma, dim} conditioned on being >= min_value.

    Args:
      size: The shape of the return value. If scalar, then an array of that
        size is returned.
      min_value: The minimum value for sampling from conditional distribution.
    Returns:
      Samples from M_{sigma, dim} of shape `size`, each drawn from
      M_{sigma, dim} conditioned on being at least `min_value`.
    """
    size = (size,) if isinstance(size, int) else size

    # We use a heuristic to decide when to use `ppf` vs `isf` for sampling
    # depending on `min_value`. Namely, if the CDF of the single Gaussian
    # corresponding to `min_value` is less than 0.5, we use `ppf` else `isf`.
    if self.logcdf(min_value) / self.dim < math.log(0.5):
      min_value_cdf = self.cdf(min_value)
      # cdf_values below are uniformly random in (min_value_cdf, 1).
      cdf_values = (1 - min_value_cdf) * np.random.rand(*size) + min_value_cdf
      return self.ppf(cdf_values)
    else:
      min_value_sf = self.sf(min_value)
      # sf_values below are uniformly random in (0, min_value_sf).
      sf_values = min_value_sf * np.random.rand(*size)
      return self.isf(sf_values)


def sample_gaussians_conditioned_on_max_value(
    sigma, dim, max_values
):
  """Samples from high dimensional Gaussian conditioned on max value.

  Args:
    sigma: The standard deviation of the Gaussian.
    dim: The dimension of the last axis of returned samples.
    max_values: The max value of the Gaussian.
  Returns:
    If max_values has shape (a_0, ..., a_t), the return value will have shape
    (a_0, ..., a_t, dim), where the value in coordinate
    (i_0, ..., i_t, i_{t+1}) is drawn from Gaussian with scale sigma,
    conditioned on the value being at most max_values[i_0, ..., i_t].
  """
  # max_values_cdf has the CDF corresponding to max_values.
  max_values_cdf = stats.norm.cdf(max_values, scale=sigma)
  # random_seed_values has shape (a_0, ..., a_t, dim), and the value at
  # coordinate (i_0, ..., i_t, i_{t+1}) is uniformly random in the interval
  # (0, CDF(max_values[i_0, ..., i_t])).
  random_seed_values = max_values_cdf[Ellipsis, np.newaxis] * np.random.rand(
      *(max_values.shape + (dim,))
  )
  return stats.norm.ppf(random_seed_values, scale=sigma)


def sample_gaussians_conditioned_on_min_max_value(
    sigma, min_max_value, dim, sample_size
):
  """Samples from high-dimensional Gaussian conditioned on being "out of box".

  Args:
    sigma: The standard deviation of each coordinate of the Gaussian
      distribution.
    min_max_value: The value such that the max value on each row of the returned
      output is at least this value.
    dim: The dimension of the Gaussian distribution.
    sample_size: The number of samples to sample.
  Returns:
    Samples of shape (sample_size, dim), where each row is sampled from the
    Gaussian distribution N(0, sigma^2 I_{dim}) conditioned on the event that
    the max value within the row is at least `min_max_value`.
  """
  # 1. Sample the max value for each sample; shape = (sample_size,)
  max_values = MaxOfGaussians(sigma, dim).rvs(
      size=sample_size, min_value=min_max_value
  )

  # 2. Sample coordinates with values at most the corresponding max value,
  # with shape = (sample_size, dim)
  samples = sample_gaussians_conditioned_on_max_value(sigma, dim, max_values)

  # 3. Insert the max values in a random coordinate within each row.
  row_indices = np.arange(sample_size)
  random_coords = np.random.randint(0, dim, size=(sample_size,))
  samples[row_indices, random_coords] = max_values

  return samples


def sample_order_statistics_from_uniform(
    dim, orders, size
):
  """Samples from order statistics of `dim` i.i.d. samples from U[0, 1].

  We use that the k-th top ranked element of a draw from U[0, 1]^n is
  distributed as Beta(n + 1 - k, k).
  The following process samples a draw from the joint distribution of
  the [k_1, k_2, ..., k_R] ranked elements from U[0, 1]^d.

  * Sample Z_1 ~ Beta(d - k_1 + 1, k_1). Set Y_1 = Z_1.
  * Sample Z_2 ~ Beta(d - k_2 + 1, k_2 - k_1). Set Y_2 = Z_2 * Y_1,
  * Sample Z_3 ~ Beta(d - k_3 + 1, k_3 - k_2). Set Y_3 = Z_3 * Y_2,
  * ... and so on ...
  * Sample Z_R ~ Beta(d - k_R + 1, k_R - k_{R-1}). Set Y_R = Z_R * Y_{R-1}.

  This is equivalent to: Y_k = prod_{i=1}^k Z_i, a "cumulative product".

  Args:
    dim: The total number of i.i.d. U[0, 1] random variables.
    orders: The sequence of order statistics to sample. It is assumed that
      these are sorted in increasing order, and all order values are integers
      in [1, dim]. For efficiency, this condition is not checked.
    size: The outer shape desired. E.g. if size = (a_0, a_1), then the return
      value will have shape (a_0, a_1, len(orders)). If size is scalar, then the
      return value will have shape (size, len(orders)).
  Returns:
    Samples of shape (size, len(orders)) [or size + (len(orders),)], where the
    last axis is sampled from the joint distribution of the [k_1, k_2, ..., k_R]
    ranked elements in a random draw from U[0, 1]^{dim}.
  """
  if isinstance(size, int):
    size = (size, len(orders))
  else:
    size = size + (len(orders),)
  # Sample Z_1, ..., Z_R
  orders = np.asarray(orders)
  random_seed = stats.beta.rvs(dim - orders + 1,
                               np.diff(np.insert(orders, 0, 0)),
                               size=size)
  # We use a numerically stable alternative to np.cumprod(random_seed, axis=-1).
  return np.exp(np.cumsum(np.log(random_seed), axis=-1))


def hockey_stick_divergence_from_privacy_loss(
    epsilon,
    privacy_losses,
):
  """Returns hockey stick divergence from privacy loss."""
  return np.maximum(0, - np.expm1(epsilon - privacy_losses))


def get_order_stats_seq_from_encoding(
    order_stats_encoding,
    num_steps_per_epoch
):
  """Returns the sequence of order statistics from the encoding.

  Encoding for order statistics must be None or a list of size that is a
  multiple of 3; the list is partitioned into tuples of size 3 and for each
  3-tuple of numbers (a, b, c), the orders of np.arange(a, b, c) are
  included. If `order_stats_encoding` is None or an empty list, then None is
  returned.

  Args:
    order_stats_encoding: The encoding of the order statistics.
    num_steps_per_epoch: The number of steps in a single epoch.
  """
  if not order_stats_encoding:
    # Handles the case of both `None` and empty list.
    return None

  if len(order_stats_encoding) % 3 != 0:
    raise ValueError(
        'order_stats_encoding must be a non-empty list of size that is a '
        f'multiple of 3. Found {order_stats_encoding}.'
    )
  order_stats_seq = np.concatenate([
      np.arange(a, b, c, dtype=int)
      for a, b, c in zip(
          order_stats_encoding[::3],
          order_stats_encoding[1::3],
          order_stats_encoding[2::3],
      )
  ])

  if (np.any(np.diff(order_stats_seq) < 1) or order_stats_seq[0] != 1
      or order_stats_seq[-1] > num_steps_per_epoch - 1):
    raise ValueError(
        '`order_stats_seq` must be sorted in increasing order, the first '
        'element should be 1 at last element should be at most '
        f'num_steps_per_epoch - 1. Found {order_stats_seq=}.'
    )
  return order_stats_seq


class AdjacencyType(enum.Enum):
  """Designates the type of adjacency for computing privacy loss distributions.

  ADD: the 'add' adjacency type specifies that the privacy loss distribution
    for a mechanism M is to be computed with mu_upper = M(D) and mu_lower =
    M(D'), where D' contains one more datapoint than D.
  REMOVE: the 'remove' adjacency type specifies that the privacy loss
    distribution for a mechanism M is to be computed with mu_upper = M(D) and
    mu_lower = M(D'), where D' contains one less datapoint than D.

  Note: We abuse notation and use 'ADD' and 'REMOVE' also to indicate the
  direction of adjacency in "Zeroing-Out" neighboring relation. Namely,
  'REMOVE' corresponds to replacing a real datapoint with the special symbol,
  and 'ADD' corresponds to the reverse.
  """
  ADD = 'ADD'
  REMOVE = 'REMOVE'


class BnBAccountant:
  """Privacy accountant for ABLQ with Balls and Bins Sampler.

  For REMOVE adjacency, consider the following upper and lower probability
  measures:
    upper_prob_measure P = sum_{t=1}^T N(e_t, sigma^2 * I) / T
    lower_prob_measure Q = N(0, sigma^2 * I)

    The privacy loss function L(x) is given as log(P(x) / Q(x)) is:
    L(x) = log(sum_{t=1}^T exp(x_t / sigma^2)) - log(T) - 1 / (2 * sigma^2)

  For ADD adjacency, the order of P and Q is reversed, and the loss function
  is negative of the above.

  The hockey stick divergence D_{e^eps}(P || Q) is given by
    E_{x ~ P} max{0, 1 - exp(epsilon - L(x))}.
  For P_t = N(e_t, sigma^2 * I) being the t-th component of the mixture P,
  the above expectation is same as E_{x ~ P_t} max{0, 1 - exp(epsilon - L(x))},
  by symmetry of all the P_t's. In particular, we can take t = 1.

  Furthermore, for any set E such that L(x) <= epsilon for all x not in E,
  the above expectation is same as
    P(E) * E_{P|E}  max{0, 1 - exp(epsilon - L(x))},
  where P|E is the distribution of P conditioned on the sample being in E.
  In particular,
  * for ADD adjacency, we use the set
    E_C := {x : max_t x_t <= C} for the smallest possible C.
  * for REMOVE adjacency, we use the set
    E_C := {x : max{x_1 - 1, max_{t > 1} x_t} >= C} for the largest possible C.

  Attributes:
    max_memory_limit: The maximum number of floats that can be sampled at once
      in memory. The Monte Carlo estimator breaks down the sample size into
      batches, each requiring at most `max_memory_limit` floats in memory.
    lower_bound_accountant: The accountant similar to the ShuffleAccountant for
      obtaining a lower bound on the hockey stick divergence.
  """

  def __init__(self, max_memory_limit = int(1e8)):
    self.max_memory_limit = max_memory_limit
    self.lower_bound_accountant = ShuffleAccountant(
        mean_upper=1.0, mean_lower=0.0,
    )

  def privacy_loss(
      self,
      sigma,
      samples,  # shape=(size, [num_epochs], num_steps_per_epoch)
      adjacency_type,
  ):
    """Returns privacy loss for samples.

    For REMOVE adjacency, the privacy loss for each x along the last axis of
    `samples` is given as:
    log(sum_{t=1}^T exp(x_t / sigma^2)) - log(T) - 1 / (2 * sigma^2)

    For ADD adjacency, the privacy loss is the negative of the above.

    Args:
      sigma: The scale of Gaussian noise.
      samples: The samples of shape (sample_size, num_steps_per_epoch) or
        (sample_size, num_epochs, num_steps_per_epoch).
      adjacency_type: The type of adjacency to use in computing privacy loss.
    """
    num_steps_per_epoch = samples.shape[-1]
    privacy_loss_per_epoch = (
        special.logsumexp(samples / sigma**2, axis=-1)
        - np.log(num_steps_per_epoch) - 1 / (2 * sigma**2)
    )
    if privacy_loss_per_epoch.ndim == 2:
      privacy_loss_per_epoch = np.sum(privacy_loss_per_epoch, axis=1)
    if adjacency_type == AdjacencyType.ADD:
      return - privacy_loss_per_epoch
    return privacy_loss_per_epoch

  def order_stats_privacy_loss(
      self,
      sigma,
      num_steps_per_epoch,
      samples,  # shape=(sample_size, [num_epochs], R)
      order_stats_weights,  # shape=(R,)
  ):
    """Returns order statistics upper bound on privacy loss for samples.

    The privacy loss for each x along the last axis of `samples` is given as:
    log(sum_{i=1}^{R} w_i * exp(x_i / sigma^2)) - log(T) - 1 / (2 * sigma^2)
    where w_1, ..., w_R are weights provided in `order_stats_weights`.

    This method does not take in the adjacency type, since that is encoded in
    the choice of `order_stats_weights`.

    Args:
      sigma: The scale of Gaussian noise.
      num_steps_per_epoch: The number of batches sampled in a single epoch.
      samples: The samples of shape (sample_size, R) or
        (sample_size, num_epochs, R).
      order_stats_weights: The weights associated with the order statistics, of
        shape (R,).
    Returns:
      The privacy loss of shape (sample_size,).
    """
    privacy_loss_per_epoch = (
        special.logsumexp(samples / sigma**2, axis=-1, b=order_stats_weights)
        - np.log(num_steps_per_epoch) - 1 / (2 * sigma**2)
    )
    if privacy_loss_per_epoch.ndim == 2:
      privacy_loss_per_epoch = np.sum(privacy_loss_per_epoch, axis=1)
    return privacy_loss_per_epoch

  def get_importance_threshold_value(
      self, sigma, epsilon, num_steps,
      adjacency_type = AdjacencyType.REMOVE,
  ):
    """Returns value of C such that L(x) <= eps for all x not in E_C.

    For ADD adjacency, the set E_C is given as:
    E_C := {x : max_t x_t <= C}
    Thus, we can choose C to be the smallest value such that:
    log(T) + 1/(2 * sigma^2) - log(exp(C / sigma^2)) <= epsilon.
    This is equivalent to:
    C >= 0.5 + (log(T) - epsilon) * sigma^2

    For REMOVE adjacency, the set E_C is given as:
    E_C := {x : max{x_1 - 1, max_{t > 1} x_t} >= C}
    Thus, we can choose C to be the largest value such that:
    log(exp((C+1)/sigma^2) + (T-1) * exp(C/sigma^2))
    <= log(T) + epsilon + 1/(2 * sigma^2).
    This is equivalent to:
    C / sigma^2 + log(exp(1/sigma^2) + T-1)
    <= log(T) + epsilon + 1/(2 * sigma^2).
    That is:
    C <= 0.5 + sigma^2 * (epsilon - log(1 + (exp(1/sigma^2) - 1) / T))
       = 0.5 + sigma^2 * (epsilon - log1p(expm1(1/sigma^2) / T))

    Args:
      sigma: The scale of Gaussian noise.
      epsilon: The epsilon value for which to compute the min max value.
      num_steps: The number of batches sampled.
      adjacency_type: The type of adjacency to use in computing threshold.
    Returns:
      The value of C such that L(x) <= epsilon for all x not in E_C.
    """
    if adjacency_type == AdjacencyType.ADD:
      return 0.5 + sigma**2 * (math.log(num_steps) - epsilon)
    else:  # Case: adjacency_type == AdjacencyType.REMOVE
      return (0.5 + sigma**2 * (
          epsilon - math.log1p(math.expm1(1 / sigma**2) / num_steps)))

  def sample_privacy_loss(
      self,
      sample_size,
      sigma,
      num_steps_per_epoch,
      num_epochs = 1,
      importance_threshold = None,
      adjacency_type = AdjacencyType.REMOVE,
  ):
    """Returns samples of privacy loss.

    Args:
      sample_size: The number of samples to return.
      sigma: The scale of Gaussian noise.
      num_steps_per_epoch: The number of batches sampled in a single epoch.
      num_epochs: The number of epochs.
      importance_threshold: The threshold value for importance sampling.
        For ADD adjacency, this is the value such that
        max_t x_t on each row of the returned output is at most
        `importance_threshold`.
        For REMOVE adjacency, this is the value such that
        max{ x_1 - 1, max_{t > 1} x_t} on each row of the returned output is at
        least `importance_threshold`.
        This value must be None when `num_epochs` is greater than 1.
      adjacency_type: The type of adjacency to use in computing privacy loss.
    Returns:
      Samples of shape (sample_size,).
    Raises:
      ValueError: If `min_max_value` is not None and `num_epochs` is not 1.
    """
    if importance_threshold is not None and num_epochs != 1:
      raise ValueError(
          'num_epochs must be 1 if importance_threshold is provided.'
          f'Found {importance_threshold=} and {num_epochs=}.'
      )
    if adjacency_type == AdjacencyType.ADD:
      if importance_threshold is None:
        samples = stats.norm.rvs(
            scale=sigma, size=(sample_size, num_epochs, num_steps_per_epoch)
        )
      else:
        # Guaranteed to be in the single epoch case at this point.
        max_values = importance_threshold * np.ones(sample_size)
        samples = sample_gaussians_conditioned_on_max_value(
            sigma, num_steps_per_epoch, max_values
        )
    else:  # Case: adjacency_type == AdjacencyType.REMOVE
      first_basis_vector = np.zeros(num_steps_per_epoch)
      first_basis_vector[0] = 1.0

      if importance_threshold is None:
        samples = first_basis_vector + stats.norm.rvs(
            scale=sigma, size=(sample_size, num_epochs, num_steps_per_epoch)
        )
      else:
        # Guaranteed to be in the single epoch case at this point.
        samples = sample_gaussians_conditioned_on_min_max_value(
            sigma, importance_threshold, num_steps_per_epoch, sample_size
        ) + first_basis_vector

    losses = self.privacy_loss(sigma, samples, adjacency_type)
    del samples  # Explicitly delete samples to free up memory.
    return losses

  def sample_order_stats_privacy_loss(
      self,
      sample_size,
      sigma,
      num_steps_per_epoch,
      order_stats_seq,
      num_epochs = 1,
      adjacency_type = AdjacencyType.REMOVE,
  ):
    """Returns samples of order statistics upper bounds on privacy loss.

    This method uses more efficient sampling of privacy loss, but yields
    pessimistic estimates. It relies on the following approach for sampling from
    a distribution that dominates the log-sum-exp of i.i.d. Gaussians, for
    order statistics [k_1, ... , k_R]:

    For REMOVE adjacency:
      Sample X_1 ~ N(1, sigma^2).
      Sample Y_1, Y_2, ... , Y_R ~ [k_1, ... , k_R] ranked elements from (T-1)
        samples from N(0, sigma^2).

      Use the following loss function to estimate hockey stick divergence:
      L(Y) = log(
          exp(X_1 / sigma^2)
          + sum_{t=1}^{R-1} (k_{t+1} - k_t) * exp(Y_t / sigma^2)
          + (T - k_R) * exp(Y_R / sigma^2)
      ) - log(T) - 1 / (2 * sigma^2)

    For ADD adjacency:
      Sample Y_1, Y_2, ... , Y_R ~ [k_1, ... , k_R] ranked elements from T
        samples from N(0, sigma^2).
      Use the following loss function to estimate hockey stick divergence:
      L(Y) = - log(
          k_1 * exp(Y_1 / sigma^2)
          + sum_{t=2}^{R} (k_t - k_{t-1}) * exp(Y_t / sigma^2)
      ) + log(T) + 1 / (2 * sigma^2)

    For multiple epochs, the following approach is used:
    For a dominating pair (P, Q), the hockey stick divergence corresponding to
    e-fold composition of a mechanism is given as:
      E_{x_1, ... , x_e ~ P} max{0, 1 - exp(epsilon - L(x_1) - ... - L(x_e))},
    where L(x) is the privacy loss at x corresponding to a single epoch.

    Args:
      sample_size: The number of samples to return.
      sigma: The scale of Gaussian noise.
      num_steps_per_epoch: The number of batches sampled in a single epoch.
      order_stats_seq: The sequence of orders to use for sampling order
        statistics, and computing upper bounds on the privacy loss. It is
        assumed that the orders are sorted in increasing order, the first value
        is 1 and the last value is at most num_steps_per_epoch - 1. This
        condition is not checked for efficiency reasons.
      num_epochs: The number of epochs.
      adjacency_type: The type of adjacency to use in computing privacy loss.
    Returns:
      Samples of privacy loss upper bounds of shape (sample_size,).
    """
    if adjacency_type == AdjacencyType.REMOVE:
      order_stats_weights = np.diff(np.append(order_stats_seq,
                                              num_steps_per_epoch))
      order_stats_weights = np.insert(order_stats_weights, 0, 1)
      first_coordinate_samples = stats.norm.rvs(
          loc=1, scale=sigma, size=(sample_size, num_epochs, 1))
      other_coordinates_samples = stats.norm.ppf(
          sample_order_statistics_from_uniform(num_steps_per_epoch - 1,
                                               order_stats_seq,
                                               (sample_size, num_epochs)),
          scale=sigma,
      )
      samples = np.concatenate(
          (first_coordinate_samples, other_coordinates_samples), axis=-1
      )
      loss_sign = 1.0
    else:  # Case: adjacency_type == AdjacencyType.ADD
      order_stats_weights = np.diff(np.insert(order_stats_seq, 0, 0))
      samples = stats.norm.ppf(
          sample_order_statistics_from_uniform(num_steps_per_epoch,
                                               order_stats_seq,
                                               (sample_size, num_epochs)),
          scale=sigma,
      )
      loss_sign = -1.0

    return loss_sign * self.order_stats_privacy_loss(
        sigma, num_steps_per_epoch, samples, order_stats_weights)

  def estimate_deltas(
      self,
      sigma,
      epsilons,
      num_steps_per_epoch,
      sample_size,
      num_epochs = 1,
      adjacency_type = AdjacencyType.REMOVE,
      use_importance_sampling = True,
  ):
    """Returns estimates of hockey stick divergence at various epsilons.

    Args:
      sigma: The scale of Gaussian noise.
      epsilons: A list of epsilon values for estimating hockey stick divergence.
      num_steps_per_epoch: The number of batches sampled in a single epoch.
      sample_size: The sample size to use for estimation.
      num_epochs: The number of epochs. When set to 1 (default), importance
        sampling is used to estimate the hockey stick divergence. But when set
        to a value greater than 1, importance sampling is not used, and the
        hockey stick divergence is estimated using naive sampling.
      adjacency_type: The type of adjacency to use in computing privacy loss
        distribution.
      use_importance_sampling: If True, then importance sampling is used to
        estimate the hockey stick divergence. Otherwise, naive sampling is used.
        This is only applicable when num_epochs is 1.
    Returns:
      A list of hockey stick divergence estimates corresponding to epsilons.
    """
    max_batch_size = int(self.max_memory_limit / num_steps_per_epoch)

    hsd_estimates = []
    for epsilon in epsilons:
      if num_epochs == 1 and use_importance_sampling:
        importance_threshold = self.get_importance_threshold_value(
            sigma, epsilon, num_steps_per_epoch, adjacency_type)
        if adjacency_type == AdjacencyType.ADD:
          # Use importance sampling for a single epoch, by conditioning
          # on the maximum value.
          scaling_factor = MaxOfGaussians(
              sigma, num_steps_per_epoch).cdf(importance_threshold)
        else:  # Case: adjacency_type == AdjacencyType.REMOVE
          # Use importance sampling for a single epoch, by conditioning
          # on a lower bound on the maximum value.
          scaling_factor = MaxOfGaussians(
              sigma, num_steps_per_epoch).sf(importance_threshold)

        sampler = lambda sample_size: self.sample_privacy_loss(
            sample_size,
            sigma,
            num_steps_per_epoch,
            num_epochs=1,
            importance_threshold=importance_threshold,  # pylint: disable=cell-var-from-loop
            adjacency_type=adjacency_type,
        )
      else:
        # No importance sampling is used for multiple epochs or when
        # specifically disabled by setting `use_importance_sampling = False`.
        sampler = lambda sample_size: self.sample_privacy_loss(
            sample_size,
            sigma,
            num_steps_per_epoch,
            num_epochs=num_epochs,
            adjacency_type=adjacency_type,
        )
        scaling_factor = 1.0

      f = lambda privacy_losses: hockey_stick_divergence_from_privacy_loss(
          epsilon, privacy_losses)  # pylint: disable=cell-var-from-loop

      hsd_estimates.append(get_monte_carlo_estimate_with_scaling(
          sampler, f, scaling_factor, sample_size, max_batch_size
      ))
    return hsd_estimates

  def estimate_order_stats_deltas(
      self,
      sigma,
      epsilons,
      num_steps_per_epoch,
      sample_size,
      order_stats_seq = None,
      num_epochs = 1,
      adjacency_type = AdjacencyType.REMOVE,
  ):
    """Returns pessimistic estimates of HS divergence for multiple epochs.

    The pessimistic estimate is obtained by sampling from the order statistics
    upper bound on the privacy loss. See docstring for
    `sample_order_stats_privacy_loss` for more details.

    Args:
      sigma: The scale of Gaussian noise.
      epsilons: A list of epsilon values for estimating hockey stick divergence.
      num_steps_per_epoch: The number of batches sampled in a single epoch.
      sample_size: The sample size to use for estimation.
      order_stats_seq: The sequence of order statistics to use for upper bound.
        If an integer, then the orders of [1, 2, ..., order_stats_seq] are used.
        If None, then the orders of [1, 2, ..., num_steps_per_epoch - 1] are
        used.
      num_epochs: The number of epochs.
      adjacency_type: The type of adjacency to use in computing privacy loss
        distribution.
    Returns:
      A list of hockey stick divergence estimates corresponding to epsilons.
    Raises:
      ValueError: If `order_stats_seq` is not sorted in increasing order or if
        the first value is not 1 or if any of the values are not in
        [1, num_steps - 1].
    """
    if sigma <= 0:
      raise ValueError(f'sigma must be positive. Found {sigma=}')
    if sample_size < 1:
      raise ValueError(f'sample_size must be positive. Found {sample_size=}')

    # Interpret `order_stats_seq` as a numpy array and check for any errors.
    if order_stats_seq is None:
      if adjacency_type == AdjacencyType.ADD:
        order_stats_seq = np.arange(1, num_steps_per_epoch + 1, dtype=int)
      else:  # Case: adjacency_type = AdjacencyType.REMOVE
        order_stats_seq = np.arange(1, num_steps_per_epoch, dtype=int)
    elif isinstance(order_stats_seq, int):
      # For ADD adjacency, it is also okay for order_stats_seq to be
      # num_steps_per_epoch. But since this is not an interesting setting we do
      # not handle this case.
      if order_stats_seq < 1 or order_stats_seq > num_steps_per_epoch - 1:
        raise ValueError(
            'If an integer, order_stats_seq must be in '
            f'[1, num_steps_per_epoch - 1]. Found {order_stats_seq=}.'
        )
      order_stats_seq = np.arange(1, order_stats_seq + 1, dtype=int)
    else:
      order_stats_seq = np.asarray(order_stats_seq)
      if np.any(np.diff(order_stats_seq) < 1):
        raise ValueError(
            'If a sequence, `order_stats_seq` must be sorted in increasing '
            f'order. Found {order_stats_seq=}'
        )
      if adjacency_type == AdjacencyType.ADD:
        if (order_stats_seq[0] < 1 or
            order_stats_seq[-1] > num_steps_per_epoch):
          raise ValueError(
              'Under ADD adjacency, all orders must be in '
              f'[1, num_steps_per_epoch]. Found {order_stats_seq=}'
          )
      else:  # Case: adjacency_type = AdjacencyType.REMOVE
        if (order_stats_seq[0] != 1 or
            order_stats_seq[-1] > num_steps_per_epoch - 1):
          raise ValueError(
              'Under REMOVE adjacency the first order should be 1 and the '
              'last order should be at most num_steps_per_epoch - 1. Found '
              f'{order_stats_seq=}.'
          )

    # Determine maximum batch size for Monte-Carlo estimation.
    if num_epochs * (len(order_stats_seq) + 1) > self.max_memory_limit:
      raise ValueError(
          'The number of epochs and the number of order statistics are too '
          'large for the given memory limit.'
      )
    max_batch_size = int(
        self.max_memory_limit / (num_epochs * (order_stats_seq.shape[0] + 1))
    )

    scaling_factor = 1.0  # Since no importance sampling is used.

    sampler = lambda sample_size: self.sample_order_stats_privacy_loss(
        sample_size, sigma, num_steps_per_epoch, order_stats_seq, num_epochs,
        adjacency_type)

    hsd_estimates = []
    for epsilon in epsilons:
      f = lambda privacy_losses: hockey_stick_divergence_from_privacy_loss(
          epsilon, privacy_losses)  # pylint: disable=cell-var-from-loop
      hsd_estimates.append(get_monte_carlo_estimate_with_scaling(
          sampler, f, scaling_factor, sample_size, max_batch_size
      ))
    return hsd_estimates

  def get_deltas_lower_bound(
      self,
      sigma,
      epsilons,
      num_steps_per_epoch,
      num_epochs = 1,
  ):
    """Returns lower bounds on delta values for corresponding epsilons."""
    return self.lower_bound_accountant.get_deltas(
        sigma, epsilons, num_steps_per_epoch, num_epochs
    )