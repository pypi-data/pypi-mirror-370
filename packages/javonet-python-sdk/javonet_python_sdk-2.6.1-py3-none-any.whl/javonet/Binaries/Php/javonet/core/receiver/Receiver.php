<?php

declare(strict_types=1);

namespace core\receiver;

use core\interpreter\Interpreter;
use core\protocol\CommandSerializer;


use Throwable;
use utils\Command;
use utils\connectiondata\IConnectionData;
use utils\connectiondata\InMemoryConnectionData;
use utils\ExceptionSerializer;
use utils\RuntimeLogger;
use utils\RuntimeName;
use utils\type\CommandType;

final class Receiver
{
    private IConnectionData $connectionData;

    public function __construct()
    {
        $this->connectionData = new InMemoryConnectionData();
    }

    public function sendCommand(array $messageByteArray): array
    {
        try {
            $result = (new Interpreter())->process($messageByteArray);
            return CommandSerializer::serialize($result, $this->connectionData);
        } catch (Throwable $ex) {
            $exceptionCommand = ExceptionSerializer::serializeException(
                $ex,
                new Command(RuntimeName::PHP(), CommandType::EXCEPTION(), [])
            );
            return CommandSerializer::serialize($exceptionCommand, $this->connectionData);
        }
    }

    public function heartBeat(array $messageByteArray): array
    {
        return [$messageByteArray[11], $messageByteArray[12] - 2];
    }

    public function getRuntimeInfo(): string
    {
        return RuntimeLogger::getRuntimeInfo();
    }
}
