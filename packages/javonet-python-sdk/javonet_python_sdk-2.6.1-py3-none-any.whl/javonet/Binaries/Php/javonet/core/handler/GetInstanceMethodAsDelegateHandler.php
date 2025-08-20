<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionException;
use ReflectionMethod;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class GetInstanceMethodAsDelegateHandler extends AbstractHandler
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

        $objectInstance = $command->getPayload()[0];
        $methodToInvoke = (string) $command->getPayload()[1];

        $argumentsTypes = array_slice($command->getPayload(), 2);

        $reflectionClass = new ReflectionClass($objectInstance);

        try {
            return $reflectionClass->getMethod($methodToInvoke);
        } catch (ReflectionException $e) {
            $methods = $reflectionClass->getMethods(ReflectionMethod::IS_PUBLIC);
            $message = sprintf('Instance method %s with arguments types [%s] not found in class %s. Available methods:' . PHP_EOL,
                $methodToInvoke,
                implode(', ', array_map('gettype', $argumentsTypes)),
                get_class($objectInstance)
            );

            foreach ($methods as $method) {
                $parameters = $method->getParameters();
                $paramTypes = array_map(function($param) {
                    $type = $param->getType();

                    return $type ? $type->getName() : 'mixed';
                }, $parameters);

                $message .= $method->getName() . ' with arguments [' .
                    implode(', ', $paramTypes) . "]\n";
            }

            throw new ReflectionException($message, 0, $e);
        }
    }
}
