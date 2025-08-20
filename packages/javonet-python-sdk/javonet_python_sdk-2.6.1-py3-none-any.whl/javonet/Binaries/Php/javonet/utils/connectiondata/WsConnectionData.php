<?php

declare(strict_types=1);

namespace utils\connectiondata;

use utils\type\ConnectionType;

final class WsConnectionData implements IConnectionData
{
    private string $hostName;

    public function __construct(
        string $hostName
    ) {
        $this->hostName = $hostName;
    }

    public function getConnectionType(): ConnectionType
    {
        return ConnectionType::WEB_SOCKET();
    }

    public function serializeConnectionData(): array
    {
        return [$this->getConnectionType()->getValue(), 0, 0, 0, 0, 0, 0 ];
    }

    public function getHostname(): string
    {
        return $this->hostName;
    }

    public function __toString(): string
    {
        return $this->hostName;
    }

    public function toString(): string
    {
        return $this->hostName;
    }
}