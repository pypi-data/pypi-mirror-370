<?php

declare(strict_types=1);

namespace core\handler;

use ReflectionClass;
use ReflectionException;
use Exception;
use SebastianBergmann\CodeCoverage\Report\PHP;
use utils\CommandInterface;
use utils\exception\JavonetArgumentsMismatchException;

final class GetInstanceFieldHandler extends AbstractHandler
{
    private const REQUIRED_ARGUMENTS_COUNT = 2;

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

        $objectClass = $command->getPayload()[0];
        $fieldString = (string)$command->getPayload()[1];

        try {
            $reflection = new ReflectionClass($objectClass);
            if (!$reflection->hasProperty($fieldString)) {
                throw new ReflectionException(sprintf('Property %s not found', $fieldString));
            }

            $property = $reflection->getProperty($fieldString);
            $property->setAccessible(true);

            return $property->getValue($objectClass);
        } catch (ReflectionException $e) {
            $reflection = new ReflectionClass($objectClass);
            $properties = $reflection->getProperties();

            $message = sprintf('Instance field %s not found in class %s . Available fields:' . PHP_EOL,
                $fieldString,
                get_class($objectClass)
            );

            foreach ($properties as $property) {
                if ($property->isPublic()) {
                    $message .= $property->getName() . PHP_EOL;
                }
            }

            throw new Exception($message);
        }
    }
}
