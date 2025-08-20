<?php

declare(strict_types=1);

namespace utils\type;

use utils\Enum;

final class CommandType extends Enum
{
    public const VALUE = 0;
    public const LOAD_LIBRARY = 1;
    public const INVOKE_STATIC_METHOD = 2;
    public const GET_STATIC_FIELD = 3;
    public const SET_STATIC_FIELD = 4;
    public const CREATE_INSTANCE = 5;
    public const GET_TYPE = 6;
    public const REFERENCE = 7;
    public const GET_MODULE = 8;
    public const INVOKE_INSTANCE_METHOD = 9;
    public const EXCEPTION = 10;
    public const HEART_BEAT = 11;
    public const CAST = 12;
    public const GET_INSTANCE_FIELD = 13;
    public const OPTIMIZE = 14;
    public const GENERATE_LIB = 15;
    public const INVOKE_GLOBAL_FUNCTION = 16;
    public const DESTRUCT_REFERENCE = 17;
    public const ARRAY_REFERENCE = 18;
    public const ARRAY_GET_ITEM = 19;
    public const ARRAY_GET_SIZE = 20;
    public const ARRAY_GET_RANK = 21;
    public const ARRAY_SET_ITEM = 22;
    public const ARRAY = 23;
    public const RETRIEVE_ARRAY = 24;
    public const SET_INSTANCE_FIELD = 25;
    public const INVOKE_GENERIC_STATIC_METHOD = 26;
    public const INVOKE_GENERIC_METHOD = 27;
    public const GET_ENUM_ITEM = 28;
    public const GET_ENUM_NAME = 29;
    public const GET_ENUM_VALUE = 30;
    public const AS_REF = 31;
    public const AS_OUT = 32;
    public const GET_REF_VALUE = 33;
    public const ENABLE_NAMESPACE = 34;
    public const ENABLE_TYPE = 35;
    public const CREATE_NULL = 36;
    public const GET_STATIC_METHOD_AS_DELEGATE = 37;
    public const GET_INSTANCE_METHOD_AS_DELEGATE = 38;
    public const PASS_DELEGATE = 39;
    public const INVOKE_DELEGATE = 40;
    public const CONVERT_TYPE = 41;
    public const ADD_EVENT_LISTENER = 42;
    public const PLUGIN_WRAPPER = 43;
    public const GET_ASYNC_OPERATION_RESULT = 44;
}
