<?php

declare(strict_types=1);

namespace core\handler;

use core\referencecache\ReferencesCache;

use utils\CommandInterface;
use utils\Command;
use utils\exception\JavonetArgumentsMismatchException;
use utils\RuntimeName;
use utils\type\CommandType;

final class ResolveInstanceHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    public function process(CommandInterface $command)
    {
        if (self::REQUIRED_ARGUMENTS_COUNT !== $command->getPayloadSize()) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }
        if ($command->getRuntimeName()->equalsByValue(RuntimeName::PHP)) {
            return ReferencesCache::getInstance()->resolveReference($command->getPayload()[0]);
        }

        return new Command($command->getRuntimeName(), CommandType::REFERENCE(), $command->getPayload()[0]);
    }
}
