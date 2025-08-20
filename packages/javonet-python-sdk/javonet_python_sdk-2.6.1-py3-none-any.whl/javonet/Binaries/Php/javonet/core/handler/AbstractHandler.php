<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use utils\type\CommandType;

abstract class AbstractHandler
{
    private static array $HANDLER_MAP = [];
    private static bool $isInitializing = false;

    /**
     * @return mixed
     */
    abstract public function process(CommandInterface $command);

    public function __construct()
    {
        if (!self::$isInitializing && empty(self::$HANDLER_MAP)) {
            self::$isInitializing = true;
            try {
                $handler = new Handler();
                self::$HANDLER_MAP = $handler->handlers;
            } finally {
                self::$isInitializing = false;
            }
        }
    }

    public function handleCommand(CommandInterface $command)
    {
        if ($command->getCommandType()->equalsByValue(CommandType::GENERATE_LIB)) {
            return $this->process($command);
        }

        $this->iterate($command);

        return $this->process($command);
    }

    public function iterate(CommandInterface $command): void
    {
        for ($i = 0; $i < $command->getPayloadSize(); $i++) {
            if ($command->getPayload()[$i] instanceof CommandInterface) {
                $innerCommand = $command->getPayload()[$i];
                $command->setPayload($i, self::$HANDLER_MAP[$innerCommand->getCommandType()->getValue()]->handleCommand($innerCommand));
            }
        }
    }
}
