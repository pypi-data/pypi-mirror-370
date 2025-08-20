<?php

declare(strict_types=1);

namespace core\handler;

use BadMethodCallException;
use ReflectionClass;
use ReflectionMethod;
use ReflectionException;
use RuntimeException;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class InvokeStaticMethodHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

    public function process(CommandInterface $command)
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
        $arguments = array_slice($payload, 2);

        try {
            $reflectionClass = $this->getReflectionClass($classToLoad);
            if (!$reflectionClass->hasMethod($methodToInvoke)) {
                $this->throwMethodNotFoundException($reflectionClass->getName(), $methodToInvoke, $arguments, $reflectionClass);
            }

            $method = $reflectionClass->getMethod($methodToInvoke);
            if (!$method->isStatic()) {
                throw new BadMethodCallException(sprintf('Method %s is not static', $methodToInvoke));
            }

            return $method->invokeArgs(null, $arguments);
        } catch (ReflectionException $e) {
            throw new RuntimeException(sprintf(
                'Cannot load the class: %s, error: %s',
                $this->getClassName($classToLoad),
                $e->getMessage())
            );
        }
    }

    /**
     * @param mixed $classToLoad
     */
    private function getClassName($classToLoad): string
    {
        if ($classToLoad instanceof ReflectionClass) {
            return $classToLoad->getName();
        }

        return is_object($classToLoad) ? get_class($classToLoad) : (string) $classToLoad;
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

    private function throwMethodNotFoundException(string $className, string $methodName, array $arguments, ReflectionClass $reflectionClass): void
    {
        $methods = $reflectionClass->getMethods(ReflectionMethod::IS_STATIC);
        $message = sprintf('Static method %s with arguments %s was not found in class %s.
            Available static methods:' . PHP_EOL, $methodName, json_encode($arguments), $className
        );

        foreach ($methods as $method) {
            $params = [];
            foreach ($method->getParameters() as $param) {
                $paramStr = $param->getType() ? $param->getType()->getName() : 'mixed';
                $paramStr .= ' $' . $param->getName();
                if ($param->isOptional()) {
                    $paramStr .= ' = ' . ($param->isDefaultValueAvailable() ?
                        var_export($param->getDefaultValue(), true) : 'null');
                }
                $params[] = $paramStr;
            }
            $message .= $method->getName() . '(' . implode(', ', $params) . ")\n";
        }

        throw new BadMethodCallException($message);
    }
}
