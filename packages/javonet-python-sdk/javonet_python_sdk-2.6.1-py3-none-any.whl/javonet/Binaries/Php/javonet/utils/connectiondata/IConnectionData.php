<?php

declare(strict_types=1);

namespace utils\connectiondata;

use utils\type\ConnectionType;

interface IConnectionData
{
    public function getConnectionType(): ConnectionType;
    public function getHostname(): string;
    public function serializeConnectionData(): array;
    public function toString(): string;
}