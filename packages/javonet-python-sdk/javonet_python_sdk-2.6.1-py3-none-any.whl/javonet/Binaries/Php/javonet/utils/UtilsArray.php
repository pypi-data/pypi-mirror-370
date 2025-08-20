<?php

declare(strict_types=1);

namespace utils;

final class UtilsArray
{
    public static function hasNotValues(array $array): bool
    {
        $filtered = array_filter($array, function ($value) {
            return is_array($value) ? self::hasNotValues($value) : !empty($value);
        });

        return empty($filtered);
    }
}