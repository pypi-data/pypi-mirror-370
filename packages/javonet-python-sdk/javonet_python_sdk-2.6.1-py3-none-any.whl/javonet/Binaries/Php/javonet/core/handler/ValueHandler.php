<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;

final class ValueHandler extends AbstractHandler
{
    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        return $command->getPayload()[0];
    }
}
