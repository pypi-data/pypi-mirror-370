<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionException;
use ReflectionMethod;
use ReflectionType;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class GetStaticMethodAsDelegateHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

    public function process(CommandInterface $command): ReflectionMethod
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $payload = $command->getPayload();
        $classToLoad = $payload[0];
        $methodToInvoke = (string) $payload[1];
        $argumentsTypes = array_slice($payload, 2);

        try {
            $reflectionClass = $this->getReflectionClass($classToLoad);
            if (!$reflectionClass->hasMethod($methodToInvoke)) {
                $this->throwMethodNotFoundException($reflectionClass, $methodToInvoke, $argumentsTypes);
            }

            $foundMethod = $reflectionClass->getMethod($methodToInvoke);
            if (!$foundMethod->isStatic()) {
                throw new ReflectionException(sprintf('Method %s is not a static method in the class.', $reflectionClass->getName()));
            }

            return $foundMethod;

        } catch (ReflectionException $e) {

            if (strpos($e->getMessage(), 'does not exist') !== false) {
                throw new ReflectionException(sprintf(
                    'Class: %s does not exist',
                    $this->getReflectionClassName($classToLoad)
                ));
            }
            throw $e;
        }
    }

    private function throwMethodNotFoundException(
        ReflectionClass $reflectionClass,
        string $methodName,
        array $argumentsTypes
    ): void {
        $methods = $reflectionClass->getMethods(ReflectionMethod::IS_STATIC);
        $argumentsTypesStr = implode(', ', array_map('gettype', $argumentsTypes));

        $message = sprintf(
            'Static method %s with arguments [%s] was not found in class %s}. Available static methods:' . PHP_EOL,
            $methodName,
            $argumentsTypesStr,
            $reflectionClass->getName()
        );
        foreach ($methods as $method) {
            $paramTypes = array_map(function($param) {
                return $this->getParamTypeName($param->getType());
            }, $method->getParameters());

            $paramTypesStr = implode(', ', $paramTypes);
            $message .= $method->getName() . 'with arguments [ ' . $paramTypesStr . ']' . PHP_EOL;
        }

        throw new ReflectionException($message);
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

    /**
     * @param mixed $classToLoad
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
