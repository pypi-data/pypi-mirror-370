<?php

declare(strict_types=1);

namespace core\referencecache;

use ArrayAccess;
use Countable;
use Iterator;

final class ArrayWrapper implements ArrayAccess, Countable, Iterator
{
    private array $data;
    private int $position = 0;

    public function __construct(array $data)
    {
        $this->data = $data;
    }

    public function &getData(): array
    {
        return $this->data;
    }

    public function setData(array $data): void
    {
        $this->data = $data;
    }

    public function offsetExists($offset): bool
    {
        return isset($this->data[$offset]);
    }

    /**
     * @param mixed $offset
     * @return mixed|null
     */
    public function offsetGet($offset)
    {
        return $this->data[$offset] ?? null;
    }

    /**
     * @param mixed $offset
     * @param mixed $value
     */
    public function offsetSet($offset, $value): void
    {
        if (is_null($offset)) {
            $this->data[] = $value;
        } else {
            $this->data[$offset] = $value;
        }
    }

    /**
     * @param $offset
     */
    public function offsetUnset($offset): void
    {
        unset($this->data[$offset]);
    }

    public function count(): int
    {
        return count($this->data);
    }

    /**
     * @return false|mixed
     */
    public function current()
    {
        return current($this->data);
    }

    /**
     * @return int|string|null
     */
    public function key()
    {
        return key($this->data);
    }

    public function next(): void
    {
        next($this->data);
    }

    public function rewind(): void
    {
        reset($this->data);
        $this->position = 0;
    }

    public function valid(): bool
    {
        return key($this->data) !== null;
    }

    public function getRank(): int
    {
        if (empty($this->data)) {
            return 1;
        }

        $maxRank = 0;
        foreach ($this->data as $element) {
            if (is_array($element)) {
                $elementWrapper = new ArrayWrapper($element);
                $rank = $elementWrapper->getRank();
                if ($rank > $maxRank) {
                    $maxRank = $rank;
                }
            }
        }

        return 1 + $maxRank;
    }
}
