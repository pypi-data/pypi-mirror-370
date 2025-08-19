__all__ = ['StochasticRounding']

import numcodecs.abc

class StochasticRounding(numcodecs.abc.Codec):
    r"""
    Codec that stochastically rounds the data to the nearest multiple of
    `precision` on encoding and passes through the input unchanged during
    decoding.
    
    The nearest representable multiple is chosen such that the absolute
    difference between the original value and the rounded value do not exceed
    the precision. Therefore, the rounded value may have a non-zero remainder.
    
    This codec first hashes the input array data and shape to then `seed` a
    pseudo-random number generator that is used to sample the stochasticity for
    rounding. Therefore, passing in the same input with the same `seed` will
    produce the same stochasticity and thus the same encoded output.
    
    Parameters
    ----------
    precision : ...
        The precision of the rounding operation
    seed : ...
        Seed for the random generator
    _version : ..., optional, default = "1.0.0"
        The codec's encoding format version. Do not provide this parameter explicitly.
    """

    def __init__(self, precision, seed, _version='1.0.0'): ...

    codec_id = 'stochastic-rounding.rs'

    def decode(self, buf, out=None):
        r"""
        Decode the data in `buf`.
        
        Parameters
        ----------
        buf : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        out : Buffer, optional
            Writeable buffer to store decoded data. N.B. if provided, this buffer must
            be exactly the right size to store the decoded data.
        
        Returns
        -------
        dec : Buffer
            Decoded data. May be any object supporting the new-style
            buffer protocol.
        """
        ...

    def encode(self, buf):
        r"""
        Encode the data in `buf`.
        
        Parameters
        ----------
        buf : Buffer
            Data to be encoded. May be any object supporting the new-style
            buffer protocol.
        
        Returns
        -------
        enc : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        """
        ...

    @classmethod
    def from_config(cls, config):
        r"""
        Instantiate the codec from a configuration [`dict`][dict].
        
        Parameters
        ----------
        config : dict
            Configuration of the codec.
        
        Returns
        -------
        codec : Self
            Instantiated codec.
        """
        ...

    def get_config(self):
        r"""
        Returns the configuration of the codec.
        
        [`numcodecs.registry.get_codec(config)`][numcodecs.registry.get_codec]
        can be used to reconstruct this codec from the returned config.
        
        Returns
        -------
        config : dict
            Configuration of the codec.
        """
        ...
