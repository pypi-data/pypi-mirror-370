<?php

declare(strict_types=1);

namespace utils;

use Exception;
use utils\type\CommandType;

final class Command implements CommandInterface
{
    private RuntimeName $runtimeName;
    private CommandType $commandType;
    private array $payload;

    public function __construct(
        RuntimeName $runtimeName,
        CommandType $commandType,
        ...$payload
    ) {
        $this->runtimeName = $runtimeName;
        $this->commandType = $commandType;
        $this->payload = count($payload) === 1 && is_array($payload[0])
            ? $payload[0]
            : $payload;
    }

    /**
     * @param mixed $arg
     */
    public function addArgToPayload($arg): CommandInterface
    {
        return new Command($this->runtimeName, $this->commandType, array_merge($this->payload, [$arg]));
    }

    /**
     * @param mixed $value
     */
    public function setPayload(int $index, $value): void
    {
        $this->payload[$index] = $value;
    }

    public function getRuntimeName(): RuntimeName
    {
        return $this->runtimeName;
    }

    public function getCommandType(): CommandType
    {
        return $this->commandType;
    }

    public function getPayload(): array
    {
        return $this->payload;
    }

    /**
     * @return mixed
     */
    public function getPayloadByIndex(int $index)
    {
        return $this->payload[$index];
    }

    public function getPayloadSize(): int
    {
        return count($this->payload);
    }

    public function toString(): string
    {
        return 'Target runtime: ' . $this->runtimeName->getName() .
            ' Command type: ' . $this->commandType->getName() .
            ' Payload: ' . json_encode($this->payload);
    }

    public function __toString(): string
    {
        try {
            $result = 'RuntimeName: ';
            $result .= $this->runtimeName->getName();
            $result .= ' CommandType: ';
            $result .= $this->commandType->getName();
            $result .= ' Payload: ';
            foreach ($this->payload as $value) {
                $result .= $this->getPayloadValue($value);
            }

            return $result;
        } catch (Exception $e) {
            return 'Error while converting command to string: ' . $e->getMessage();
        }
    }

    private function getPayloadValue($value): string
    {
        if (null === $value) {
            return 'null ';
        }

        return $value . PHP_EOL;
    }

    /**
     * @param mixed $response
     */
    public static function createResponse($response, RuntimeName $runtimeName): CommandInterface
    {
        return new Command($runtimeName, CommandType::VALUE(), $response);
    }

    public static function createReference(string $uuid, RuntimeName $runtimeName): CommandInterface
    {
        return new Command($runtimeName, CommandType::REFERENCE(), $uuid);
    }

    public static function createArrayResponse(array $array, RuntimeName $runtimeName): CommandInterface
    {
        return new Command($runtimeName, CommandType::ARRAY(), $array);
    }

    public function prependArgumentToPayload(?CommandInterface $currentCommand): CommandInterface
    {
        if ($currentCommand === null) {
            return new self($this->runtimeName, $this->commandType, $this->payload);
        }

        return new self($this->runtimeName, $this->commandType, [$currentCommand, ...$this->payload]);
    }

    /**
     * @param mixed $element
     */
    public function equals($element): bool
    {
        if ($this === $element) {
            return true;
        }

        if (!$element instanceof CommandInterface) {
            return false;
        }

        if ($this->runtimeName !== $element->runtimeName || $this->commandType !== $element->commandType) {
            return false;
        }

        if (count($this->payload) !== count($element->payload)) {
            return false;
        }

        foreach ($this->payload as $index => $payloadItem) {
            $elementPayloadItem = $element->payload[$index];

            if ($payloadItem instanceof CommandInterface && $elementPayloadItem instanceof CommandInterface) {
                if (!$payloadItem->equals($elementPayloadItem)) {
                    return false;
                }
            }

            if (is_object($payloadItem) && method_exists($payloadItem, 'equals') && is_object($elementPayloadItem)) {
                if (!$payloadItem->equals($elementPayloadItem)) {
                    return false;
                }
            }

            elseif ($payloadItem !== $elementPayloadItem) {
                return false;
            }
        }

        return true;
    }
}
