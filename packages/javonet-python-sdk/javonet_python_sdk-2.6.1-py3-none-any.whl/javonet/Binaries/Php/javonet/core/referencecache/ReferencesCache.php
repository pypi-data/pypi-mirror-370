<?php

declare(strict_types=1);

namespace core\referencecache;

use utils\exception\SingletonUnserializeException;
use utils\Uuid;

final class ReferencesCache
{
    private static ?ReferencesCache $instance = null;
    private array $references = [];

    private function __construct()
    {
    }

    public static function getInstance(): ReferencesCache
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    /**
     * @param mixed $reference
     */
    public function cacheReference($reference): string
    {
        $uuid = Uuid::uuid4()->toString();
        $this->references[$uuid] = $reference;

        return $uuid;
    }

    /**
     * @return null|mixed
     */
    public function resolveReference(string $uuid)
    {
        return $this->references[$uuid] ?? null;
    }

    public function deleteReference(string $uuid): bool
    {
        if (isset($this->references[$uuid])) {
            unset($this->references[$uuid]);
            return true;
        }

        return false;
    }

    private function __clone()
    {
    }

    /**
     * @throws \Exception
     */
    public function __wakeup()
    {
        throw new SingletonUnserializeException();
    }
}
