<?php

declare(strict_types=1);

namespace core\handler;

use core\typescache\TypesCache;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class EnableTypeHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    public function process(CommandInterface $command): int
    {
        if (count($command->getPayload()) < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(self::class, self::REQUIRED_ARGUMENTS_COUNT);
        }

        $typesCache = TypesCache::getInstance();
        foreach ($command->getPayload() as $payload) {
            if (is_string($payload)) {
                $typesCache->cacheType($payload);
            }

            if (is_array($payload)) {
                foreach ($payload as $namespaceToEnable) {
                    $typesCache->cacheType($namespaceToEnable);
                }
            }
        }

        return 0;
    }
}
