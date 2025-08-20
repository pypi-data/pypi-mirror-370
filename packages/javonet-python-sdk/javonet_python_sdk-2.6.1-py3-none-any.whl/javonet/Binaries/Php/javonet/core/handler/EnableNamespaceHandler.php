<?php

declare(strict_types=1);

namespace core\handler;

use core\namespacescache\NamespacesCache;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class EnableNamespaceHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    public function process(CommandInterface $command): int
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $namespacesCache = NamespacesCache::getInstance();

        foreach ($command->getPayload() as $payload) {
            if (is_string($payload)) {
                $namespacesCache->cacheNamespace($payload);
            }

            if (is_array($payload)) {
                foreach ($payload as $namespaceToEnable) {
                    if (is_string($namespaceToEnable)) {
                        $namespacesCache->cacheNamespace($namespaceToEnable);
                    }
                }
            }
        }

        return 0;
    }
}
