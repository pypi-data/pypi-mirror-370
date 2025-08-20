<?php

declare(strict_types=1);

namespace core\handler;

use ArrayObject;
use core\referencecache\ReferencesCache;
use core\referencecache\ArrayWrapper;
use Throwable;
use TypeError;
use utils\Command;
use utils\CommandInterface;
use utils\ExceptionSerializer;
use utils\type\CommandType;
use utils\TypesHandler;

final class Handler
{
    public array $handlers = [];

    public function __construct()
    {
        $this->handlers[CommandType::VALUE()->getValue()] = new ValueHandler();
        $this->handlers[CommandType::LOAD_LIBRARY()->getValue()] = new LoadLibraryHandler();
        $this->handlers[CommandType::REFERENCE()->getValue()] = new ResolveInstanceHandler();
        $this->handlers[CommandType::DESTRUCT_REFERENCE()->getValue()] = new DestructReferenceHandler();
        $this->handlers[CommandType::INVOKE_STATIC_METHOD()->getValue()] = new InvokeStaticMethodHandler();
        $this->handlers[CommandType::GET_STATIC_FIELD()->getValue()] = new GetStaticFieldHandler();
        $this->handlers[CommandType::SET_STATIC_FIELD()->getValue()] = new SetStaticFieldHandler();
        $this->handlers[CommandType::CREATE_INSTANCE()->getValue()] = new CreateInstanceHandler();
        $this->handlers[CommandType::GET_TYPE()->getValue()] = new GetTypeHandler();
        $this->handlers[CommandType::INVOKE_INSTANCE_METHOD()->getValue()] = new InvokeInstanceMethodHandler();
        $this->handlers[CommandType::CAST()->getValue()] = new CastHandler();
        $this->handlers[CommandType::OPTIMIZE()->getValue()] = new OptimizeHandler();
        $this->handlers[CommandType::GET_INSTANCE_FIELD()->getValue()] = new GetInstanceFieldHandler();
        $this->handlers[CommandType::SET_INSTANCE_FIELD()->getValue()] = new SetInstanceFieldHandler();
        $this->handlers[CommandType::ARRAY_GET_ITEM()->getValue()] = new ArrayGetItemHandler();
        $this->handlers[CommandType::ARRAY_GET_SIZE()->getValue()] = new ArrayGetSizeHandler();
        $this->handlers[CommandType::ARRAY_GET_RANK()->getValue()] = new ArrayGetRankHandler();
        $this->handlers[CommandType::ARRAY_SET_ITEM()->getValue()] = new ArraySetItemHandler();
        $this->handlers[CommandType::ARRAY()->getValue()] = new ArrayHandler();
        $this->handlers[CommandType::INVOKE_GENERIC_STATIC_METHOD()->getValue()] = new InvokeGenericStaticMethodHandler();
        $this->handlers[CommandType::INVOKE_GENERIC_METHOD()->getValue()] = new InvokeGenericMethodHandler();
        $this->handlers[CommandType::ENABLE_NAMESPACE()->getValue()] = new EnableNamespaceHandler();
        $this->handlers[CommandType::ENABLE_TYPE()->getValue()] = new EnableTypeHandler();
        $this->handlers[CommandType::GET_STATIC_METHOD_AS_DELEGATE()->getValue()] = new GetStaticMethodAsDelegateHandler();
        $this->handlers[CommandType::GET_INSTANCE_METHOD_AS_DELEGATE()->getValue()] = new GetInstanceMethodAsDelegateHandler();
        $this->handlers[CommandType::PASS_DELEGATE()->getValue()] = new PassDelegateHandler();
        $this->handlers[CommandType::INVOKE_DELEGATE()->getValue()] = new InvokeDelegateHandler();
        $this->handlers[CommandType::CONVERT_TYPE()->getValue()] = new ConvertTypeHandler();
        $this->handlers[CommandType::INVOKE_GLOBAL_FUNCTION()->getValue()] = new InvokeGlobalFunctionHandler();
        $this->handlers[CommandType::ADD_EVENT_LISTENER()->getValue()] = new AddEventListenerHandler();
    }

    public function handleCommand(CommandInterface $command): CommandInterface
    {
        try {
            if ($command->getCommandType()->equalsByValue(CommandType::RETRIEVE_ARRAY)) {
                $resolvedObject = $this->handlers[CommandType::REFERENCE()->getValue()]->handleCommand($command->getPayload()[0]);

                if ($resolvedObject instanceof ArrayWrapper) {
                    return Command::createArrayResponse(
                        $resolvedObject->getData(),
                        $command->getRuntimeName()
                    );
                }

                if ($resolvedObject instanceof ArrayObject) {
                    return Command::createArrayResponse(
                        $resolvedObject->getArrayCopy(),
                        $command->getRuntimeName()
                    );
                }

                if (is_array($resolvedObject)) {
                    return Command::createArrayResponse(
                        $resolvedObject,
                        $command->getRuntimeName()
                    );
                }

                throw new TypeError(sprintf(
                    'Expected array, ArrayObject or ArrayWrapper for RETRIEVE_ARRAY, got %s',
                    is_object($resolvedObject) ? get_class($resolvedObject) : gettype($resolvedObject)
                ));
            }

            return $this->getParseResponse($command);
        } catch (Throwable $e) {
            if ($e->getPrevious() !== null) {
                return ExceptionSerializer::serializeException($e->getPrevious(), $command);
            }

            return ExceptionSerializer::serializeException($e, $command);
        }
    }

    private function getParseResponse(CommandInterface $command): CommandInterface
    {
        $response = $this->handlers[$command->getCommandType()->getValue()]->handleCommand($command);
        if (TypesHandler::isSimpleType($response)) {
            return Command::createResponse($response, $command->getRuntimeName());
        }

        if ($this->isCommandGenerateLibType($response) || $this->isCommandExceptionType($response)) {
            return $response;
        }

        if (is_array($response)) {
            $response = new ArrayWrapper($response);
        }

        return Command::createReference(
            ReferencesCache::getInstance()->cacheReference($response),
            $command->getRuntimeName()
        );
    }

    /**
     * @param mixed $result
     */
    private function isCommandGenerateLibType($result): bool
    {
        if (is_object($result) && get_class($result) === Command::class) {
            return $result->getCommandType()->equalsByValue(CommandType::GENERATE_LIB);
        }

        return false;
    }

    /**
     * @param mixed $result
     */
    private function isCommandExceptionType($result): bool
    {
        if (is_object($result) && get_class($result) === Command::class) {
            return $result->getCommandType()->equalsByValue(CommandType::EXCEPTION);
        }

        return false;
    }
}
