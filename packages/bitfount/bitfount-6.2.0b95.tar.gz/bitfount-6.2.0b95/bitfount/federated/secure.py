"""Secure aggregation."""

from __future__ import annotations

from collections.abc import Mapping
import inspect
import logging
import secrets
from typing import TYPE_CHECKING, Any, ClassVar, Union

from marshmallow import fields
import numpy as np

from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.federated.transport.worker_transport import (
    _get_worker_secure_shares,
    _InterPodWorkerMailbox,
    _send_secure_shares_to_others,
)
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.types import _TensorLike

# Can't be larger than 2^64 -1 (largest unsigned 64 bit integer). Otherwise we get:
# "OverflowError: Python int too large to convert to C long"
LARGE_PRIME_NUMBER: int = (2**61) - 1  # Largest possible Mersenne prime number.

# Precision does not need to be greater than this in order be able to perform lossless
# computation on IEEE 754 32-bit floating point values
FLOAT_32_BIT_PRECISION: int = 10**10

_secure_share_registry: dict[str, type[_BaseSecureShare]] = {}

logger = logging.getLogger(__name__)


class _BaseSecureShare:
    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to registry")
            _secure_share_registry[cls.__name__] = cls


class SecureShare(_BaseSecureShare, _BaseSerializableObjectMixIn):
    """Additive, replicated, secret sharing algorithm responsible for secure averaging.

    This secret sharing implementation is 'additive' because the secret can be
    reconstructed by taking the sum of all the shares it is split into, and 'replicated'
    because each party receives more than one share.

    The algorithm works as follows:
        1. First every worker shares a securely generated random number (between 0 and
        `prime_q`) with every other worker such that every worker ends up with one
        number from every other worker. These numbers are known as shares as they will
        form part of the secret (the state dictionary) which will be shared.
        2. The values in the state dictionary are then converted to positive integer
        field elements of a finite field bounded by `prime_q`.
        3. The random numbers generated are used to compute a final share for every
        value in the state dictionary. This final share has the same shape as the secret
        state dictionary.
        4. This final share is then reconstructed using the shares retrieved from the
        other workers. At this point, the final share from each worker is meaningless
        until averaged with every other state dictionary.
        5. This final share is sent to the modeller where it will be averaged with the
        state dictionaries from all the other workers (all the while in the finite field
        space).
        6. After averaging, the state dictionaries are finally decoded back to floating
        point numpy arrays.

    :::note

    The relationships between individual elements in the tensors are preserved in
    this implementation since our shares are scalars rather than vectors. Therefore,
    whilst the secret itself cannot be reconstructed, some properties of the secret can
    be deciphered e.g. which element is the largest/smallest, etc.

    :::

    Args:
        prime_q: Large prime number used in secure aggregation. This should be a
            few orders of magnitude larger than the precision so that when we add
            encoded finite field elements with one another, we do not breach the limits
            of the finite field. Defaults to 2^61 -1 (the largest Mersenne 64 bit
            Mersenne prime number - for ease).
        precision: Degree of precision for floating points in secure aggregation
            i.e. the number of digits after the decimal point that we want to keep.
            Defaults to 10^10.

    Attributes:
        prime_q: Large prime number used in secure aggregation.
        precision: Degree of precision for floating points in secure aggregation.
    """

    # TODO: [BIT-423] Review security
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "prime_q": fields.Integer(),
        "precision": fields.Integer(),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(
        self,
        prime_q: int = LARGE_PRIME_NUMBER,
        precision: int = FLOAT_32_BIT_PRECISION,
    ):
        self.class_name = type(self).__name__
        self.prime_q = prime_q
        self.precision = precision

        self._tensor_shim = _load_default_tensor_shim()
        self._own_shares: list[int] = []
        self._other_worker_shares: list[int] = []

    def _encode_finite_field(
        self, rational: Union[_TensorLike, np.ndarray]
    ) -> np.ndarray:
        """Converts `rational` to integer in finite field."""
        total_num_workers = len(self._own_shares) + 1
        # Warning! on Windows astype(int) returns the min long value.
        # We use astype(np.int64) in this module to avoid this.

        # This branch is only for tensors. Clamping parameters does not apply to
        # non-model state dictionaries.
        if not isinstance(rational, np.ndarray):
            # Auxiliary value for checking finite field limit
            _upscaled_param_values = (
                self._tensor_shim.to_numpy(rational * self.precision).astype(np.int64)
                * total_num_workers
            )

            # Check that _upscaled_param_values are all within finite field limits
            if (
                (_upscaled_param_values > self.prime_q / 2)
                | (_upscaled_param_values < -self.prime_q / 2)
            ).sum() != 0:
                logger.warning(
                    "Parameter weights have been clipped. If you want to avoid this, "
                    "choose a larger `prime_q` or a smaller `precision` for "
                    "the `SecureShare` or normalize continuous features prior "
                    "to training."
                )
                rational = self._tensor_shim.clamp_params(
                    rational, self.prime_q, self.precision, total_num_workers
                )

            rational = self._tensor_shim.to_numpy(rational)

        upscaled = (rational * self.precision).astype(np.int64)
        field_element = upscaled % self.prime_q
        return field_element

    def _decode_finite_field(self, field_element: np.ndarray) -> np.ndarray:
        """Converts finite field array back into a rational array."""
        field_element = np.where(
            field_element > (self.prime_q / 2),
            field_element - self.prime_q,
            field_element,
        )
        return (field_element / self.precision).astype(float)

    def _encode_secret(self, secret: Union[_TensorLike, np.ndarray]) -> np.ndarray:
        """Encodes the provided secret using `self.own_shares` and returns it.

        Secret is first moved to the finite field space and then split into n shares
        where n is the number of all workers participating in training. All but one
        shares (integers) are shared with the other workers and the final share
        (a dictionary of tensors) is returned. The sum of all these will yield the
        original (encoded) secret.
        """
        secret_array = self._encode_finite_field(secret)
        encoded_secret = (secret_array - sum(self._own_shares)) % self.prime_q
        return encoded_secret

    def _reconstruct_secret(self, shares: list[Union[np.ndarray, int]]) -> np.ndarray:
        """Reconstructs the shares into a secret.

        This secret is not the same secret as originally encoded and shared. This secret
        is useless unless averaged with the secret outputs from all the other workers.
        """
        return np.asarray(sum(shares) % self.prime_q)

    def _encode_and_reconstruct_state_dict(
        self, secret_state_dict: Union[_Weights, Mapping[str, np.ndarray]]
    ) -> dict[str, np.ndarray]:
        """Encodes and reconstructs state dict from own and worker shares.

        Encrypts `secret_state_dict` using `own_shares` then reconstructs it using
        `self._other_worker_shares`.
        """
        logger.debug("Encoding state dict...")
        encrypted_state_dict = [
            self._encode_secret(v) for _, v in secret_state_dict.items()
        ]
        logger.debug("Reconstructing state dict...")
        reconstructed = [
            self._reconstruct_secret([*self._other_worker_shares, value])
            for value in encrypted_state_dict
        ]
        return dict(zip(list(secret_state_dict), reconstructed))

    def _get_random_number(self) -> int:
        """Generate a random number, append it to `self.own_shares` and also return it.

        Random number generator is cryptographically secure.
        """
        rand_num = secrets.randbelow(self.prime_q)
        self._own_shares.append(rand_num)
        return rand_num

    async def _share_own_shares(self, mailbox: _InterPodWorkerMailbox) -> None:
        """Sends own secure aggregation shares to other workers (one each).

        A random number is securely generated and sent to each worker such that each
        worker receives a different random number from every other worker. Each worker
        keeps a copy of the random numbers they generated which later become 'shares'
        as they can be used to encode a secret (the state dictionary).
        """
        self._own_shares = []
        await _send_secure_shares_to_others(self._get_random_number, mailbox)

    async def _receive_worker_shares(self, mailbox: _InterPodWorkerMailbox) -> None:
        """Receives secure aggregation shares from other workers."""
        self._other_worker_shares = await _get_worker_secure_shares(mailbox)

    def _add(self, arrays: list[np.ndarray]) -> np.ndarray:
        """Add multiple encoded numpy arrays element-wise and return a numpy array.

        All arrays must have the same shape.
        """
        if arrays[0].size > 1:
            return np.array(
                [np.sum(arrs, axis=0) % self.prime_q for arrs in zip(*arrays)]
            )
        else:
            return np.asarray(np.sum(arrays, axis=0) % self.prime_q)

    def average_and_decode_state_dicts(
        self,
        state_dicts: list[dict[str, np.ndarray]],
    ) -> dict[str, np.ndarray]:
        """Averages and decodes multiple encrypted state dictionaries.

        Computes the mean of all the `state_dicts` before decoding the averaged result
        and returning it. This is called on the Modeller side after receiving the state
        dictionaries from all the workers.

        Args:
            state_dicts: list of encoded state dictionaries as numpy arrays.

        Returns:
            A dictionary of averaged and decoded state dictionaries.
        """
        average_state_dict: dict[str, np.ndarray] = {}
        for field in state_dicts[0]:
            summed_value = self._add([state_dict[field] for state_dict in state_dicts])
            average_decoded_value = self._decode_finite_field(summed_value) / len(
                state_dicts
            )
            average_state_dict[field] = average_decoded_value

        return average_state_dict

    async def do_secure_aggregation(
        self,
        state_dict: Union[_Weights, Mapping[str, np.ndarray]],
        mailbox: _InterPodWorkerMailbox,
    ) -> dict[str, np.ndarray]:
        """Performs secure aggregation.

        This is called on the Pod side before sending the state dict to the
        Modeller.

        Args:
            state_dict: A dictionary of tensors or numpy arrays to be securely
                aggregated.
            mailbox: A mailbox to send and receive messages from other workers.

        Returns:
            A dictionary of encoded numpy arrays.
        """
        logger.info("Performing secure aggregation...")
        await self._share_own_shares(mailbox)
        logger.debug("Shared own shares with other workers.")
        await self._receive_worker_shares(mailbox)
        logger.debug("Received shares from other workers.")
        encoded_reconstructued_update = self._encode_and_reconstruct_state_dict(
            state_dict
        )
        logger.info("Secure aggregation complete.")
        return encoded_reconstructued_update
