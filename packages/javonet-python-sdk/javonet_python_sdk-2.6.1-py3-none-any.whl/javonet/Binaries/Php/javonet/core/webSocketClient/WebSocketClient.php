<?php

declare(strict_types=1);

namespace core\webSocketClient;

use RuntimeException;
use utils\Uri;

final class WebSocketClient
{
    private const SECURE_PORT_NUMBER = 443;
    private const UNSECURE_PORT_NUMBER = 80;
    private $socket;
    private URI $uri;
    private bool $connected = false;

    public function __construct(URI $uri)
    {
        $this->uri = $uri;
        $port = $this->getPort();

        $this->socket = fsockopen($this->getUri(), $port, $errno, $errstr);

        if ($this->socket === false) {
            throw new RuntimeException(sprintf('Could not connect to %s : %d - %s (%s)', $uri->getHost(), $port, $errstr, $errno));
        }

        $this->connect();
    }

    private function connect(): void
    {
        $request = sprintf(
            "GET %s HTTP/1.1\r\n" .
            "Host: %s\r\n" .
            "Upgrade: websocket\r\n" .
            "Connection: Upgrade\r\n" .
            "Sec-WebSocket-Key: %s\r\n" .
            "Sec-WebSocket-Version: 13\r\n\r\n",
            $this->getPath(),
            $this->getHost(),
            $this->generateWebSocketKey()
        );

        fwrite($this->socket, ...unpack('C*',mb_convert_encoding($request, 'UTF-8')));
        fflush($this->socket);

        $response = fread($this->socket, 1024);
        if ($response === false) {
            fclose($this->socket);
            throw new RuntimeException('Response read error');
        }

        if (strpos($response, '101 Switching Protocols') === false) {
            fclose($this->socket);
            throw new RuntimeException('Failed to upgrade to WebSocket');
        }

        $this->connected = true;
    }

    private function getPath(): string
    {
        return $this->uri->isEmptyPath() ? '/' : $this->uri->getPath();
    }

    private function isSecureConnect(): bool
    {
        return strtolower($this->uri->getScheme()) === 'wss';
    }

    private function getPort(): int
    {
        return $this->uri->getPort() ?? $this->isSecureConnect() ? self::SECURE_PORT_NUMBER : self::UNSECURE_PORT_NUMBER;
    }

    private function getProtocol(): string
    {
        return $this->isSecureConnect() ? 'ssl' : 'tcp';
    }

    private function getHost(): string
    {
        $host = $this->uri->getHost();
        if ($this->uri->isNotEmptyPort()) {
            return $host . ':' . $this->uri->getPort();
        }

        return $host;
    }

    private function getUri(): string
    {
        return $this->getProtocol() . '://' . $this->uri->getHost();
    }

    private function generateWebSocketKey(): string
    {
        return base64_encode(random_bytes(16));
    }

    public static function sendMessage(URI $uri, array $message): array
    {
        $client = new WebSocketClient($uri);
        try {
            if (!$client->connected) {
                throw new RuntimeException('WebSocket is not connected');
            }
            $client->sendByteArray($message);

            return $client->receiveByteArray();
        } finally {
            $client->close();
        }
    }

    private function sendByteArray(array $message): void
    {
        $length = count($message);
        $mask = [];
        for ($i = 0; $i < 4; $i++) {
            $mask[] = rand(0, 255);
        }

        $frame[0] = 0x82;
        $frame[1] = 0x80 | $length;

        for ($i = 0; $i < 4; $i++) {
            $frame[2 + $i] = $mask[$i];
        }

        for ($i = 0; $i < $length; $i++) {
            $frame[6 + $i] = $message[$i] ^ $mask[$i % 4];
        }

        fwrite($this->socket, ...$frame);
        fflush($this->socket);
    }

    private function receiveByteArray(): array
    {
        $header = fread($this->socket, 2);
        if (strlen($header) !== 2) {
            throw new \RuntimeException('Failed to read WebSocket frame header');
        }

        $headerBytes = unpack('C*', $header);
        $isMasked = ($headerBytes[1] & 0x80) !== 0;
        $payloadLength = $headerBytes[1] & 0x7F;

        if ($payloadLength === 126) {
            $extendedPayloadLength = fread($this->socket, 2);
            if (strlen($extendedPayloadLength) !== 2) {
                throw new \RuntimeException('Failed to read extended payload length');
            }
            $extendedPayloadLengthBytes = unpack('C*', $extendedPayloadLength);
            $payloadLength = (($extendedPayloadLengthBytes[0] & 0xFF) << 8) | ($extendedPayloadLengthBytes[1] & 0xFF);
        } elseif ($payloadLength === 127) {
            $extendedPayloadLength = fread($this->socket, 8);
            if (strlen($extendedPayloadLength) !== 8) {
                throw new \RuntimeException('Failed to read extended payload length');
            }
            $extendedPayloadLengthBytes = unpack('C*', $extendedPayloadLength);
            $payloadLength = 0;
            for ($i = 0; $i < 8; $i++) {
                $payloadLength = ($payloadLength << 8) | ($extendedPayloadLengthBytes[$i] & 0xFF);
            }
        }

        $mask = [];
        if ($isMasked) {
            $maskBytes = fread($this->socket, 4);
            if (strlen($maskBytes) !== 4) {
                throw new \RuntimeException('Failed to read mask');
            }
            $mask = unpack('C*', $maskBytes);
        }

        $payloadBytes = fread($this->socket, $payloadLength);
        if (strlen($payloadBytes) !== $payloadLength) {
            throw new \RuntimeException('Failed to read payload');
        }

        $payload = unpack('C*', $payloadBytes);
        if ($isMasked) {
            for ($i = 0; $i < $payloadLength; $i++) {
                $payload[$i] ^= $mask[$i % 4];
            }
        }

        return $payload;
    }

    public function __destruct()
    {
        $this->close();
    }

    public function close(): void
    {
        if ($this->socket) {
            fwrite($this->socket, "\x88\x00");
            fflush($this->socket);

            $this->connected = false;
        }

        fclose($this->socket);
    }
}