#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Tecton's comment:
This is a backport from pyspark 3.5.1
We need it because of the fixed spark -> arrow schema conversion.
pyspark 3.1 doesn't support TimestampType nested into Map or Struct
"""

from typing import TYPE_CHECKING

from pyspark.sql.types import (
    BooleanType,
    ByteType,
    ShortType,
    IntegerType,
    IntegralType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
    StringType,
    BinaryType,
    DateType,
    TimestampType,
    ArrayType,
    MapType,
    StructType,
    StructField,
    NullType,
    DataType,
    UserDefinedType,
    Row,
    _create_row,
)

if TYPE_CHECKING:
    import pyarrow as pa


def to_arrow_type(dt: DataType) -> "pa.DataType":
    """Convert Spark data type to pyarrow type"""
    from distutils.version import LooseVersion
    import pyarrow as pa

    if type(dt) == BooleanType:
        arrow_type = pa.bool_()
    elif type(dt) == ByteType:
        arrow_type = pa.int8()
    elif type(dt) == ShortType:
        arrow_type = pa.int16()
    elif type(dt) == IntegerType:
        arrow_type = pa.int32()
    elif type(dt) == LongType:
        arrow_type = pa.int64()
    elif type(dt) == FloatType:
        arrow_type = pa.float32()
    elif type(dt) == DoubleType:
        arrow_type = pa.float64()
    elif type(dt) == DecimalType:
        arrow_type = pa.decimal128(dt.precision, dt.scale)
    elif type(dt) == StringType:
        arrow_type = pa.string()
    elif type(dt) == BinaryType:
        arrow_type = pa.binary()
    elif type(dt) == DateType:
        arrow_type = pa.date32()
    # TODO: use pyspark type instead of name when we upgrade to Spark 3.4+
    elif type(dt) == TimestampType or dt.simpleString() == 'timestamp_ntz':
        # Timestamps should be in UTC, JVM Arrow timestamps require a timezone to be read
        arrow_type = pa.timestamp("us", tz="UTC")
    elif type(dt) == ArrayType:
        field = pa.field("element", to_arrow_type(dt.elementType), nullable=dt.containsNull)
        arrow_type = pa.list_(field)
    elif type(dt) == MapType:
        key_field = pa.field("key", to_arrow_type(dt.keyType), nullable=False)
        value_field = pa.field("value", to_arrow_type(dt.valueType), nullable=dt.valueContainsNull)
        arrow_type = pa.map_(key_field, value_field)
    elif type(dt) == StructType:
        fields = [
            pa.field(field.name, to_arrow_type(field.dataType), nullable=field.nullable)
            for field in dt
        ]
        arrow_type = pa.struct(fields)
    elif type(dt) == NullType:
        arrow_type = pa.null()
    elif isinstance(dt, UserDefinedType):
        arrow_type = to_arrow_type(dt.sqlType())
    else:
        raise TypeError("Unsupported type in conversion to Arrow: " + str(dt))
    return arrow_type


def to_arrow_schema(schema: StructType) -> "pa.Schema":
    """Convert a schema from Spark to Arrow"""
    import pyarrow as pa

    fields = [
        pa.field(field.name, to_arrow_type(field.dataType), nullable=field.nullable)
        for field in schema
    ]
    return pa.schema(fields)


def from_arrow_type(at: "pa.DataType", prefer_timestamp_ntz: bool = False) -> DataType:
    """Convert pyarrow type to Spark data type."""
    from distutils.version import LooseVersion
    import pyarrow as pa
    import pyarrow.types as types

    spark_type: DataType
    if types.is_boolean(at):
        spark_type = BooleanType()
    elif types.is_int8(at):
        spark_type = ByteType()
    elif types.is_int16(at):
        spark_type = ShortType()
    elif types.is_int32(at):
        spark_type = IntegerType()
    elif types.is_int64(at):
        spark_type = LongType()
    elif types.is_float32(at):
        spark_type = FloatType()
    elif types.is_float64(at):
        spark_type = DoubleType()
    elif types.is_decimal(at):
        spark_type = DecimalType(precision=at.precision, scale=at.scale)
    elif types.is_string(at):
        spark_type = StringType()
    elif types.is_large_string(at):
        spark_type = StringType()
    elif types.is_binary(at):
        spark_type = BinaryType()
    elif types.is_large_binary(at):
        spark_type = BinaryType()
    elif types.is_date32(at):
        spark_type = DateType()
    elif types.is_timestamp(at):
        spark_type = TimestampType()
    elif types.is_list(at):
        spark_type = ArrayType(from_arrow_type(at.value_type, prefer_timestamp_ntz))
    elif types.is_map(at):
        spark_type = MapType(
            from_arrow_type(at.key_type, prefer_timestamp_ntz),
            from_arrow_type(at.item_type, prefer_timestamp_ntz),
        )
    elif types.is_struct(at):
        return StructType(
            [
                StructField(
                    field.name,
                    from_arrow_type(field.type, prefer_timestamp_ntz),
                    nullable=field.nullable,
                )
                for field in at
            ]
        )
    elif types.is_dictionary(at):
        spark_type = from_arrow_type(at.value_type, prefer_timestamp_ntz)
    elif types.is_null(at):
        spark_type = NullType()
    else:
        raise TypeError("Unsupported type in conversion from Arrow: " + str(at))
    return spark_type


def from_arrow_schema(arrow_schema: "pa.Schema", prefer_timestamp_ntz: bool = False) -> StructType:
    """Convert schema from Arrow to Spark."""
    return StructType(
        [
            StructField(
                field.name,
                from_arrow_type(field.type, prefer_timestamp_ntz),
                nullable=field.nullable,
            )
            for field in arrow_schema
        ]
    )
