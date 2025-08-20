<?php

declare(strict_types=1);

namespace utils\connectiondata;

use utils\type\ConnectionType;

final class InMemoryConnectionData implements IConnectionData
{
    public function getConnectionType(): ConnectionType
    {
        return ConnectionType::IN_MEMORY();
    }

    public function getHostname(): string
    {
        return '';
    }

    public function serializeConnectionData(): array
    {
        return [$this->getConnectionType()->getValue(), 0, 0, 0, 0, 0, 0 ];
    }

    public function toString(): string
    {
        return $this->getHostname();
    }

    public function __toString(): string
    {
        return $this->getHostname();
    }
}