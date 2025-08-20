<?php

declare(strict_types=1);

namespace utils;

use utils\exception\enum\{
    EnumNameNotFoundException,
    InvalidEnumValueException
};
use ReflectionClass;
use utils\exception\BadMethodCallException;

abstract class Enum
{
    private int $value;
    private static array $instances = [];

    public function __construct(int $value)
    {
        $constants = (new ReflectionClass(static::class))->getConstants();
        if (!in_array($value, $constants, true)) {
            throw new InvalidEnumValueException(static::class, $value);
        }

        $this->value = $value;
    }

    public function getValue(): int
    {
        return $this->value;
    }

    public function getName(): string
    {
        foreach ((new ReflectionClass(static::class))->getConstants() as $name => $val) {
            if ($val === $this->value) {
                return $name;
            }
        }

        throw new EnumNameNotFoundException((string)$this->value);
    }

    public static function __callStatic(string $method, array $arguments)
    {
        $className = static::class;
        if (isset(self::$instances[$className][$method])) {
            return self::$instances[$className][$method];
        }

        $constants = (new ReflectionClass($className))->getConstants();

        if (array_key_exists($method, $constants)) {
            $instance = new static($constants[$method]);
            self::$instances[$className][$method] = $instance;
            return $instance;
        }

        throw new BadMethodCallException($className, $method);
    }

    public static function from(int $value): self
    {
        $constants = (new ReflectionClass(static::class))->getConstants();
        if (!in_array($value, $constants, true)) {
            throw new InvalidEnumValueException(static::class, $value);
        }

        return new static($value);
    }

    public function equalsByValue(int $value): bool
    {
        return $this->value === $value;
    }

    public function notEqualsByValue(int $value): bool
    {
        return $this->value !== $value;
    }

    public function __toString(): string
    {
        return (string)$this->value;
    }
}
