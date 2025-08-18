import unittest
from dataclasses import dataclass
from typing import Annotated, Optional

import pydantic

from bitstruct_annotated import *


class TestFormats(unittest.TestCase):
    def test_format_unsigned(self):
        self.assertEqual(">u1", Unsigned(1).format_string())
        self.assertEqual("<u11", Unsigned(11, msb_first=False).format_string())

    def test_format_signed(self):
        self.assertEqual(">s2", Signed(2).format_string())
        self.assertEqual("<s12", Signed(12, msb_first=False).format_string())

    def test_format_float(self):
        self.assertEqual(">f3", Float(3).format_string())
        self.assertEqual("<f13", Float(13, msb_first=False).format_string())

    def test_format_bool(self):
        self.assertEqual(">b4", Bool(4).format_string())
        self.assertEqual("<b14", Bool(14, msb_first=False).format_string())

    def test_format_text(self):
        self.assertEqual(">t5", Text(5).format_string())
        self.assertEqual("<t15", Text(15, msb_first=False).format_string())

    def test_format_raw(self):
        self.assertEqual(">r6", Raw(6).format_string())
        self.assertEqual("<r16", Raw(16, msb_first=False).format_string())

    def test_format_padding_zeros(self):
        self.assertEqual(">p7", PaddingZeros(7).format_string())
        self.assertEqual("<p17", PaddingZeros(17, msb_first=False).format_string())

    def test_format_padding_ones(self):
        self.assertEqual(">P8", PaddingOnes(8).format_string())
        self.assertEqual("<P18", PaddingOnes(18, msb_first=False).format_string())


class TestDataclassSimple(unittest.TestCase):
    @dataclass
    class Example:
        unsigned: Annotated[Optional[int], Unsigned(8, default=17)]
        signed: Annotated[Optional[int], Signed(16, msb_first=True, default=-1)]
        float: Annotated[Optional[float], Float(32, msb_first=False, default=3.14)]
        bool: Annotated[Optional[bool], Bool(8, msb_first=False)]
        text: Annotated[str, Text(40)]
        raw: Annotated[bytes, Raw(40)]
        padding_zeros: Annotated[None, PaddingZeros(4)]
        padding_ones: Annotated[None, PaddingOnes(4)]
        ignored: int = 0

    def test_format_string(self):
        self.assertEqual(">u8s16<f32b8>t40r40p4P4", format_string(self.Example))

    def test_field_values(self):
        instance = self.Example(
            unsigned=1,
            signed=-1,
            float=3.14,
            bool=True,
            text="hello",
            raw=b"world",
            padding_zeros=None,
            padding_ones=None,
        )

        self.assertEqual(
            (1, -1, 3.14, True, "hello", b"world"),
            field_values(instance),
        )

    def test_field_values_with_default(self):
        instance = self.Example(
            unsigned=None,
            signed=None,
            float=None,
            bool=True,
            text="hello",
            raw=b"world",
            padding_zeros=None,
            padding_ones=None,
        )

        self.assertEqual(
            (17, -1, 3.14, True, "hello", b"world"),
            field_values(instance),
        )

    def test_field_values_with_missing_default(self):
        instance = self.Example(
            unsigned=1,
            signed=2,
            float=3.14,
            bool=None,
            text="hello",
            raw=b"world",
            padding_zeros=None,
            padding_ones=None,
        )

        with self.assertRaisesRegex(ValueError, "Field 'bool' has no value and no default"):
            field_values(instance)

    def test_pack(self):
        instance = self.Example(
            unsigned=1,
            signed=-1,
            float=3.14,
            bool=True,
            text="hello",
            raw=b"world",
            padding_zeros=None,
            padding_ones=None,
        )

        self.assertEqual(b"\x01\xff\xff\xc3\xaf\x12\x02\x80helloworld\x0f", pack(instance))

    def test_unpack(self):
        data = b"\x01\xff\xff\xc3\xaf\x12\x02\x80helloworld\x0f"
        instance = self.Example(
            unsigned=0,
            signed=0,
            float=0.0,
            bool=False,
            text="",
            raw=b"",
            padding_zeros=None,
            padding_ones=None,
        )

        unpack(instance, data)

        self.assertEqual(1, instance.unsigned)
        self.assertEqual(-1, instance.signed)
        self.assertEqual(3.14, round(instance.float, 2))
        self.assertEqual(True, instance.bool)
        self.assertEqual("hello", instance.text)
        self.assertEqual(b"world", instance.raw)
        self.assertEqual(None, instance.padding_zeros)
        self.assertEqual(None, instance.padding_ones)


