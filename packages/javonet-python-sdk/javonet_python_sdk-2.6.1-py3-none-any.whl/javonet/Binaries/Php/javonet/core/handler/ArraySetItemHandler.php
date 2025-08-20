<?php

declare(strict_types=1);

namespace core\handler;

use ArrayAccess;
use core\referencecache\ArrayWrapper;
use Exception;
use InvalidArgumentException;
use utils\CommandInterface;

final class ArraySetItemHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 3;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        $payload = $command->getPayload();
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new InvalidArgumentException(sprintf(
                'Payload array must have at least %d elements for a set operation.',
                self::REQUIRED_ARGUMENTS_COUNT
            ));
        }

        if (is_array($payload[1])) {
            return $this->setArrayElement($command);
        }

        if (is_array($payload[0]) || $payload[0] instanceof ArrayAccess) {
            return $this->setSingleKeyElement($command);
        }

        throw new Exception(sprintf('Cannot set element on target of type %s', gettype($payload[0])));
    }

    private function setArrayElement(CommandInterface $command): int
    {
        $payload = $command->getPayload();
        $array = $payload[0];
        $indexes = $payload[1];
        $value = $payload[2];

        $actualArray = &$this->getActualArray($array);
        $this->setNestedArrayValue($actualArray, $indexes, $value);

        if (!$array instanceof ArrayWrapper) {
            $command->setPayload(0, $actualArray);
        }

        return 0;
    }

    /**
     * @param mixed $array
     */
    private function &getActualArray($array): array
    {
        if ($array instanceof ArrayWrapper) {
            return $array->getData();
        }

        if (is_array($array)) {
            return $array;
        }

        throw new InvalidArgumentException('Target is not an array or ArrayWrapper for multi-index set.');
    }

    /**
     * @param mixed $value
     */
    private function setNestedArrayValue(array &$array, array $indexes, $value): void
    {
        if (empty($indexes)) {
            throw new InvalidArgumentException('Indexes array cannot be empty.');
        }

        $current = &$array;
        $lastIndex = array_pop($indexes);

        foreach ($indexes as $index) {
            if (!isset($current[$index]) || !is_array($current[$index])) {
                $current[$index] = [];
            }
            $current = &$current[$index];
        }

        $current[$lastIndex] = $value;
    }

    /**
     * @return mixed
     */
    private function setSingleKeyElement(CommandInterface $command)
    {
        $payload = $command->getPayload();
        $target = $payload[0];
        $key = $payload[1];
        $value = $payload[2];

        if (!(is_array($target) || $target instanceof ArrayAccess)) {
            throw new InvalidArgumentException('Target for set operation must be an array or ArrayAccess.');
        }

        $oldValue = null;
        if (isset($target[$key])) {
            $oldValue = $target[$key];
        }

        $target[$key] = $value;

        $command->setPayload(0, $target);

        return $oldValue;
    }
}
