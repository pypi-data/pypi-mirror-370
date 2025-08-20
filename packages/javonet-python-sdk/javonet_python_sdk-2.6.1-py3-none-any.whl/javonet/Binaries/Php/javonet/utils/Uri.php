<?php

declare(strict_types=1);

namespace utils;

use utils\exception\InvalidUriException;

final class Uri {
    private ?string $scheme;
    private ?string $host;
    private ?int $port;
    private ?string $user;
    private ?string $pass;
    private ?string $path;
    private ?string $query;
    private ?string $fragment;

    public function __construct(string $uri)
    {
        $this->parseUri($uri);
    }

    private function parseUri(string $uri): void
    {
        $parsedUri = parse_url($uri);
        if ($parsedUri === false) {
            throw new InvalidUriException($uri);
        }

        if (UtilsArray::hasNotValues($parsedUri)) {
            throw new InvalidUriException($uri);
        }

        $this->scheme = $parsedUri['scheme'] ?? null;
        $this->host = $parsedUri['host'] ?? null;
        $this->port = $parsedUri['port'] ?? null;
        $this->user = $parsedUri['user'] ?? null;
        $this->pass = $parsedUri['pass'] ?? null;
        $this->path = $parsedUri['path'] ?? null;
        $this->query = $parsedUri['query'] ?? null;
        $this->fragment = $parsedUri['fragment'] ?? null;
    }

    public function getScheme(): ?string
    {
        return $this->scheme;
    }

    public function getHost(): ?string
    {
        return $this->host;
    }

    public function getPort(): ?int
    {
        return $this->port;
    }

    public function isNotEmptyPort(): bool
    {
        return !empty($this->port);
    }

    public function getUser(): ?string
    {
        return $this->user;
    }

    public function getPass(): ?string
    {
        return $this->pass;
    }

    public function getPath(): ?string
    {
        return $this->path;
    }

    public function isEmptyPath(): bool
    {
        return empty($this->path);
    }

    public function getQuery(): ?string
    {
        return $this->query;
    }

    public function getFragment(): ?string
    {
        return $this->fragment;
    }

    public function __toString(): string
    {
        return $this->toString();
    }

    public function toString(): string
    {
        $uri = '';
        if ($this->scheme) {
            $uri .= $this->scheme . '://';
        }

        if ($this->user) {
            $uri .= $this->user;

            if ($this->pass) {
                $uri .= ':' . $this->pass;
            }

            $uri .= '@';
        }

        if ($this->host) {
            $uri .= $this->host;
        }

        if ($this->port) {
            $uri .= ':' . $this->port;
        }

        if ($this->path) {
            $uri .= $this->path;
        }

        if ($this->query) {
            $uri .= '?' . $this->query;
        }

        if ($this->fragment) {
            $uri .= '#' . $this->fragment;
        }

        return $uri;
    }
}