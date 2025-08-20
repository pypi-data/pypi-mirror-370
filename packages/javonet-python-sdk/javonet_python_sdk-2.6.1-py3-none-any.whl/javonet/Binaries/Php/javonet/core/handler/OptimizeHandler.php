<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use BadMethodCallException;

final class OptimizeHandler extends AbstractHandler
{
    public function process(CommandInterface $command)
    {
        throw new BadMethodCallException('Optimize method is not available for PHP');
    }
}
