<?php

declare(strict_types=1);

namespace core\handler;

use ArrayAccess;
use Exception;
use utils\CommandInterface;

final class ArrayGetItemHandler extends AbstractHandler
{
    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        $payload = $command->getPayload();
        if (empty($payload)) {
            throw new Exception('Payload cannot be empty.');
        }

        if (is_array($payload[0]) || $payload[0] instanceof ArrayAccess) {
            $indexes = array_slice($payload, 1);

            return $this->getElement($payload[0], $indexes);
        }

        throw new Exception(sprintf('Cannot get element from type: %s', gettype($payload[0])));
    }

    /**
     * @param mixed $value
     * @return mixed
     */
    private function getElement($value, array $indexes)
    {
        if (count($indexes) === 1 && is_array($indexes[0])) {
            $indexes = $indexes[0];
        }

        if (empty($indexes)) {
            throw new Exception('Index not provided.');
        }

        foreach ($indexes as $index) {
            if ((is_array($value) || $value instanceof ArrayAccess) && isset($value[$index])) {
                $value = $value[$index];
            } else {
                throw new Exception(sprintf('Invalid index: %s or key not found.', $index));
            }
        }
        return $value;
    }
}
