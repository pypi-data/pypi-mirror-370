<?php

declare(strict_types=1);

namespace utils;

use utils\type\CommandType;
use core\interpreter\Interpreter;
use utils\connectiondata\InMemoryConnectionData;
use ReflectionClass;

final class DynamicMethodFactory
{
    public static function createDynamicClass(
        string $className,
        string $returnType,
        array $paramTypes,
        RuntimeName $callingRuntimeName,
        string $delegateGuid
    ): object {
        $dynamicClass = new class($returnType, $paramTypes, $callingRuntimeName, $delegateGuid) {
            private $returnType;
            private $paramTypes;
            private $callingRuntimeName;
            private $delegateGuid;
            
            public function __construct($returnType, $paramTypes, $callingRuntimeName, $delegateGuid) {
                $this->returnType = $returnType;
                $this->paramTypes = $paramTypes;
                $this->callingRuntimeName = $callingRuntimeName;
                $this->delegateGuid = $delegateGuid;
            }
            
            public function methodToExecute(...$args) {
                $objArgs = [];
                foreach ($args as $arg) {
                    $objArgs[] = $arg;
                }

                $payload = array_merge([$this->delegateGuid], $objArgs);

                $invokeDelegateCommand = new Command(
                    $this->callingRuntimeName,
                    CommandType::INVOKE_DELEGATE(),
                    $payload
                );

                $interpreter = new Interpreter();
                $executeCall = $interpreter->execute(
                    $invokeDelegateCommand, 
                    new InMemoryConnectionData()
                );

                $response = $executeCall->getPayload()[0];

                return self::castToType($response, $this->returnType);
            }
            
            private static function castToType($value, string $targetType) {
                switch ($targetType) {
                    case 'int':
                    case 'integer':
                        return (int) $value;
                    case 'float':
                    case 'double':
                        return (float) $value;
                    case 'string':
                        return (string) $value;
                    case 'bool':
                    case 'boolean':
                        return (bool) $value;
                    case 'array':
                        return (array) $value;
                    case 'object':
                        return (object) $value;
                    default:
                        if (class_exists($targetType)) {
                            if ($value instanceof $targetType) {
                                return $value;
                            }

                            $reflection = new ReflectionClass($targetType);
                            if ($reflection->isInstantiable()) {
                                return $reflection->newInstance($value);
                            }
                        }
                        return $value;
                }
            }
        };
        
        return $dynamicClass;
    }
}
