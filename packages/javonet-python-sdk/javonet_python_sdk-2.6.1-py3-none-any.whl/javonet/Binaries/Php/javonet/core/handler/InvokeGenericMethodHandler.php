<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;
use ReflectionClass;
use ReflectionException;

final class InvokeGenericMethodHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(self::class, self::REQUIRED_ARGUMENTS_COUNT);
        }

        $objectOrClass = $command->getPayload()[0];
        $methodToInvoke = $command->getPayload()[1];
        $arguments = array_slice($command->getPayload(), 2);

        try {
            $reflectionClass = new ReflectionClass($objectOrClass);
            $method = $reflectionClass->getMethod($methodToInvoke);

            return $method->invokeArgs(is_object($objectOrClass) ? $objectOrClass : null, $arguments);
        } catch (ReflectionException $e) {
            $reflectionClass = new ReflectionClass($objectOrClass);
            $methods = $reflectionClass->getMethods();
            $className = is_object($objectOrClass) ? get_class($objectOrClass) : (string) $objectOrClass;
            $message = sprintf('Method %s not found in class %s. Available methods:' . PHP_EOL, (string) $methodToInvoke, $className);
            foreach ($methods as $method) {
                $params = [];
                foreach ($method->getParameters() as $param) {
                    $paramType = $param->getType();
                    $params[] = ($paramType ? $paramType . ' ' : '') . '$' . $param->getName();
                }
                $message .= $method->getName() . '(' . implode(', ', $params) . ')' . PHP_EOL;
            }
            throw new ReflectionException($message);
        }
    }
}
