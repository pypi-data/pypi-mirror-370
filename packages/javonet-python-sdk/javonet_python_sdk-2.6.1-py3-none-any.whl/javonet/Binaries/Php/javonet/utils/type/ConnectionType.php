<?php

declare(strict_types=1);

namespace utils\type;

use utils\Enum;

final class ConnectionType extends Enum
{
    public const IN_MEMORY = 0;
    public const TCP = 1;
    public const WEB_SOCKET = 2;
}
