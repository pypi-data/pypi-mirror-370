<?php

declare(strict_types=1);

namespace core\handler;

use TypeError;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class CastHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        $payload = $command->getPayload();
        if ($command->getPayloadSize() !== self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(self::class, self::REQUIRED_ARGUMENTS_COUNT);
        }

        $newType = $payload[0];
        $value = $payload[1];

        if (is_array($value) && $this->isArrayType($newType)) {
            $newBaseType = $this->getArrayBaseType($newType);
            $castedArray = [];
            foreach ($value as $item) {
                $castedArray[] = $this->castValue($newBaseType, $item);
            }

            return $castedArray;
        }

        $newBaseType = $this->isArrayType($newType) ? $this->getArrayBaseType($newType) : $newType;

        return $this->castValue($newBaseType, $value);
    }

    private function isArrayType(string $type): bool
    {
        return substr($type, -2) === '[]';
    }

    private function getArrayBaseType(string $type): string
    {
        return substr($type, 0, -2);
    }

    /**
     * @param mixed $value
     * @return mixed
     */
    private function castValue(string $newBaseType, $value)
    {
        if (is_null($value)) {
            return null;
        }

        if (is_object($value)) {
            if (is_a($value, $newBaseType)) {
                return $value;
            }
        }

        switch (strtolower($newBaseType)) {
            case 'byte':
            case 'short':
            case 'int':
            case 'integer':
            case 'long':
                return (int)$value;
            case 'float':
            case 'double':
                return (float)$value;
            case 'char':
            case 'character':
            case 'string':
                return (string)$value;
            case 'bool':
            case 'boolean':
                return (bool)$value;
        }

        if (gettype($value) === $newBaseType) {
            return $value;
        }

        $valueType = is_object($value) ? get_class($value) : gettype($value);

        throw new TypeError('PHP Cast Handler: Cannot cast ' . $valueType . ' to ' . $newBaseType);
    }
}
