<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use utils\exception\NotImplementedFunctionalityException;

final class AddEventListenerHandler extends AbstractHandler
{
    function process(CommandInterface $command): void
    {
        throw new NotImplementedFunctionalityException();
    }
}
