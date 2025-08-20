<?php

declare(strict_types=1);

namespace utils\exception;

use ReflectionClass;
use ReflectionException;

final class FieldNotFoundInClassException extends ReflectionException
{
    public function __construct(string $fieldName, $classToLoad)
    {
        $reflectionClass = $this->getReflectionClass($classToLoad);
        $properties = $reflectionClass->getProperties();

        $message = sprintf(
            'Field %s not found in class %s. Available fields:' . PHP_EOL,
            $fieldName,
            $reflectionClass->getName()
        );

        foreach ($properties as $property) {
            $message .= $property->getName() . PHP_EOL;
        }

        parent::__construct($message);
    }

    /**
     * @param mixed $payload
     */
    private function getReflectionClass($classToLoad): ReflectionClass
    {
        if ($classToLoad instanceof ReflectionClass) {
            return $classToLoad;
        }

        return new ReflectionClass($classToLoad);
    }
}