class TestDataclassReordering(unittest.TestCase):
    def test_no_fields__pass(self):
        @dataclass
        class Example:
            pass

        self.assertEqual("", format_string(Example))

    def test_invalid_empty_ordering_constraint__fail(self):
        with self.assertRaisesRegex(ValueError, "Invalid ordering constraint: ''"):

            @dataclass
            class Example:
                field0: Annotated[None, Bool(1, order="")]

    def test_invalid_single_part_constraint__fail(self):
        with self.assertRaisesRegex(ValueError, "Invalid ordering constraint: 'invalid'"):

            @dataclass
            class Example:
                field0: Annotated[None, Bool(1, order="invalid")]

    def test_invalid_two_part_constraint__fail(self):
        with self.assertRaisesRegex(ValueError, "Invalid ordering constraint: 'invalid:invalid'"):

            @dataclass
            class Example:
                field0: Annotated[None, Bool(1, order="invalid:invalid")]

    def test_invalid_multi_part_constraint__fail(self):
        with self.assertRaisesRegex(ValueError, "Invalid ordering constraint: 'invalid:invalid:invalid'"):

            @dataclass
            class Example:
                field0: Annotated[None, Bool(1, order="invalid:invalid:invalid")]

    def test_two_first_fields__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="first")]
            field1: Annotated[None, Bool(1, order="first")]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field1' has 'first' constraint but is not the first field",
            format_string,
            Example,
        )

    def test_two_last_fields__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="last")]
            field1: Annotated[None, Bool(1, order="last")]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field0' has 'last' constraint but is not the last field",
            format_string,
            Example,
        )

    def test_reference_to_missing_field__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:missing")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_before_first_field__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:field1")]
            field1: Annotated[None, Bool(1, order="first")]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field1' has 'first' constraint but is not the first field",
            format_string,
            Example,
        )

    def test_after_last_field__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="after:field1")]
            field1: Annotated[None, Bool(1, order="last")]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field1' has 'last' constraint but is not the last field",
            format_string,
            Example,
        )

    def test_before_conflict_direct__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:field1")]
            field1: Annotated[None, Bool(1, order="before:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_before_conflict_indirect__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:field1")]
            field1: Annotated[None, Bool(1, order="before:field2")]
            field2: Annotated[None, Bool(1, order="before:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_before_two_fields_conflict__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:field2")]
            field1: Annotated[None, Bool(1, order="before:field2")]
            field2: Annotated[None, Bool(1)]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field0' has 'before' constraint but the next field is not 'field2'",
            format_string,
            Example,
        )

    def test_after_two_fields_conflict__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1)]
            field1: Annotated[None, Bool(1, order="after:field0")]
            field2: Annotated[None, Bool(1, order="after:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Field 'field1' has 'after' constraint but the previous field is not 'field0'",
            format_string,
            Example,
        )

    def test_after_conflict_direct__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="after:field1")]
            field1: Annotated[None, Bool(1, order="after:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_after_conflict_indirect__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="after:field1")]
            field1: Annotated[None, Bool(1, order="after:field2")]
            field2: Annotated[None, Bool(1, order="after:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_multiple_before_conflict__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="before:field2")]
            field1: Annotated[None, Bool(1, order="before:field2")]
            field2: Annotated[None, Bool(1, order="before:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_multiple_after_conflict__fail(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="after:field2")]
            field1: Annotated[None, Bool(1, order="after:field2")]
            field2: Annotated[None, Bool(1, order="after:field0")]

        self.assertRaisesRegex(
            ValueError,
            "Could not satisfy constraints of fields",
            format_string,
            Example,
        )

    def test_valid_example__pass(self):
        @dataclass
        class Example:
            field0: Annotated[None, Bool(1, order="last")]
            field1: Annotated[None, Bool(1, order="first")]
            field2: Annotated[None, Bool(1, msb_first=False)]
            field3: Annotated[None, Bool(1, order="after:field1")]
            field4: Annotated[None, Bool(1, order="before:field0")]

        self.assertEqual(">b1b1<b1>b1b1", format_string(Example))


class TestDataclassInheritance(unittest.TestCase):
    @dataclass
    class Base:
        base_field: Annotated[bool, Bool(1)]

    @dataclass
    class Derived(Base):
        derived_field: Annotated[bool, Bool(1)]

    def test_format_string(self):
        self.assertEqual(">b1b1", format_string(self.Derived))

    def test_field_values(self):
        instance = self.Derived(base_field=True, derived_field=False)
        self.assertEqual((True, False), field_values(instance))

    def test_pack(self):
        instance = self.Derived(base_field=True, derived_field=False)
        self.assertEqual(b"\x80", pack(instance))

    def test_unpack(self):
        instance = self.Derived(base_field=True, derived_field=True)
        unpack(instance, b"\xC0")
        self.assertEqual(True, instance.base_field)
        self.assertEqual(True, instance.derived_field)


class TestDataclassNesting(unittest.TestCase):
    @dataclass
    class Inner:
        first_inner_field: Annotated[int, Unsigned(4)]
        second_inner_field: Annotated[int, Unsigned(8)]

    def test_format_string(self):
        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(12)]
            inner: Annotated[TestDataclassNesting.Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(16)]

        self.assertEqual(">u12u4u8u16", format_string(Outer))

    def test_field_values(self):
        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(12)]
            inner: Annotated[TestDataclassNesting.Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(16)]

        instance = Outer(1, self.Inner(2, 3), 4)
        self.assertEqual((1, 2, 3, 4), field_values(instance))

    def test_pack(self):
        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(12)]
            inner: Annotated[TestDataclassNesting.Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(16)]

        instance = Outer(1, self.Inner(2, 3), 4)
        self.assertEqual(b"\x00\x12\x03\x00\x04", pack(instance))

    def test_unpack(self):
        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(12)]
            inner: Annotated[TestDataclassNesting.Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(16)]

        instance = Outer(0, self.Inner(0, 0), 0)
        unpack(instance, b"\x00\x12\x03\x00\x04")
        self.assertEqual(1, instance.first_outer_field)
        self.assertEqual(2, instance.inner.first_inner_field)
        self.assertEqual(3, instance.inner.second_inner_field)
        self.assertEqual(4, instance.second_outer_field)


class TestDataclassDoubleNesting(unittest.TestCase):
    @dataclass
    class Innermost:
        innermost_field: Annotated[int, Unsigned(4)]

    def test_format_string(self):
        @dataclass
        class Inner:
            first_inner_field: Annotated[int, Unsigned(8)]
            innermost: Annotated[TestDataclassDoubleNesting.Innermost, Nested()]
            second_inner_field: Annotated[int, Unsigned(16)]

        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(20)]
            inner: Annotated[Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(24)]

        self.assertEqual(">u20u8u4u16u24", format_string(Outer))

    def test_field_values(self):
        @dataclass
        class Inner:
            first_inner_field: Annotated[int, Unsigned(8)]
            innermost: Annotated[TestDataclassDoubleNesting.Innermost, Nested()]
            second_inner_field: Annotated[int, Unsigned(16)]

        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(20)]
            inner: Annotated[Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(24)]

        instance = Outer(1, Inner(2, TestDataclassDoubleNesting.Innermost(3), 4), 5)
        self.assertEqual((1, 2, 3, 4, 5), field_values(instance))

    def test_pack(self):
        @dataclass
        class Inner:
            first_inner_field: Annotated[int, Unsigned(8)]
            innermost: Annotated[TestDataclassDoubleNesting.Innermost, Nested()]
            second_inner_field: Annotated[int, Unsigned(16)]

        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(20)]
            inner: Annotated[Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(24)]

        instance = Outer(1, Inner(2, TestDataclassDoubleNesting.Innermost(3), 4), 5)
        self.assertEqual(b"\x00\x00\x10\x23\x00\x04\x00\x00\x05", pack(instance))

    def test_unpack(self):
        @dataclass
        class Inner:
            first_inner_field: Annotated[int, Unsigned(8)]
            innermost: Annotated[TestDataclassDoubleNesting.Innermost, Nested()]
            second_inner_field: Annotated[int, Unsigned(16)]

        @dataclass
        class Outer:
            first_outer_field: Annotated[int, Unsigned(20)]
            inner: Annotated[Inner, Nested()]
            second_outer_field: Annotated[int, Unsigned(24)]

        instance = Outer(0, Inner(0, TestDataclassDoubleNesting.Innermost(0), 0), 0)
        unpack(instance, b"\x00\x00\x10\x23\x00\x04\x00\x00\x05")
        self.assertEqual(1, instance.first_outer_field)
        self.assertEqual(2, instance.inner.first_inner_field)
        self.assertEqual(3, instance.inner.innermost.innermost_field)
        self.assertEqual(4, instance.inner.second_inner_field)
        self.assertEqual(5, instance.second_outer_field)


