<?php

declare(strict_types=1);

namespace core\interpreter;

use core\handler\Handler;
use core\protocol\CommandDeserializer;
use core\protocol\CommandSerializer;
use core\receiver\Receiver;
use core\transmitter\Transmitter;
use core\webSocketClient\WebSocketClient;
use Exception;
use Throwable;
use utils\Command;
use utils\CommandInterface;
use utils\connectiondata\IConnectionData;
use utils\ExceptionSerializer;
use utils\messagehelper\MessageHelper;
use utils\RuntimeName;
use utils\type\ConnectionType;
use utils\Uri;

final class Interpreter
{
    private string $debugMode;
    private Handler $handler;

    public function __construct()
    {
        $this->debugMode = getenv('DEBUG') !== false ? getenv('DEBUG') : 'FALSE';
        $this->handler = new Handler();
    }

    public function execute(CommandInterface $command, IConnectionData $connectionData): CommandInterface
    {
        if ($this->debugMode === 'TRUE') {
            echo 'Sent command: ' . $command;
            MessageHelper::getInstance()->sendMessageToAppInsights('SentCommand', $command->toString());
        }

        $responseByteArray = $this->getResponseByteArray($command, $connectionData);
        if ($responseByteArray instanceof Command) {
            return $responseByteArray;
        }

        $response = (new CommandDeserializer($responseByteArray))->deserialize();
        if ($this->debugMode === 'TRUE') {
            echo 'Received command: ' . $response;
            MessageHelper::getInstance()->sendMessageToAppInsights('ReceivedCommand', $response->toString());
        }

        return $response;
    }

    private function getResponseByteArray(Command $command, IConnectionData $connectionData)
    {
        $messageByteArray = CommandSerializer::serialize($command, $connectionData);
        if ($this->isWebSocket($connectionData))
        {
            try {
                return WebSocketClient::sendMessage(new Uri($connectionData->getHostname()), $messageByteArray);
            } catch (Exception $e) {
                if ($e->getPrevious() instanceof Throwable) {
                    return ExceptionSerializer::serializeException($e->getPrevious(), $command);
                }

                return ExceptionSerializer::serializeException($e, $command);
            }
        }

        if ($this->isInMemoryAndSameRuntime($command, $connectionData)) {
            return (new Receiver())->sendCommand($messageByteArray);
        }

        return Transmitter::sendCommand($messageByteArray);
    }

    private function isWebSocket(IConnectionData $connectionData): bool
    {
        return $connectionData->getConnectionType()->equalsByValue(ConnectionType::WEB_SOCKET);
    }

    private function isInMemoryAndSameRuntime(Command $command, IConnectionData $connectionData): bool
    {
        return $command->getRuntimeName()->equalsByValue(RuntimeName::PHP)
            && $connectionData->getConnectionType()->equalsByValue(ConnectionType::IN_MEMORY);
    }

    public function process(array $byteArray): CommandInterface
    {
        $receivedCommand = (new CommandDeserializer($byteArray))->deserialize();
        if ($this->debugMode === 'TRUE') {
            echo 'Received command: ' . $receivedCommand;
            MessageHelper::getInstance()->sendMessageToAppInsights('ReceivedCommand', $receivedCommand->toString());
        }

        $response = $this->handler->handleCommand($receivedCommand);
        if ($this->debugMode === 'TRUE') {
            echo 'Response command: ' . $response;
            MessageHelper::getInstance()->sendMessageToAppInsights('ResponseCommand', $response->toString());
        }

        return $response;
    }
}
