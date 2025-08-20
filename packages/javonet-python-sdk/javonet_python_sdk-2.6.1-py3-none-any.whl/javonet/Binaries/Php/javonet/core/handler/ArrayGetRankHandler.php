<?php

declare(strict_types=1);

namespace core\handler;

use ArrayAccess;
use core\referencecache\ArrayWrapper;
use utils\CommandInterface;

final class ArrayGetRankHandler extends AbstractHandler
{
    public function process(CommandInterface $command): int
    {
        $payload = $command->getPayload();
        if (empty($payload)) {
            return 0;
        }

        return $this->getArrayRank($payload[0]);
    }

    /**
     * @param mixed $array
     */
    private function getArrayRank($array): int
    {
        if ($array instanceof ArrayWrapper) {
            return $array->getRank();
        }

        if (!is_array($array) && !$array instanceof ArrayAccess) {
            return 0;
        }

        if (empty($array)) {
            return 1;
        }

        $maxRank = 0;
        foreach ($array as $element) {
            $rank = $this->getArrayRank($element);
            if ($rank > $maxRank) {
                $maxRank = $rank;
            }
        }

        return 1 + $maxRank;
    }
}
