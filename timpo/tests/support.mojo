"""Tiny assertion helper for Timpo Mojo tests."""


def expect(cond: Bool, msg: String) raises:
    if not cond:
        raise Error(msg)
