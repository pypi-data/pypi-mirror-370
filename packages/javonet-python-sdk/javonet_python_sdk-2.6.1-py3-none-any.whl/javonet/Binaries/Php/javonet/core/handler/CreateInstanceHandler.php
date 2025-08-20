<?php

declare(strict_types=1);

namespace core\handler;

use Exception;
use ReflectionClass;
use ReflectionException;
use ReflectionMethod;
use ReflectionType;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class CreateInstanceHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    /**
     * @return object
     */
    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class, self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $payload = $command->getPayload();
        $arguments = [];
        try {
            $reflectionClass = $this->getReflectionClass($payload[0]);
            if (count($payload) === 1) {
                return $reflectionClass->newInstance();
            }

            $arguments = array_slice($payload, 1);
            $handlerInstance = $reflectionClass->newInstanceArgs($arguments);
            if (null === $handlerInstance) {
                throw new ReflectionException();
            }

            return $handlerInstance;
        } catch (ReflectionException $e) {
            try {
                $className = $reflectionClass->getName();

                return new $className(...$arguments);
            } catch (Exception $fallbackException) {
                $constructors = $reflectionClass->getConstructor();
                $message = sprintf(
                    'Constructor with arguments %s not found in class %s. Fallback also failed: %s',
                    json_encode($arguments),
                    $this->getReflectionClassName($payload[0]),
                    $fallbackException->getMessage()
                );
            }

            if ($constructors instanceof ReflectionMethod) {
                $paramTypes = [];
                foreach ($constructors->getParameters() as $param) {
                    $paramTypes[] = $this->getParamTypeName($param->getType());
                }
                $message .= ' Available constructor: (' . implode(', ', $paramTypes) . ')';
            }
            throw new ReflectionException($message);
        }
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

    /**
     * @param mixed $payload
     */
    private function getReflectionClassName($classToLoad): string
    {
        if ($classToLoad instanceof ReflectionClass) {
            return $classToLoad->getName();
        }

        return (string) $classToLoad;
    }

    private function getParamTypeName(?ReflectionType $paramType): string
    {
        if ($paramType) {
            return $paramType->getName();
        }

        return 'mixed';
    }
}
