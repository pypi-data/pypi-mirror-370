<?php

declare(strict_types=1);

namespace core\protocol;

use utils\Command;
use utils\CommandInterface;
use utils\exception\TypeByteNotSupportedException;
use utils\RuntimeName;
use utils\StringEncodingMode;
use utils\type\CommandType;
use utils\type\JType;

final class CommandDeserializer
{
    private int $position;
    private Command $command;
    private array $buffer;

    public function __construct(
         array $buffer
    ) {
        $this->command = new Command(
            new RuntimeName($buffer[0]),
            new CommandType($buffer[10])
        );
        $this->buffer = $buffer;
        $this->position = 11;
    }

    private function isNotEnd(): bool
    {
        return $this->position < count($this->buffer);
    }

    public function deserialize(): CommandInterface
    {
        while ($this->isNotEnd()) {
            $this->command = $this->command->addArgToPayload($this->readObject($this->buffer[$this->position]));
        }

        return $this->command;
    }

    private function readObject(int $typeNum)
    {
        $typeByte = new JType($typeNum);

        switch ($typeByte->getValue()) {
            case JType::JAVONET_COMMAND:
                return $this->readCommand();
            case JType::JAVONET_STRING:
                return $this->readString();
            case JType::JAVONET_INTEGER:
                return $this->readInt();
            case JType::JAVONET_BOOLEAN:
                return $this->readBool();
            case JType::JAVONET_FLOAT:
                return $this->readFloat();
            case JType::JAVONET_BYTE:
                return $this->readByte();
            case JType::JAVONET_CHAR:
                return $this->readChar();
            case JType::JAVONET_LONG:
                return $this->readLong();
            case JType::JAVONET_DOUBLE:
                return $this->readDouble();
            case JType::JAVONET_UNSIGNED_LONG_LONG:
                return $this->readUnsignedLong();
            case JType::JAVONET_UNSIGNED_INTEGER:
                return $this->readUnsignedInteger();
            case JType::JAVONET_NULL:
                return $this->readNull();
            default:
                throw new TypeByteNotSupportedException($typeNum);
        }
    }

    protected function readCommand(): CommandInterface
    {
        $p = $this->position;
        $numberOfElementsInPayload = TypeDeserializer::deserializeInt(array_slice($this->buffer, $p + 1, 4));
        $runtime = $this->buffer[$p + 5];
        $commandType = $this->buffer[$p + 6];

        $this->position += 7;

        $payload = [];
        for ($i = 0; $i < $numberOfElementsInPayload; $i++) {
            $payload[$i] = $this->readObject($this->buffer[$this->position]);
        }

        return new Command(
            new RuntimeName($runtime),
            new CommandType($commandType),
            $payload
        );
    }

    private function readString(): string
    {
        $p = $this->position;
        $stringEncodingMode = new StringEncodingMode($this->buffer[$p + 1]);
        $size = TypeDeserializer::deserializeInt(array_slice($this->buffer, $p + 2, 4));
        $this->position += 6;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeString($stringEncodingMode, array_slice($this->buffer, $p, $size));
    }

    private function readInt(): int
    {
        $size = 4;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeInt(array_slice($this->buffer, $p, $size));
    }

    private function readBool(): bool
    {
        $size = 1;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeBool(array_slice($this->buffer, $p, $size));
    }

    private function readFloat(): float
    {
        $size = 4;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeFloat(array_slice($this->buffer, $p, $size));
    }

    private function readByte(): int
    {
        $size = 1;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeByte($this->buffer[$p]);
    }

    private function readChar(): string
    {
        $size = 1;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeChar($this->buffer[$p]);
    }

    private function readLong(): int
    {
        $size = 8;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeLong(array_slice($this->buffer, $p, $size));
    }

    private function readDouble(): float
    {
        $size = 8;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeDouble(array_slice($this->buffer, $p, $size));
    }

    private function readUnsignedLong(): int
    {
        $size = 8;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeLong(array_slice($this->buffer, $p, $size));
    }

    private function readUnsignedInteger(): int
    {
        $size = 4;
        $this->position += 2;
        $p = $this->position;
        $this->position += $size;

        return TypeDeserializer::deserializeInt(array_slice($this->buffer, $p, $size));
    }

    private function readNull()
    {
        $size = 1;
        $this->position += 2;
        $this->position += $size;

        return TypeDeserializer::deserializeNull();
    }
}
