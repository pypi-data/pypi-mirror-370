<?php

declare(strict_types=1);

namespace utils;

use RuntimeException;

final class UtilsConst
{
    private static string $configSource = '';
    private static string $licenseKey = '';
    private static string $javonetWorkingDirectory = '';

    public static function getLicenseKey(): string
    {
        return self::$licenseKey;
    }

    public static function setLicenseKey(?string $value): void
    {
        if (empty($value) || $value === 'your-license-key') {
            return;
        }

        self::$licenseKey = $value;
    }

    public static function getJavonetWorkingDirectory(): string
    {
         if (empty(self::$javonetWorkingDirectory)) {
            return self::$javonetWorkingDirectory = getcwd() . '/';
         }

        return self::$javonetWorkingDirectory;
    }

    public static function setJavonetWorkingDirectory(string $value): void
    {
        $path = str_replace('\\', '/', $value);
        if (substr($path, -1) !== '/') {
            $path .= '/';
        }

        if (!is_dir($path)) {
            if (!mkdir($path, 0700, true)) {
                throw new RuntimeException('Unable to create directory: ' . $path);
            }
        }

        if (!is_writable($path)) {
            throw new RuntimeException('Directory is not writable: ' . $path);
        }

        self::$javonetWorkingDirectory = $path;
    }

    public static function setConfigSource(string $value): void
    {
        self::$configSource = $value;
    }

    public static function getConfigSource(): string
    {
        return self::$configSource;
    }

    public static function isNotEmptyConfigSource(): bool
    {
        return !empty(self::$configSource);
    }
}
