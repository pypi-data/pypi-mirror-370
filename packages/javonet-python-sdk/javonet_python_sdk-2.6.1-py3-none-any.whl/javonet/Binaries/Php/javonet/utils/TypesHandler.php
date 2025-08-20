<?php

declare(strict_types=1);

namespace utils;

use ReflectionType;
use utils\type\JType;

final class TypesHandler
{
    private function __construct()
    {
    }

    public static function convertTypeToJavonetType(ReflectionType $type): string
    {
        $typeName = $type->getName();
        switch ($typeName) {
            case 'bool':
                return JType::JAVONET_BOOLEAN()->getName();
            case 'string':
                return JType::JAVONET_STRING()->getName();
            case 'char':
                return JType::JAVONET_CHAR()->getName();
            case 'int':
                return JType::JAVONET_INT()->getName();
            case 'float':
                return JType::JAVONET_FLOAT()->getName();
            case 'double':
                return JType::JAVONET_DOUBLE()->getName();
            case 'null':
                return JType::JAVONET_NULL()->getName();
            default:
                return $typeName;
        }
    }


    /**
     * @param mixed $item
     */
    public static function isSimpleType($item): bool
    {
        return $item === null || is_scalar($item)
            || (is_object($item) && in_array(get_class($item), [
                    'string', 'int', 'float', 'bool', 'double', 'null'
                ], true));
    }
}
