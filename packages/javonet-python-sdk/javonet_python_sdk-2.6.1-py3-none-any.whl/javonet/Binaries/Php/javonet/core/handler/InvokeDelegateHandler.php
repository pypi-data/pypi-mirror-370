<?php

declare(strict_types=1);

namespace core\handler;

use core\delegatecache\DelegatesCache;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class InvokeDelegateHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $guid = (string) $command->getPayload()[0];
        $delegate = DelegatesCache::getInstance()->getDelegate($guid);
        $parameters = array_slice($command->getPayload(), 1);

        return $delegate->invokeArgs(null, $parameters);
    }
}
