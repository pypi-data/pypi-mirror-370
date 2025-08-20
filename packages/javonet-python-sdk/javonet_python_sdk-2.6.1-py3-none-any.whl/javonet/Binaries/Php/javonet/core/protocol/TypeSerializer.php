<?php

declare(strict_types=1);

namespace core\protocol;

use utils\Command;
use utils\exception\TypeSerializationNotSupportedException;
use utils\StringEncodingMode;
use utils\type\{
    JType,
    SizeType
};
use utils\UtilsSimpleType;

final class TypeSerializer
{
    private function __construct()
    {
    }

    /**
     * @param mixed $value
     */
    public static function serializePrimitive($value): array
    {
        if (is_null($value)) {
            return self::serializeNull();
        }

        if (UtilsSimpleType::isChar($value)) {
            return self::serializeChar($value);
        }

        if (is_string($value)) {
            return self::serializeString($value);
        }

        if (is_bool($value)) {
            return self::serializeBool($value);
        }

        if (is_float($value)) {
            return self::serializeDouble($value);
        }

        if (UtilsSimpleType::isFloat($value)) {
            return self::serializeFloat($value);
        }

        if (UtilsSimpleType::isInteger($value)) {
            return self::serializeInt($value);
        }

        if (UtilsSimpleType::isByte($value)) {
            return self::serializeByte($value);
        }

        if (UtilsSimpleType::isLong($value)) {
            return self::serializeLong($value);
        }

        throw new TypeSerializationNotSupportedException($value);
    }

    public static function serializeNull(): array
    {
        return [
            JType::JAVONET_NULL,
            SizeType::JAVONET_NULL_SIZE,
            0
        ];
    }

    public static function serializeString(string $val): array
    {
        $bytes = unpack('C*',mb_convert_encoding($val, 'UTF-8'));
        $buffer[] = JType::JAVONET_STRING;
        $buffer[] = StringEncodingMode::JAVONET_UTF8;
        array_push($buffer, ...self::serializeIntValue(count($bytes)));

        return array_merge($buffer, $bytes);
    }

    public static function serializeInt(int $intVal): array
    {
        return [
            JType::JAVONET_INTEGER,
            SizeType::JAVONET_INTEGER_SIZE,
            $intVal & 0xFF,
            ($intVal >> 8) & 0xFF,
            ($intVal >> 16) & 0xFF,
            ($intVal >> 24) & 0xFF
        ];
    }

    public static function serializeBool(bool $boolValue): array
    {
        return [
            JType::JAVONET_BOOLEAN,
            SizeType::JAVONET_BOOLEAN_SIZE,
            $boolValue ? 1 : 0
        ];
    }

    public static function serializeFloat(float $floatValue): array
    {
        $bytesFloat = unpack('l', pack('f', $floatValue))[1];
        return [
            JType::JAVONET_FLOAT,
            SizeType::JAVONET_FLOAT_SIZE,
            $bytesFloat & 0xFF,
            ($bytesFloat >> 8) & 0xFF,
            ($bytesFloat >> 16) & 0xFF,
            ($bytesFloat >> 24) & 0xFF
        ];
    }

    public static function serializeByte(int $byteValue): array
    {
        return [
            JType::JAVONET_BYTE,
            SizeType::JAVONET_BYTE_SIZE,
            $byteValue & 0xFF
        ];
    }

    public static function serializeChar(string $charValue): array
    {
        return [
            JType::JAVONET_CHAR,
            SizeType::JAVONET_CHAR_SIZE,
            ord($charValue)
        ];
    }

    public static function serializeLong(int $longValue): array
    {
        return [
            JType::JAVONET_LONG,
            SizeType::JAVONET_LONG_SIZE,
            $longValue & 0xFF,
            ($longValue >> 8) & 0xFF,
            ($longValue >> 16) & 0xFF,
            ($longValue >> 24) & 0xFF,
            ($longValue >> 32) & 0xFF,
            ($longValue >> 40) & 0xFF,
            ($longValue >> 48) & 0xFF,
            ($longValue >> 56) & 0xFF,
        ];
    }

    public static function serializeDouble(float $doubleValue): array
    {
        $value = unpack('P', pack('d', $doubleValue))[1];
        return [
            JType::JAVONET_DOUBLE,
            SizeType::JAVONET_DOUBLE_SIZE,
            $value & 0xFF,
            ($value >> 8) & 0xFF,
            ($value >> 16) & 0xFF,
            ($value >> 24) & 0xFF,
            ($value >> 32) & 0xFF,
            ($value >> 40) & 0xFF,
            ($value >> 48) & 0xFF,
            ($value >> 56) & 0xFF,
        ];
    }

    private static function serializeIntValue(int $intValue): array
    {
        return [
            $intValue & 0xFF,
            ($intValue >> 8) & 0xFF,
            ($intValue >> 16) & 0xFF,
            ($intValue >> 24) & 0xFF
        ];
    }

    public static function serializeCommand(Command $cmd): array
    {
        $buffer[] = JType::JAVONET_COMMAND;
        array_push($buffer, ...self::serializeIntValue($cmd->getPayloadSize()));
        $buffer[] = $cmd->getRuntimeName()->getValue();
        $buffer[] = $cmd->getCommandType()->getValue();

        return $buffer;
    }
}