<?php

declare(strict_types=1);

namespace core\handler;

use Countable;
use core\referencecache\ArrayWrapper;
use Exception;
use utils\CommandInterface;

final class ArrayGetSizeHandler extends AbstractHandler
{
    public function process(CommandInterface $command): int
    {
        $payload = $command->getPayload();
        if (empty($payload)) {
            throw new Exception('Payload is empty.');
        }

        if ($payload[0] instanceof ArrayWrapper) {
            return $this->getArraySize($payload[0]->getData());
        }

        if (is_array($payload[0])) {
            return $this->getArraySize($payload[0]);
        }

        if ($payload[0] instanceof Countable) {
            return count($payload[0]);
        }

        if (is_object($payload[0]) && method_exists($payload[0], 'size')) {
            return $payload[0]->size();
        }

        if (is_object($payload[0])) {
            throw new Exception(sprintf('Cannot get size of object of class %s', get_class($payload[0])));
        }

        throw new Exception(sprintf('Cannot get size of type %s', gettype($payload[0])));
    }

    private function getArraySize(array $array): int
    {
        $sizeCount = 1;
        $currentElement = $array;

        while (is_array($currentElement)) {
            $sizeCount *= count($currentElement);
            if (empty($currentElement)) {
                break;
            }
            $currentElement = $currentElement[0];
        }

        return $sizeCount;
    }
}
