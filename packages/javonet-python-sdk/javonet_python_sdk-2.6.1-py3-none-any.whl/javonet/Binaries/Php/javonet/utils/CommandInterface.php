<?php

declare(strict_types=1);

namespace utils;

use utils\type\CommandType;

interface CommandInterface
{
    public function addArgToPayload($arg): CommandInterface;
    public function setPayload(int $index, $value): void;
    public function getRuntimeName(): RuntimeName;
    public function getCommandType(): CommandType;
    public function getPayload(): array;
    public function getPayloadByIndex(int $index);
    public function getPayloadSize(): int;
    public function toString(): string;
    public function __toString(): string;
    public static function createResponse($response, RuntimeName $runtimeName): CommandInterface;
    public static function createReference(string $uuid, RuntimeName $runtimeName): CommandInterface;
    public static function createArrayResponse(array $array, RuntimeName $runtimeName): CommandInterface;
    public function prependArgumentToPayload(?CommandInterface $currentCommand): CommandInterface;
    public function equals($element): bool;
}
