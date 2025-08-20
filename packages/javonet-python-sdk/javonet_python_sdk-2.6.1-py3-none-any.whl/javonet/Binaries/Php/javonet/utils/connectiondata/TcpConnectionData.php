<?php

declare(strict_types=1);

namespace utils\connectiondata;

use utils\type\ConnectionType;

final class TcpConnectionData implements IConnectionData
{
    private string $hostName;
    private string $ipAddress;
    private int $port;
    private ConnectionType $connectionType;

    public function __construct(
        string $hostName,
        int $port
    ) {
        $this->hostName = $hostName;
        $this->port = $port;
        $this->ipAddress = gethostbyname($hostName);
        $this->connectionType = ConnectionType::TCP();
    }

    public function getConnectionType(): ConnectionType
    {
        return $this->connectionType;
    }

    public function getHostname(): string
    {
        return $this->hostName;
    }

    public function serializeConnectionData(): array
    {
        $result[] = $this->getConnectionType()->getValue();
        array_push($result, ...$this->getAddressBytes());

        return array_merge($result, $this->getPortBytes());
    }

    private function getAddressBytes(): array
    {
        $ipAddress = explode('.', $this->ipAddress);
        $ipBytes = [];
        foreach ($ipAddress as $ip) {
            $ipBytes[] = (int) $ip;
        }

        return $ipBytes;
    }

    private function getPortBytes(): array
    {
        return [
            $this->port & 0xFF,
            $this->port >> 8 & 0xFF
        ];
    }

    public function toString(): string
    {
        return $this->ipAddress . ':' . $this->port;
    }

    public function __toString(): string
    {
        return $this->ipAddress . ':' . $this->port;
    }
}