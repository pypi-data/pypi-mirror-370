<?php

declare(strict_types=1);

namespace utils;

use RuntimeException;
use Throwable;

final class Uuid
{
    private string $uuid;

    private function __construct(string $uuid)
    {
        $this->uuid = $uuid;
    }

    public static function uuid4(): Uuid
    {
        try {
            $data = random_bytes(16);
            $data[6] = chr(ord($data[6]) & 0x0f | 0x40);
            $data[8] = chr(ord($data[8]) & 0x3f | 0x80);
            $hex = bin2hex($data);
            $uuid = substr($hex, 0, 8) . '-' .
                substr($hex, 8, 4) . '-' .
                substr($hex, 12, 4) . '-' .
                substr($hex, 16, 4) . '-' .
                substr($hex, 20);

            return new self($uuid);
        } catch (Throwable $th) {
            throw new RuntimeException('Failed to generate UUID: ' . $th->getMessage(), 0, $th);
        }
    }

    public function toString(): string
    {
        return $this->uuid;
    }

    public function __toString(): string
    {
        return $this->uuid;
    }
}
