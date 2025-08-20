<?php

declare(strict_types=1);

namespace utils\messagehelper;

use DateTime;
use DateTimeZone;
use Exception;
use GuzzleHttp\Promise\Create;
use GuzzleHttp\Promise\PromiseInterface;
use sdk\tools\HttpConnection;
use utils\RuntimeName;
use utils\Uri;
use utils\UtilsConst;

final class MessageHelper
{
    private const ADDRESS = 'https://dc.services.visualstudio.com/v2/track';
    private const DEFAULT_PACKAGE_VER = '2.0.0';
    private static ?MessageHelper $instance = null;
    private HttpConnection $connection;
    private string $instrumentationKey;
    private string $javonetVersion;
    private string $nodeName;
    private string $osName;

    private function __construct()
    {
        $this->connection = new HttpConnection(new Uri(self::ADDRESS));
        $this->instrumentationKey = getenv('JAVONET_INSTRUMENTATION_KEY') ?: '2c751560-90c8-40e9-b5dd-534566514723';
        $this->javonetVersion = $this->getJavonetVersion();
        $this->nodeName = $this->getHostName();
        $this->osName = php_uname('s');
    }

    public static function getInstance(): MessageHelper
    {
        if (self::$instance === null) {
            self::$instance = new MessageHelper();
        }
        return self::$instance;
    }

    public function sendMessageToAppInsights(string $operationName, string $message): PromiseInterface
    {
        try {
            $licenseKey = UtilsConst::getLicenseKey();
            if (strpos($message, 'BinariesUnloader exception') !== false && $licenseKey === 'javonet-functional-tests-key') {
                return Create::promiseFor(0);
            }

            $formattedDateTime = (new DateTime('now', new DateTimeZone('GMT')))
                ->format('Y-m-d\TH:i:s');

            $jsonPayload = sprintf("{\"name\":\"AppEvents\",\"time\":\"%s\",\"iKey\":\"%s\",\"tags\":{\"ai.application.ver\":\"%s\",\"ai.cloud.roleInstance\":\"%s\",\"ai.operation.id\":\"0\",\"ai.operation.parentId\":\"0\",\"ai.operation.name\":\"%s\",\"ai.internal.sdkVersion\":\"javonet:2\",\"ai.internal.nodeName\":\"%s\"},\"data\":{\"baseType\":\"EventData\",\"baseData\":{\"ver\":2,\"name\":\"%s\",\"properties\":{\"OperatingSystem\":\"%s\",\"LicenseKey\":\"%s\",\"CallingTechnology\":\"%s\"}}}}",
                $formattedDateTime, $this->instrumentationKey, $this->javonetVersion, $this->nodeName,
                $operationName, $this->nodeName, $message, $this->osName, $licenseKey, RuntimeName::PHP()->getName());

            return $this->connection->sendAsync($jsonPayload);

        } catch (Exception $e) {
            return Create::rejectionFor(-1);
        }
    }

    private function getJavonetVersion(): string
    {
        $composerJsonPath = dirname(__DIR__,4) . '/composer.json';
        if (!file_exists($composerJsonPath)) {
            return self::DEFAULT_PACKAGE_VER;
        }

        $composerJsonFile = json_decode(file_get_contents($composerJsonPath));
        if (json_last_error() !== JSON_ERROR_NONE || !isset($composerJsonFile->name)) {
            return self::DEFAULT_PACKAGE_VER;
        }

        $composerInstalledJsonPath = dirname(__DIR__, 3) . '/composer/installed.json';
        if (!file_exists($composerInstalledJsonPath)) {
            return self::DEFAULT_PACKAGE_VER;
        }

        $composerInstalledFile = json_decode(file_get_contents($composerInstalledJsonPath), true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return self::DEFAULT_PACKAGE_VER;
        }

        foreach ($composerInstalledFile['packages'] ?? [] as $package)
        {
            if ($package['name'] === $composerJsonFile->name) {
                return $package['version'] ?? self::DEFAULT_PACKAGE_VER;
            }
        }

        return self::DEFAULT_PACKAGE_VER;
    }

    private function getHostName(): string
    {
        return gethostname() ?: 'Unknown Host';
    }
}