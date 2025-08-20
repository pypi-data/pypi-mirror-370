<?php

declare(strict_types=1);

namespace core\protocol;

use core\referencecache\ReferencesCache;
use Exception;
use RuntimeException;
use utils\Command;
use utils\CommandInterface;
use utils\connectiondata\IConnectionData;
use utils\RuntimeName;
use utils\type\CommandType;
use utils\TypesHandler;

final class CommandSerializer
{
    private function __construct()
    {
    }

    private const DEFAULT_SERIALIZER_CONNECTION_DATA = [0, 0, 0, 0, 0, 0, 0];

    public static function serialize(CommandInterface $rootCommand, ?IConnectionData $connectionData): array
    {
        try {
            $buffer[] = $rootCommand->getRuntimeName()->getValue();
            $buffer[] = 0; // runtimeVersion
            array_push($buffer, ...self::getDataByConnectionData($connectionData));
            $buffer[] = RuntimeName::PHP;
            $buffer[] = $rootCommand->getCommandType()->getValue();

            self::serializeRecursively($rootCommand, $buffer);

            return $buffer;
        } catch (Exception $e) {
            throw new RuntimeException('Error during serialization ' . $e);
        }
    }

    private static function getDataByConnectionData(?IConnectionData $connectionData): array
    {
        if (null !== $connectionData) {
            return $connectionData->serializeConnectionData();
        }

        return self::DEFAULT_SERIALIZER_CONNECTION_DATA;
    }

    private static function serializeRecursively(CommandInterface $command, array &$buffer): void
    {
        foreach ($command->getPayload() as $payloadItem) {
            if ($payloadItem instanceof CommandInterface) {
                array_push($buffer, ...TypeSerializer::serializeCommand($payloadItem));
                self::serializeRecursively($payloadItem, $buffer);
            } else if (TypesHandler::isSimpleType($payloadItem)) {
                array_push($buffer, ...TypeSerializer::serializePrimitive($payloadItem));
            } else {
                $refCommand = new Command(
                    $command->getRuntimeName(),
                    CommandType::REFERENCE(),
                    ReferencesCache::getInstance()->cacheReference($payloadItem)
                );
                array_push($buffer, ...TypeSerializer::serializeCommand($refCommand));
                self::serializeRecursively($refCommand, $buffer);
            }
        }
    }
}
