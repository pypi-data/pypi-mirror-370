<?php

declare(strict_types=1);

namespace core\handler\LoadLibrary;

use Phar;

final class ClasspathScanner
{
    public function getClassesFromFile(string $filePath): array
    {
        if (!is_file($filePath)) {
            return [];
        }

        $classes = [];
        if (substr($filePath, -5) === '.phar') {
            return $this->getClassesFromPhar($filePath);
        }

        if (substr($filePath, -4) === '.php') {
            $content = file_get_contents($filePath);
            $classes = $this->extractClassesFromPhpContent($content);
        }

        return $classes;
    }

    private function getClassesFromPhar(string $pharPath): array
    {
        $classes = [];

        $phar = new Phar($pharPath);
        foreach ($phar as $file) {
            if ($file->getExtension() === 'php') {
                $content = $file->getContent();
                $classes = array_merge(
                    $classes,
                    $this->extractClassesFromPhpContent($content)
                );
            }
        }

        return $classes;
    }

    private function extractClassesFromPhpContent(string $content): array
    {
        $classes = [];
        $namespace = '';

        if (preg_match('/namespace\s+([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff\\\\]*)\s*;/', $content, $matches)) {
            $namespace = $matches[1] . '\\';
        }

        preg_match_all('/(?:class|interface|trait)\s+([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)/i', $content, $matches);
        
        foreach ($matches[1] as $className) {
            $fullClassName = $namespace . $className;
            $classes[] = $fullClassName;
        }

        return $classes;
    }
}
