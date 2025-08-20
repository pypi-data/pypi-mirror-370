<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use core\referencecache\ReferencesCache;

final class DestructReferenceHandler extends AbstractHandler
{
    public function process(CommandInterface $command): bool
    {
        return ReferencesCache::getInstance()->deleteReference((string) $command->getPayload()[0]);
    }
}
