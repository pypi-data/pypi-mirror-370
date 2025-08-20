"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var SdkExceptionHelper_exports = {};
__export(SdkExceptionHelper_exports, {
  sendExceptionToAppInsights: () => sendExceptionToAppInsights
});
module.exports = __toCommonJS(SdkExceptionHelper_exports);
var import_Runtime = require("../../../utils/Runtime.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
let https = null;
let os = null;
const address = "https://dc.services.visualstudio.com/v2/track";
if ((0, import_Runtime.isNodejsRuntime)()) {
  try {
    https = requireDynamic("https", import_meta.url);
    os = requireDynamic("os", import_meta.url);
  } catch (error) {
    throw error;
  }
}
function sendExceptionToAppInsights(e, licenseKey) {
  return new Promise((resolve, reject) => {
    try {
      const instrumentationKey = "2c751560-90c8-40e9-b5dd-534566514723";
      const javonetVersion = "2.0.0";
      const nodeName = os.hostname();
      const operationName = "JavonetSdkException";
      const osName = os.platform();
      const callingRuntimeName = "Nodejs";
      const eventMessage = e.message;
      const nowGMT = (/* @__PURE__ */ new Date()).toISOString();
      const jsonPayload = JSON.stringify({
        name: "AppEvents",
        time: nowGMT,
        iKey: instrumentationKey,
        tags: {
          "ai.application.ver": javonetVersion,
          "ai.cloud.roleInstance": nodeName,
          "ai.operation.id": "0",
          "ai.operation.parentId": "0",
          "ai.operation.name": operationName,
          "ai.internal.sdkVersion": "javonet:" + javonetVersion,
          "ai.internal.nodeName": nodeName
        },
        data: {
          baseType: "EventData",
          baseData: {
            ver: 2,
            name: eventMessage,
            properties: {
              OperatingSystem: osName,
              LicenseKey: licenseKey,
              CallingTechnology: callingRuntimeName
            }
          }
        }
      });
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": jsonPayload.length
        }
      };
      const req = https.request(address, options, (res) => {
        console.log("POST Response Code ::", res.statusCode);
        resolve(res.statusCode);
      });
      req.on("error", (error) => {
        console.error(error);
        reject(error);
      });
      req.write(jsonPayload);
      req.end();
    } catch (error) {
      reject(error);
    }
  });
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  sendExceptionToAppInsights
});
