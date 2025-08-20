<?php

declare(strict_types=1);

namespace core\transmitter;

use RuntimeException;
use Throwable;

final class Transmitter
{
    public static function sendCommand(array $messageByteArray): array
    {
        try {
            return TransmitterWrapper::sendCommand($messageByteArray);
        } catch (Throwable $e) {
            throw new RuntimeException('Error sending command: ' . $e->getMessage(), 0, $e);
        }
    }

    public static function activate(string $licenseKey): int
    {
        try {
            return TransmitterWrapper::activate($licenseKey);
        } catch (Throwable $e) {
            throw new RuntimeException('Error during activation: ' . $e->getMessage(), 0, $e);
        }
    }

    public static function setConfigSource(string $configSource): int
    {
        try {
            return TransmitterWrapper::setConfigSource($configSource);
        } catch (Throwable $e) {
            throw new RuntimeException('Error setting config source: ' . $e->getMessage(), 0, $e);
        }
    }

    public static function setJavonetWorkingDirectory(string $path): int
    {
        try {
            return TransmitterWrapper::setJavonetWorkingDirectory($path);
        } catch (Throwable $e) {
            throw new RuntimeException('Error setting working directory: ' . $e->getMessage(), 0, $e);
        }
    }
}
