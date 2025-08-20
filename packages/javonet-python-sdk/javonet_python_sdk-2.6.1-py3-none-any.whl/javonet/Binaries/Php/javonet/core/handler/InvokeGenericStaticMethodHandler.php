<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionMethod;
use ReflectionException;
use ReflectionType;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class InvokeGenericStaticMethodHandler extends AbstractHandler
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

        $payload = $command->getPayload();
        $className = $payload[0];
        $methodToInvoke = (string) $payload[1];
        $arguments = array_slice($payload, 2);

        try {
            [$reflectionClass, $className] = $this->getReflectionClassAndName($className);
            if (!$reflectionClass->hasMethod($methodToInvoke)) {
                $this->throwMethodNotFoundError($reflectionClass, $methodToInvoke, $arguments);
            }

            $method = $reflectionClass->getMethod($methodToInvoke);
            if (!$method->isStatic()) {
                throw new ReflectionException(sprintf(
                    'Method %s in class %s is not static',
                        $methodToInvoke,
                        $className
                    )
                );
            }

            return $method->invokeArgs(null, $arguments);

        } catch (ReflectionException $e) {
            if (strpos($e->getMessage(), 'Class') === 0) {
                throw new ReflectionException(sprintf('Class: %s not found', $this->getReflectionClassName($className)));
            }
            throw $e;
        }
    }

    private function throwMethodNotFoundError(
        ReflectionClass $reflectionClass,
        string $methodToInvoke,
        array $arguments
    ): void {
        $className = $reflectionClass->getName();
        $argumentTypes = array_map('gettype', $arguments);

        $message = sprintf('Generic static method %s with arguments ['
                   . implode(', ', $argumentTypes)
                   . '] not found in class %s. Available methods:' . PHP_EOL, $methodToInvoke, $className);

        $methods = $reflectionClass->getMethods(ReflectionMethod::IS_STATIC | ReflectionMethod::IS_PUBLIC);

        foreach ($methods as $method) {
            $parameterTypes = array_map(function($param) {
                return $this->getParamTypeName($param->getType());
            }, $method->getParameters());
            $message .= $method->getName() . ' with arguments ['. implode(', ', $parameterTypes) . "]\n";
        }

        throw new ReflectionException($message);
    }

    /**
     * @param mixed $payload
     */
    private function getReflectionClassAndName($classToLoad): array
    {
        if ($classToLoad instanceof ReflectionClass) {
            return [$classToLoad, $classToLoad->getName()];
        }

        return [new ReflectionClass($classToLoad), (string) $classToLoad];
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
