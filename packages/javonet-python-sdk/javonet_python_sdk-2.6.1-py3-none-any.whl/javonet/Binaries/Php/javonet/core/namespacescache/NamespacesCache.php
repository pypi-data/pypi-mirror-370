<?php

declare(strict_types=1);

namespace core\namespacescache;

use ReflectionClass;

final class NamespacesCache
{
    private static ?NamespacesCache $instance = null;
    private static array $namespacesCache = [];

    private function __construct() {}

    public static function getInstance(): NamespacesCache
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }


    public function cacheNamespace(string $namespaceRegex): void
    {
        self::$namespacesCache[] = $namespaceRegex;
    }

    public function isNamespaceCacheEmpty(): bool
    {
        return empty(self::$namespacesCache);
    }

    public function isTypeAllowed(object $typeToCheck): bool
    {
        $typeNamespace = $this->getTypeNamespace($typeToCheck);
        foreach (self::$namespacesCache as $namespacePattern) {
            if ($typeNamespace === $namespacePattern) {
                return true;
            }

            $normalizedPattern = str_replace('\\', '.', $namespacePattern);
            $normalizedNamespace = str_replace('\\', '.', $typeNamespace);

            if (substr($normalizedPattern, -2) === '.*') {
                $basePattern = substr($normalizedPattern, 0, -2);
                if ($normalizedNamespace === $basePattern || strpos($normalizedNamespace, $basePattern . '.') === 0) {
                    return true;
                }
            }

            if (substr($normalizedPattern, -1) === '*') {
                $basePattern = substr($normalizedPattern, 0, -1);
                if ($normalizedNamespace === $basePattern || strpos($normalizedNamespace, $basePattern) === 0) {
                    return true;
                }
            }

            if ($normalizedNamespace === $normalizedPattern) {
                return true;
            }
        }

        return false;
    }

    private function getTypeNamespace(object $typeToCheck): string
    {
        if ($typeToCheck instanceof ReflectionClass) {

            return $typeToCheck->getNamespaceName();
        }
        $reflection = new ReflectionClass($typeToCheck);

        return $reflection->getNamespaceName();
    }

    public function getCachedNamespaces(): array
    {
        return self::$namespacesCache;
    }

    public function clearCache(): void
    {
        self::$namespacesCache = [];
    }
}
