<?php

declare(strict_types=1);

namespace core\handler;

use Exception;
use ParseError;
use Phar;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class LoadLibraryHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;
    private static array $loadedLibraries = [];
    private array $loadedClassPaths = [];

    public function process(CommandInterface $command): int
    {
        return $this->loadLibrary($command);
    }

    private function loadLibrary(CommandInterface $command): int
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
            self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $assemblyName = (string) $command->getPayload()[0];
        if (!file_exists($assemblyName)) {
            throw new Exception('File not found: ' . $assemblyName);
        }

        if (in_array($assemblyName, self::$loadedLibraries, true)) {
            return 0;
        }

        if (is_dir($assemblyName)) {
            $this->loadDirectory($assemblyName);
        } elseif (pathinfo($assemblyName, PATHINFO_EXTENSION) === 'phar') {
            $this->loadPharFile($assemblyName);
        } else {
            $this->loadPhpFile($assemblyName);
        }

        self::$loadedLibraries[] = $assemblyName;
        return 0;
    }

    private function loadDirectory(string $directoryPath): void
    {
        if (!is_readable($directoryPath)) {
            throw new Exception('Directory is not readable: ' . $directoryPath);
        }

        $realPath = realpath($directoryPath);
        if ($realPath === false) {
            throw new Exception('Cannot resolve directory path: ' . $directoryPath);
        }

        $currentIncludePath = get_include_path();
        if (strpos($currentIncludePath, $realPath) === false) {
            set_include_path($currentIncludePath . PATH_SEPARATOR . $realPath);
            $this->loadedClassPaths[] = $realPath;
        }

        $this->autoloadPhpFilesFromDirectory($realPath);
    }

    private function loadPharFile(string $pharPath): void
    {
        if (!is_readable($pharPath)) {
            throw new Exception('PHAR file is not readable: ' . $pharPath);
        }

        try {
            $phar = new Phar($pharPath);

            $currentIncludePath = get_include_path();
            if (strpos($currentIncludePath, $pharPath) === false) {
                set_include_path($currentIncludePath . PATH_SEPARATOR . $pharPath);
                $this->loadedClassPaths[] = $pharPath;
            }

            if (isset($phar['bootstrap.php'])) {
                include_once 'phar://' . $pharPath . '/bootstrap.php';
            }
        } catch (Exception $e) {
            throw new Exception(sprintf('Error loading PHAR file %s : %s', $pharPath, $e->getMessage()));
        }
    }

    private function loadPhpFile(string $filePath): void
    {
        if (!is_readable($filePath)) {
            throw new Exception('PHP file is not readable: ' . $filePath);
        }

        $fileExtension = pathinfo($filePath, PATHINFO_EXTENSION);
        if (!in_array($fileExtension, ['php', 'inc'], true)) {
            throw new Exception('File is not a valid PHP file: ' . $filePath);
        }

        $code = file_get_contents($filePath);
        if ($code === false) {
            throw new Exception(sprintf('Failed to read php file: %s', $filePath));
        }

        try {
            token_get_all($code, TOKEN_PARSE);
        } catch (ParseError $e) {
            throw new Exception(sprintf('PHP syntax error in file %s: %s', $filePath, $e->getMessage()));
        }

        $lastError = error_get_last();
        if ($lastError && $lastError['type'] === E_PARSE) {
            throw new Exception(sprintf('PHP syntax error in file %s: %s', $filePath, $lastError['message']));
        }

        include_once $filePath;
    }

    private function autoloadPhpFilesFromDirectory(string $directory): void
    {
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($directory)
        );

        foreach ($iterator as $file) {
            if ($file->isFile() && $file->getExtension() === 'php') {
                include_once $file->getPathname();
            }
        }
    }

    public static function getLoadedLibraries(): array
    {
        return self::$loadedLibraries;
    }

    public function __destruct()
    {
        foreach ($this->loadedClassPaths as $path) {
            if (strpos($path, sys_get_temp_dir()) === 0 && is_dir($path)) {
                $this->removeDirectoryOrFile($path);
            }
        }
    }

    private function removeDirectoryOrFile(string $dir): void
    {
        if (!file_exists($dir)) {
            return;
        }

        if (is_file($dir) || is_link($dir)) {
            if (!unlink($dir)) {
                throw new Exception('Cannot delete file path: ' . $dir);
            }

            return;
        }
        $files = scandir($dir);
        foreach ($files as $file) {
            if ($file === '.' || $file === '..') {
                continue;
            }
            $this->removeDirectoryOrFile($dir . DIRECTORY_SEPARATOR . $file);
        }

        if(!rmdir($dir)) {
            throw new Exception('Cannot delete dir path: '. $dir);
        }
    }
}
