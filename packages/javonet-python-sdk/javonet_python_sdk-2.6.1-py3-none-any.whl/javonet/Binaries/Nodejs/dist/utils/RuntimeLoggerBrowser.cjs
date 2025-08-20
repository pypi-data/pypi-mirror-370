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
var RuntimeLoggerBrowser_exports = {};
__export(RuntimeLoggerBrowser_exports, {
  RuntimeLoggerBrowser: () => RuntimeLoggerBrowser
});
module.exports = __toCommonJS(RuntimeLoggerBrowser_exports);
class RuntimeLoggerBrowser {
  static notLoggedYet = true;
  /**
   * Gets runtime information in a browser environment.
   * @method
   * @returns {string}
   */
  static getRuntimeInfo() {
    try {
      return `JavaScript Managed Runtime Info:
User-Agent: ${navigator.userAgent}
Language: ${navigator.language}
`;
    } catch (error) {
      return "JavaScript Managed Runtime Info: Error while fetching runtime info";
    }
  }
  /**
   * Prints runtime information to the console.
   * @method
   * @returns {void}
   */
  static printRuntimeInfo() {
    if (this.notLoggedYet) {
      console.log(this.getRuntimeInfo());
      this.notLoggedYet = false;
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeLoggerBrowser
});
