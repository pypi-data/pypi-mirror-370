<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionException;
use utils\CommandInterface;
use utils\exception\FieldNotFoundInClassException;
use utils\exception\JavonetArgumentsMismatchException;

final class SetInstanceFieldHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 3;

    public function process(CommandInterface $command): int
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
            self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $objectInstance = $command->getPayloadByIndex(0);
        $fieldName = (string) $command->getPayloadByIndex(1);
        $newValue = $command->getPayloadByIndex(2);

        try {
            $reflectionClass = new ReflectionClass($objectInstance);
            $property = $reflectionClass->getProperty($fieldName);
            $property->setAccessible(true);
            $property->setValue($objectInstance, $newValue);
        } catch (ReflectionException $e) {
            throw new FieldNotFoundInClassException($fieldName, $objectInstance);
        }

        return 0;
    }
}
