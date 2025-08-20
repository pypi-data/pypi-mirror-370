<?php

declare(strict_types=1);

namespace core\typescache;

final class TypesCache
{
    private static ?TypesCache $instance = null;
    private array $typeCache = [];

    private function __construct() {}

    public static function getInstance(): TypesCache
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function cacheType(string $typeRegex): int
    {
        $this->typeCache[] = $typeRegex;

        return 0;
    }

    public function isTypeCacheEmpty(): bool
    {
        return empty($this->typeCache);
    }

    public function isTypeAllowed(string $typeToCheck): bool
    {
        foreach ($this->typeCache as $typePattern) {
            if ($typePattern === $typeToCheck) {
                return true;
            }

            $typeRegex = str_replace(['\\', '*'], ['\\\\', '.*'], $typePattern);
            $typeRegex = '/^' . $typeRegex . '$/';

            if (preg_match($typeRegex, $typeToCheck)) {
                return true;
            }
        }
        return false;
    }

    public function getTypeCache(): array
    {
        return $this->typeCache;
    }

    public function clearCache(): void
    {
        $this->typeCache = [];
    }
}
