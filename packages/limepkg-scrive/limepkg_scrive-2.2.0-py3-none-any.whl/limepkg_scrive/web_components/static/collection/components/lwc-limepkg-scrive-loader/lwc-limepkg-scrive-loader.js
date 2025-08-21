var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function")
    r = Reflect.decorate(decorators, target, key, desc);
  else
    for (var i = decorators.length - 1; i >= 0; i--)
      if (d = decorators[i])
        r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
import { PlatformServiceName, SelectConfig, SelectSession, } from '@limetech/lime-web-components';
import { EsignCommand } from 'src/commands/esign/esign.command';
import { EsignHandler } from 'src/commands/esign/esign.handler';
// NOTE: Do NOT remove this component, it is required to run the plugin correctly.
// However, if your plugin has any code that should run only once when the application
// starts, you are free to use the component lifecycle methods below to do so.
// The component should never render anything, so do NOT implement a render method.
export class Loader {
  connectedCallback() { }
  componentWillLoad() {
    const language = this.session.language;
    const handler = new EsignHandler(this.notificationService, this.queryService, this.config.limepkg_scrive, language);
    this.commandBus.register(EsignCommand, handler);
  }
  componentWillUpdate() { }
  disconnectedCallback() { }
  get notificationService() {
    return this.platform.get(PlatformServiceName.Notification);
  }
  get queryService() {
    return this.platform.get(PlatformServiceName.Query);
  }
  get commandBus() {
    return this.platform.get(PlatformServiceName.CommandBus);
  }
  static get is() { return "lwc-limepkg-scrive-loader"; }
  static get encapsulation() { return "shadow"; }
  static get properties() {
    return {
      "platform": {
        "type": "unknown",
        "mutable": false,
        "complexType": {
          "original": "LimeWebComponentPlatform",
          "resolved": "LimeWebComponentPlatform",
          "references": {
            "LimeWebComponentPlatform": {
              "location": "import",
              "path": "@limetech/lime-web-components"
            }
          }
        },
        "required": false,
        "optional": false,
        "docs": {
          "tags": [{
              "name": "inherit",
              "text": undefined
            }],
          "text": "Reference to the platform"
        }
      },
      "context": {
        "type": "unknown",
        "mutable": false,
        "complexType": {
          "original": "LimeWebComponentContext",
          "resolved": "LimeWebComponentContext",
          "references": {
            "LimeWebComponentContext": {
              "location": "import",
              "path": "@limetech/lime-web-components"
            }
          }
        },
        "required": false,
        "optional": false,
        "docs": {
          "tags": [{
              "name": "inherit",
              "text": undefined
            }],
          "text": "The context this component belongs to"
        }
      }
    };
  }
}
__decorate([
  SelectConfig({})
], Loader.prototype, "config", void 0);
__decorate([
  SelectSession()
], Loader.prototype, "session", void 0);
