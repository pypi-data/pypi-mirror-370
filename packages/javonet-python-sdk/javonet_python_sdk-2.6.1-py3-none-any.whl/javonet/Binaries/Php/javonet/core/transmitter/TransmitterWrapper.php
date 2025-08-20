<?php

declare(strict_types=1);

namespace core\transmitter;

use FFI;
use FFI\Exception as FFIException;
use RuntimeException;

final class TransmitterWrapper
{
    private function __construct()
    {
    }

    private static ?FFI $phpLib = null;

    private static ?string $workingDirectory = null;


    public static function setWorkingDirectoryPath(string $path): void
    {
        self::$workingDirectory = $path;
    }
    private static function loadNativeLibrary(): void
    {
        if (null !== self::$phpLib) {
            return;
        }

        $nativeLibPath = self::getNativeLibPath();
        if (!file_exists($nativeLibPath)) {
            throw new RuntimeException('Native library not found in path: ' . $nativeLibPath);
        }

        try {
            $lib = FFI::cdef(
            'int Activate(const char* licenseKey);
                int SendCommand(unsigned char* messageByteArray, int messageByteArrayLen);
                int ReadResponse(unsigned char* responseByteArray, int responseByteArrayLen);
                int SetConfigSource(const char* sourcePath);
                int SetWorkingDirectory(const char* path);
                const char* GetNativeError();',
            $nativeLibPath
            );
        } catch (FFIException $e) {
            throw new RuntimeException('Unable to load native library: ' . $e->getMessage());
        }

        self::$phpLib = $lib;
    }

    private static function getNativeLibPath(): string
    {
        $archSuffix = self::detectArchitecture();
        $basePath = self::getWorkingDirectoryBasePath();
        $osName = strtolower(PHP_OS);

        if (strpos($osName, 'win') !== false) {
            return $basePath . '/Binaries/Native/Windows/' . $archSuffix . '/JavonetPhpRuntimeNative.dll';
        }

        if (strpos($osName, 'darwin') !== false) {
            return $basePath . '/Binaries/Native/MacOs/' . $archSuffix . '/libJavonetPhpRuntimeNative.dylib';
        }

        if (strpos($osName, 'linux') !== false) {
            return $basePath . '/Binaries/Native/Linux/' . $archSuffix . '/libJavonetPhpRuntimeNative.so';
        }

        throw new RuntimeException('Unsupported OS: ' . $osName);
    }

    private static function getWorkingDirectoryBasePath(): string
    {
        if (empty(self::$workingDirectory)) {
            return rtrim(dirname(__DIR__, 3), '/\\\\');
        }

        return rtrim(self::$workingDirectory, '/\\\\');
    }

    private static function detectArchitecture(): string
    {
        $arch = strtolower(php_uname('m'));
        if (strpos($arch, 'arm') !== false || strpos($arch, 'aarch') !== false) {
            return strpos($arch, '64') !== false ? 'ARM64' : 'ARM';
        }

        if (strpos($arch, '64') !== false) {
            return 'X64';
        }

        return 'X86';
    }

    public static function sendCommand(array $messageByteArray): array
    {
        self::loadNativeLibrary();

        $messageLength = count($messageByteArray);
        $messageBuffer = self::$phpLib->new("unsigned char [$messageLength]");
        for ($i = 0; $i < $messageLength; $i++) {
            $messageBuffer[$i] = (int) $messageByteArray[$i] & 0xFF;
        }

        $responseArrayLen = self::$phpLib->SendCommand($messageBuffer, $messageLength);
        if ($responseArrayLen > 0) {
            $responseBuffer = self::$phpLib->new("unsigned char[$responseArrayLen]");
            self::$phpLib->ReadResponse($responseBuffer, $responseArrayLen);

            $response = [];
            for ($i = 0; $i < $responseArrayLen; $i++) {
                $response[] = $responseBuffer[$i];
            }

            return $response;
        }

        if ($responseArrayLen === 0) {
            throw new RuntimeException('Response is empty');
        }

        throw new RuntimeException('Javonet native error code: ' . $responseArrayLen . self::getErrorMessage());
    }

    public static function activate(string $licenseKey): int
    {
        self::loadNativeLibrary();

        $activationResult = self::$phpLib->Activate($licenseKey);
        if ($activationResult < 0) {
            throw new RuntimeException(
                'Javonet activation result: ' . $activationResult .
                '. Native error message: ' . self::getErrorMessage()
            );
        }
        return $activationResult;
    }

    public static function setConfigSource(string $configSource): int
    {
        self::loadNativeLibrary();

        $result = self::$phpLib->SetConfigSource($configSource);
        if ($result < 0) {
            throw new RuntimeException(
                'Javonet set config source failed. Result code: ' . $result .
                '. Native error message: ' . self::getErrorMessage()
            );
        }

        return $result;
    }

    public static function setJavonetWorkingDirectory(string $path): int
    {
        self::setWorkingDirectoryPath($path);
        self::loadNativeLibrary();

        $result = self::$phpLib->SetWorkingDirectory($path);
        if ($result < 0) {
            throw new RuntimeException('Javonet set working directory failed. Result code: ' . $result . '" Native error message: "' . self::getErrorMessage());
        }

        return $result;
    }

    public static function getErrorMessage(): string
    {
        try {
            $errorMessageCData = self::$phpLib->GetNativeError();

            return $errorMessageCData ?: 'Unknown native error';
        } catch (FFIException $e) {
            return 'FFI error calling GetNativeError: ' . $e->getMessage();
        }
    }
}
