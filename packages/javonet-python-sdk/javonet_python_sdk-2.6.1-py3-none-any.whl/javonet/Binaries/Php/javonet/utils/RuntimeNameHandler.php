<?php

declare(strict_types=1);

namespace utils;

final class RuntimeNameHandler
{
    public static function getName(RuntimeName $runtimeName): string
    {
        switch ($runtimeName->getValue()) {
            case RuntimeName::CLR:
                return 'clr';
            case RuntimeName::GO:
                return 'go';
            case RuntimeName::JVM:
                return 'jvm';
            case RuntimeName::NETCORE:
                return 'netcore';
            case RuntimeName::PERL:
                return 'perl';
            case RuntimeName::PYTHON:
                return 'python';
            case RuntimeName::RUBY:
                return 'ruby';
            case RuntimeName::NODEJS:
                return 'nodejs';
            case RuntimeName::CPP:
                return 'cpp';
            case RuntimeName::PHP:
                return 'php';
            case RuntimeName::PYTHON27:
                return 'python27';
            case RuntimeName::NONE:
                return 'none';
            default:
                 throw new \Exception('Invalid runtime name.');
        }
    }
}
