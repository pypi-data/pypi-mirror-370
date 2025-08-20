<?php

declare(strict_types=1);

namespace core\handler;

use core\handler\LoadLibrary\ClasspathScanner;
use core\namespacescache\NamespacesCache;
use core\typescache\TypesCache;
use Exception;
use ReflectionClass;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class GetTypeHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;
    private array $primitiveTypeMap;

    public function __construct()
    {
        $this->primitiveTypeMap = [
            'boolean' => 'bool',
            'bool' => 'bool',
            'integer' => 'int',
            'int' => 'int',
            'double' => 'float',
            'float' => 'float',
            'string' => 'string',
            'array' => 'array',
            'object' => 'object',
            'resource' => 'resource',
            'null' => 'null'
        ];
    }

    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $typeName = $this->getTypeName($command);

        if (array_key_exists($typeName, $this->primitiveTypeMap)) {
            $typeToReturn = $this->primitiveTypeMap[$typeName];
        } else {
            try {
                if (class_exists($typeName)) {
                    $typeToReturn = new ReflectionClass($typeName);
                } else {
                    if (class_exists($typeName)) {
                        $typeToReturn = new ReflectionClass($typeName);
                    } else {
                        throw new Exception('Class not found: ' . $typeName);
                    }
                }
            } catch (Exception $ex) {
                $loadedLibraries = LoadLibraryHandler::getLoadedLibraries();
                $loadedClasses = [];

                foreach ($loadedLibraries as $library) {
                    if (substr($library, -4) === '.php' || substr($library, -5) === '.phar') {
                        $scanner = new ClasspathScanner();
                        $loadedClasses = array_merge(
                            $loadedClasses,
                            $scanner->getClassesFromFile($library)
                        );
                    }
                }

                $availableClasses = implode(PHP_EOL, $loadedClasses) .
                    implode(PHP_EOL, get_declared_classes());

                $includePath = get_include_path();

                throw new Exception(sprintf(
                    'Type: %s not found in include path' . PHP_EOL
                    . 'Load all libraries at the beginning of your application' . PHP_EOL
                    . 'Exception: %s' . PHP_EOL
                    . 'PHP include path: %s' . PHP_EOL
                    . 'Available classes loaded by user: %s' . PHP_EOL,
                    $typeName,
                    $ex->getMessage(),
                    $includePath,
                    $availableClasses
                ));
            }
        }

        if ($command->getPayloadSize() > 1) {
            $parentClass = $command->getPayload()[1];
            if ($typeToReturn instanceof ReflectionClass && $parentClass instanceof ReflectionClass) {
                if (!$typeToReturn->isSubclassOf($parentClass->getName())) {
                    throw new Exception(sprintf(
                        'Class %s is not a subclass of %s',
                        $typeToReturn->getName(),
                        $parentClass->getName()
                    ));
                }
            }
        }

        $namespaceCache = NamespacesCache::getInstance();
        $typeCache = TypesCache::getInstance();

        $typeName = $typeToReturn instanceof ReflectionClass ? $typeToReturn->getName() : (string) $typeToReturn;

        $isAllowed = ($namespaceCache->isNamespaceCacheEmpty() && $typeCache->isTypeCacheEmpty())
            || ($typeToReturn instanceof ReflectionClass && $namespaceCache->isTypeAllowed($typeToReturn))
            || $typeCache->isTypeAllowed($typeName);

        if (!$isAllowed) {
            $allowedNamespaces = implode(', ', $namespaceCache->getCachedNamespaces());
            $allowedTypes = implode(', ', $typeCache->getTypeCache());

            $typeName = $typeToReturn instanceof ReflectionClass
                ? $typeToReturn->getName()
                : (string) $typeToReturn;

            throw new Exception(sprintf(
                'Type %s not allowed. Allowed namespaces: %s. Allowed types: %s',
                $typeName,
                $allowedNamespaces,
                $allowedTypes
            ));
        }

        return $typeToReturn;
    }

    private function getTypeName(CommandInterface $command): string
    {
        $payload = $command->getPayload()[0];
        if (is_string($payload)) {
            return $payload;
        }

        if ($payload instanceof ReflectionClass) {
            return $payload->getName();
        }

        if (is_object($payload)) {
           return get_class($payload);
        }

        return gettype($payload);
    }
}
