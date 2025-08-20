<?php

declare(strict_types=1);

namespace core\handler;

use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;
use utils\TypesHandler;

final class ConvertTypeHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    public function process(CommandInterface $command): string
    {
        if ($command->getPayloadSize() !== self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        return TypesHandler::convertTypeToJavonetType($command->getPayload()[0]);
    }
}
