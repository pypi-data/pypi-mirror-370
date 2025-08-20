<?php

declare(strict_types=1);

namespace utils\error;

use TypeError;

final class UnsupportedPayloadItemTypeError extends TypeError
{
    public function __construct($payloadItem)
    {
        parent::__construct(sprintf(
            'Unsupported payload item type: %s for payload item: %s.',
            gettype($payloadItem),
            var_export($payloadItem, true)
        ));
    }
}
