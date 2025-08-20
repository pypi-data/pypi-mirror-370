<?php

declare(strict_types=1);

namespace core\handler;

use BadMethodCallException;
use core\referencecache\ArrayWrapper;
use ReflectionClass;
use ReflectionMethod;
use ReflectionException;
use RuntimeException;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class InvokeInstanceMethodHandler extends AbstractHandler
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
        $objectInstance = $payload[0];
        $methodToInvoke = (string) $payload[1];
        $arguments = array_slice($payload, 2);

        foreach ($arguments as $i => $arg) {
            if ($arg instanceof ArrayWrapper) {
                $arguments[$i] = $arg->getData();
            }
        }

        try {
            $reflectionClass = new ReflectionClass($objectInstance);

            if (!$reflectionClass->hasMethod($methodToInvoke)) {
                $this->throwMethodNotFoundException($objectInstance, $methodToInvoke, $arguments, $reflectionClass);
            }

            $method = $reflectionClass->getMethod($methodToInvoke);
            if ($method->isStatic()) {
                throw new BadMethodCallException(sprintf('Method %s is static and cannot be called on instance', $methodToInvoke));
            }

            return $method->invokeArgs($objectInstance, $arguments);
        } catch (ReflectionException $e) {
            throw new RuntimeException(sprintf('Cannot access the object: %s, error: %s', get_class($objectInstance), $e->getMessage()));
        }
    }

    private function throwMethodNotFoundException($objectInstance, string $methodName, array $arguments, ReflectionClass $reflectionClass): void
    {
        $methods = $reflectionClass->getMethods(ReflectionMethod::IS_PUBLIC & ~ReflectionMethod::IS_STATIC);
        $message = sprintf('Instance method %s with arguments %s was not found in class %s.
            Available instance methods:' . PHP_EOL, $methodName, json_encode($arguments), get_class($objectInstance)
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
