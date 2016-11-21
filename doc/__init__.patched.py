# Patched \Lib\site-packages\cryptography\hazmat\backends\__init__.py

"""
# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import pkg_resources

from cryptography.hazmat.backends.multibackend import MultiBackend


_available_backends_list = None


def _available_backends():
    global _available_backends_list

    if _available_backends_list is None:
        _available_backends_list = [
            ep.resolve()
            for ep in pkg_resources.iter_entry_points(
                "cryptography.backends"
            )
        ]

    return _available_backends_list

_default_backend = None


def default_backend():
    global _default_backend

    if _default_backend is None:
        _default_backend = MultiBackend(_available_backends())

    return _default_backend
"""
	
# To put that all together.. This is the replacement hazmat/backends/__init__.py
# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import pkg_resources

from cryptography.hazmat.backends.multibackend import MultiBackend


_available_backends_list = None
def patch_crypto_be_discovery():

    """
        Monkey patches cryptography's backend detection.
        Objective: support pyinstaller freezing.
        """

    from cryptography.hazmat import backends

    try:
        from cryptography.hazmat.backends.commoncrypto.backend import backend as be_cc
    except ImportError:
        be_cc = None

    try:
        from cryptography.hazmat.backends.openssl.backend import backend as be_ossl
    except ImportError:
        be_ossl = None

    backends._available_backends_list = [
        be for be in (be_cc, be_ossl) if be is not None
         ]
    return backends._available_backends_list

def _available_backends():
    global _available_backends_list

    if _available_backends_list is None:
        _available_backends_list = [
            # setuptools 11.3 deprecated support for the require parameter to
            # load(), and introduced the new resolve() method instead.
            # This can be removed if/when we can assume setuptools>=11.3. At
            # some point we may wish to add a warning, to push people along,
            # but at present this would result in too many warnings.
            ep.resolve() if hasattr(ep, "resolve") else ep.load(require=False)
            for ep in pkg_resources.iter_entry_points(
                "cryptography.backends"
            )
        ]
        if len(_available_backends_list) == 0:
            _available_backends_list = patch_crypto_be_discovery()
    return _available_backends_list

_default_backend = None


def default_backend():
    global _default_backend

    if _default_backend is None:
        _default_backend = MultiBackend(_available_backends())

    return _default_backend