@dataclass
class ComplexExample:
    payload_length: Annotated[int, Unsigned(8)]
    payload: Annotated[bytes, Raw(32)]

    @dataclass
    class Header:
        description: str
        packet_id: Annotated[int, Unsigned(8, order="first")]
        destination_name: Annotated[str, Text(32, order="after:packet_id")]
        source_name: Annotated[str, Text(32, order="after:destination_name")]

    header: Annotated[Header, Nested()]

    @dataclass
    class Footer:
        checksum: Annotated[int, Unsigned(16)]
        padding: Annotated[None, PaddingZeros(4)]

    footer: Annotated[Footer, Nested()]


class TestDataclassComplex(unittest.TestCase):
    def setUp(self):
        self.instance = ComplexExample(
            header=ComplexExample.Header(
                description="Test packet",
                packet_id=1,
                destination_name="Dest",
                source_name="Src ",
            ),
            payload_length=5,
            payload=b"test",
            footer=ComplexExample.Footer(checksum=0x1234, padding=None),
        )

    def test_format_string(self):
        self.assertEqual(
            ">u8t32t32u8r32u16p4",
            format_string(self.instance),
        )

    def test_field_values(self):
        self.assertEqual(
            (
                1,
                "Dest",
                "Src ",
                5,
                b"test",
                0x1234,
            ),
            field_values(self.instance),
        )

    def test_pack(self):
        self.assertEqual(
            b"\x01DestSrc \x05test\x12\x34\x00",
            pack(self.instance),
        )

    def test_unpack(self):
        instance = ComplexExample(
            header=ComplexExample.Header(
                description="",
                packet_id=0,
                destination_name="",
                source_name="",
            ),
            payload_length=0,
            payload=b"",
            footer=ComplexExample.Footer(checksum=0, padding=None),
        )

        unpack(instance, b"\x01DestSrc \x05test\x12\x34\x00")

        self.assertEqual(1, instance.header.packet_id)
        self.assertEqual("Dest", instance.header.destination_name)
        self.assertEqual("Src ", instance.header.source_name)
        self.assertEqual(5, instance.payload_length)
        self.assertEqual(b"test", instance.payload)
        self.assertEqual(0x1234, instance.footer.checksum)
        self.assertIsNone(instance.footer.padding)


