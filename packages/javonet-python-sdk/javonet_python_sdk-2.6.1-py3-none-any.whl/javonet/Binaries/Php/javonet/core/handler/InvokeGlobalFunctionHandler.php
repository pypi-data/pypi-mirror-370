<?php

declare(strict_types=1);

namespace core\handler;

use Exception;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class InvokeGlobalFunctionHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    /**
     * @return mixed
     */
    public function process(CommandInterface $command)
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(
                self::class,
                self::REQUIRED_ARGUMENTS_COUNT
            );
        }

        $functionName = $command->getPayload()[0];
        $args = array_slice($command->getPayload(), 1);

        if (function_exists($functionName)) {
            return call_user_func_array($functionName, $args);
        }

        if (strpos($functionName, '\\') !== false) {
            if (function_exists($functionName)) {
                return call_user_func_array($functionName, $args);
            }
        }

        if (strpos($functionName, '::') !== false) {
            [$className, $methodName] = explode('::', $functionName, 2);
            if (class_exists($className) && method_exists($className, $methodName)) {
                return call_user_func_array([$className, $methodName], $args);
            }
        }

        $availableFunctions = get_defined_functions()['internal'];
        throw new Exception(sprintf(
            'Function %s not found. Available built-in internal functions: %s',
            $functionName,
            implode(', ', array_slice($availableFunctions, 0, 100)) . '...'
        ));
    }
}
