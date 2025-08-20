<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionException;
use Exception;
use utils\CommandInterface;
use utils\exception\FieldNotFoundInClassException;
use utils\exception\JavonetArgumentsMismatchException;

final class SetStaticFieldHandler extends AbstractHandler
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

        $classToLoad = $command->getPayloadByIndex(0);
        $fieldName = (string) $command->getPayloadByIndex(1);
        $newValue = $command->getPayloadByIndex(2);

        try {
            $reflectionClass = $this->getReflectionClass($classToLoad);
            if (!$reflectionClass->hasProperty($fieldName)) {
                throw new ReflectionException(sprintf('Property %s not found', $fieldName));
            }

            $property = $reflectionClass->getProperty($fieldName);
            if (!$property->isStatic()) {
                throw new Exception(sprintf('Property %s is not static', $fieldName));
            }

            $property->setAccessible(true);
            $property->setValue(null, $newValue);
        } catch (ReflectionException $e) {
            throw new FieldNotFoundInClassException($fieldName, $classToLoad);
        }

        return 0;
    }

    /**
     * @param mixed $classToLoad
     */
    private function getReflectionClass($classToLoad): ReflectionClass
    {
        if ($classToLoad instanceof ReflectionClass) {
            return $classToLoad;
        }

        return new ReflectionClass($classToLoad);
    }
}
