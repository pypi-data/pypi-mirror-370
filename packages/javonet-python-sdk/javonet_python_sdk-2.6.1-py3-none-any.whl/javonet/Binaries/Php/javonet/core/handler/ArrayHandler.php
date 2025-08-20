<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;

final class ArrayHandler extends AbstractHandler
{
    public function process(CommandInterface $command): array
    {
        $payload = $command->getPayload();

        if (empty($payload)) {
            return [];
        }

        $processedArray = [];
        foreach ($payload as $item) {
            $processedArray[] = $item;
        }

        return $processedArray;
    }
}