class PydanticExample(pydantic.BaseModel):
    car_make: Annotated[str, pydantic.Field(max_length=32), Text(32, order="first")]
    car_model: Annotated[str, pydantic.Field(max_length=32), Text(32, order="after:car_make")]
    car_year: Annotated[int, pydantic.Field(ge=1900, le=2100), Unsigned(16, order="last")]


class TestPydantic(unittest.TestCase):
    def setUp(self):
        self.instance = PydanticExample(
            car_make="Toyo",
            car_model="Coro",
            car_year=2021,
        )

    def test_format_string(self):
        self.assertEqual(
            ">t32t32u16",
            format_string(self.instance),
        )

    def test_field_values(self):
        self.assertEqual(
            (
                "Toyo",
                "Coro",
                2021,
            ),
            field_values(self.instance),
        )

    def test_pack(self):
        self.assertEqual(
            b"ToyoCoro\x07\xe5",
            pack(self.instance),
        )

    def test_unpack(self):
        instance = PydanticExample(
            car_make="",
            car_model="",
            car_year=1900,
        )

        unpack(instance, b"ToyoCoro\x07\xe5")

        self.assertEqual("Toyo", instance.car_make)
        self.assertEqual("Coro", instance.car_model)
        self.assertEqual(2021, instance.car_year)


if __name__ == "__main__":
    unittest.main()
