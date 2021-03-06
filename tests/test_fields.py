# coding: utf-8

from datetime import datetime, date, time
from decimal import Decimal

import pytest

from edipy import fields, exceptions


@pytest.mark.parametrize('fixed_type, value, expected', [
    (fields.String(1), 'E', 'E'),
    (fields.String(3), 'ENC', 'ENC'),
    (fields.String(8), 'ENCODE  ', 'ENCODE  '),
    (fields.String(8, required=False), '', None),

    (fields.Integer(1), '1', 1),
    (fields.Integer(2), '21', 21),
    (fields.Integer(3), '721', 721),
    (fields.Integer(1, required=False), '', None),

    (fields.Decimal(1), '1', Decimal('1.')),
    (fields.Decimal(2), '21', Decimal('21.')),
    (fields.Decimal(3), '721', Decimal('721.')),
    (fields.Decimal(1, 1), '11', Decimal('1.1')),
    (fields.Decimal(2, 1), '211', Decimal('21.1')),
    (fields.Decimal(3, 1), '7211', Decimal('721.1')),
    (fields.Decimal(1, 2), '211', Decimal('2.11')),
    (fields.Decimal(1, 3), '7211', Decimal('7.211')),
    (fields.Decimal(1, 3, required=False), '', None),

    (fields.DateTime(8, '%d%m%Y'), '23022012', datetime(2012, 2, 23)),
    (fields.DateTime(14, '%d%m%Y%H%M%S'), '23022012235959', datetime(2012, 2, 23, 23, 59, 59)),
    (fields.DateTime(8, '%d%m%Y', required=False), '', None),

    (fields.Date(6, '%d%m%y'), '230212', date(2012, 2, 23)),
    (fields.Date(8, '%d%m%Y'), '23022012', date(2012, 2, 23)),
    (fields.Date(8, '%d%m%Y', required=False), '00000000', None),

    (fields.Time(4, '%H%M'), '2359', time(23, 59)),
    (fields.Time(6, '%H%M%S'), '235959', time(23, 59, 59)),
    (fields.Time(6, '%H%M%S', required=False), '250303', None),

    (fields.Enum(['I', 'A']), 'I', 'I'),
    (fields.Enum(['I', 'A']), 'A', 'A'),
])
def test_encode_data(fixed_type, value, expected):
    assert fixed_type.encode(value) == expected


@pytest.mark.parametrize('fixed_type, value', [
    (fields.String(1, required=True), ''),
    (fields.String(1, required=True), '         '),
    (fields.String(1, required=True), None),
    (fields.Date(6, "%Y%m%d", required=True), 'abcdef'),
])
def test_required_data(fixed_type, value):
    with pytest.raises(exceptions.EDIException):
        fixed_type.encode(value)


def test_register_validate_type():
    class NoEDIModel(object):
        pass

    with pytest.raises(exceptions.BadFormatError):
        fields.Register(NoEDIModel)


def test_register_validate_identifier():
    class MyEDIModel(fields.EDIModel):
        identifier = fields.Integer(3)

    with pytest.raises(exceptions.BadFormatError):
        fields.Register(MyEDIModel)


@pytest.mark.parametrize('occurrences', [0, -1, -10])
def test_register_validate_occurrences(occurrences):
    class MyEDIModel(fields.EDIModel):
        identifier = fields.Identifier("000")

    with pytest.raises(exceptions.BadFormatError):
        fields.Register(MyEDIModel, occurrences=occurrences)


@pytest.mark.parametrize('values', [[], ['AB', 'A']])
def test_enum_validate_format(values):
    with pytest.raises(exceptions.BadFormatError):
        fields.Enum(values)


@pytest.mark.parametrize('choice', ['1', '2', '3'])
def test_enum_validate_contains(choice):
    fixed_type = fields.Enum(['a', 'b', 'c'])
    with pytest.raises(exceptions.ValidationError):
        fixed_type.encode(choice)
