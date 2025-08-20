<?php

declare(strict_types=1);

namespace core\delegatecache;

use Exception;
use ReflectionMethod;
use utils\exception\DelegateNotFoundException;
use utils\exception\SingletonUnserializeException;
use utils\Uuid;

final class DelegatesCache
{
    private static ?DelegatesCache $instance = null;

    /** @var array<Uuid, ReflectionMethod> */
    private static array $delegatesCache = [];

    private function __construct()
    {
    }

    public static function getInstance(): DelegatesCache
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    public function addDelegate(ReflectionMethod $delegateInstance): string
    {
        $delegateId = Uuid::uuid4()->toString();
        self::$delegatesCache[$delegateId] = $delegateInstance;

        return $delegateId;
    }

    public static function getDelegate(string $delegateId): ReflectionMethod
    {
        $delegateInstance = self::$delegatesCache[$delegateId];
        if ($delegateInstance === null) {
            throw new DelegateNotFoundException($delegateId);
        }

        return $delegateInstance;
    }

    private function __clone()
    {
    }

    /**
     * @throws Exception
     */
    public function __wakeup()
    {
        throw new SingletonUnserializeException();
    }
}
