# ========================================================================================
#  Copyright (C) 2025 CryptoLab Inc. All rights reserved.
#
#  This software is proprietary and confidential.
#  Unauthorized use, modification, reproduction, or redistribution is strictly prohibited.
#
#  Commercial use is permitted only under a separate, signed agreement with CryptoLab Inc.
#
#  For licensing inquiries or permission requests, please contact: pypi@cryptolab.co.kr
# ========================================================================================

from typing import List, Optional, Union

import evi
from evi import SingleCiphertext

from proto.es2_comm_type_pb2 import CiphertextScore


class CipherBlock:
    """
    CipherBlock class for handling ciphertexts.

    Ciphertexts can be either an encrypted vector or an encrypted similarity scores.
    """

    def __init__(self, data: Union[List[SingleCiphertext], CiphertextScore], enc_type: Optional[str] = None):
        self._is_score = None
        self.data = data
        self.enc_type = enc_type

    @property
    def data(self):
        return self._data

    @property
    def enc_type(self):
        return self._enc_type

    @enc_type.setter
    def enc_type(self, value: Optional[str]):
        if value and value not in ["multiple", "single"]:
            raise ValueError("Invalid enc_type. Must be 'multiple' or 'single'.")
        self._enc_type = value

    @data.setter
    def data(self, value: Union[List[SingleCiphertext], CiphertextScore]):
        if not value:
            raise ValueError("Data list cannot be empty.")
        if isinstance(value, CiphertextScore):
            self._is_score = True
        elif isinstance(value, list) and all(isinstance(v, SingleCiphertext) for v in value):
            self._is_score = False
        else:
            raise ValueError("Data must be a list of SingleCiphertext or CiphertextScore.")
        self._data = value

    def serialize(self) -> bytes:
        """
        Serializes the CipherBlock to bytes.

        Returns:
            bytes: Serialized bytes of the CipherBlock.
        """
        if self._is_score is True:
            raise ValueError("CipherBlock data must be set before serialization.")
        return evi.serialize_query_to(self.data)
