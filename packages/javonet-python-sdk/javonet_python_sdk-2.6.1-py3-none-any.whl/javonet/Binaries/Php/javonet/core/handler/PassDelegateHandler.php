<?php

declare(strict_types=1);

namespace core\handler;

use utils\DynamicMethodFactory;
use ReflectionMethod;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;
use utils\RuntimeName;

final class PassDelegateHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 1;

    public function process(CommandInterface $command): ReflectionMethod
    {
        if ($command->getPayloadSize() < self::REQUIRED_ARGUMENTS_COUNT) {
            throw new JavonetArgumentsMismatchException(self::class, self::REQUIRED_ARGUMENTS_COUNT);
        }

        $delegateGuid = (string) $command->getPayload()[0];
        $callingRuntimeName = (int) $command->getPayload()[1];
        $delegateArgs = $this->getArguments($command);

        $delegateArgsTypes = $this->getArgumentTypes($delegateArgs);
        $delegateReturnType = $this->getReturnType($delegateArgs);

        $dynamicClass = DynamicMethodFactory::createDynamicClass(
            'DynamicallyCreatedDelegate',
            $delegateReturnType,
            $delegateArgsTypes,
            new RuntimeName($callingRuntimeName),
            $delegateGuid
        );

        return new ReflectionMethod($dynamicClass, 'methodToExecute');
    }

    private function getArguments(CommandInterface $command): array
    {
        return $command->getPayloadSize() > 2
            ? array_slice($command->getPayload(), 2)
            : [];
    }

    private function getArgumentTypes(array $args): array
    {
        $argsTypes = [];
        for ($i = 0; $i < count($args) - 1; $i++) {
            $argsTypes[$i] = $args[$i];
        }
        return $argsTypes;
    }

    private function getReturnType(array $args): string
    {
        return (string) $args[count($args) - 1];
    }
}
