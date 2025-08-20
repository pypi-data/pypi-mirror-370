<?php

declare(strict_types=1);

namespace core\handler;

use Exception;
use ReflectionClass;
use ReflectionException;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class GetStaticFieldHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $classToLoad = $command->getPayload()[0];
        $field = (string) $command->getPayload()[1];

        try {
            $reflectionClass = $this->getReflectionClass($classToLoad);

            if ($reflectionClass->hasConstant($field)) {
                return $reflectionClass->getConstant($field);
            }

            if (!$reflectionClass->hasProperty($field)) {
                $this->throwFieldNotFoundException($reflectionClass, $field);
            }

            $reflectionProperty = $reflectionClass->getProperty($field);
            if (!$reflectionProperty->isStatic()) {
                $this->throwFieldNotFoundException($reflectionClass, $field);
            }

            $reflectionProperty->setAccessible(true);

            return $reflectionProperty->getValue();
        } catch (ReflectionException $e) {
            $this->throwFieldNotFoundException($this->getReflectionClass($classToLoad), $field);
        }
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

    private function throwFieldNotFoundException(ReflectionClass $reflectionClass, string $fieldName): void
    {
        $message = sprintf('Static field %s not found in class %s.
        Available static fields:' . PHP_EOL, $fieldName, $reflectionClass->getName());

        $constants = $reflectionClass->getConstants();
        foreach ($constants as $name => $value) {
            $message .= $name . ' (constant)' . PHP_EOL;
        }

        $properties = $reflectionClass->getProperties();
        foreach ($properties as $property) {
            if ($property->isStatic()) {
                $message .= $property->getName() . ' (property)' . PHP_EOL;
            }
        }

        throw new Exception($message);
    }
}
