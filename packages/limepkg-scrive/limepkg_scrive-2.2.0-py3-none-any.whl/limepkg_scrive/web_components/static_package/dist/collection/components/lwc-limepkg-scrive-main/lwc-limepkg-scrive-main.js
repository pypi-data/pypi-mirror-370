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
import { PlatformServiceName, SelectConfig, SelectCurrentLimeObject, SelectSession, } from '@limetech/lime-web-components';
import { h } from '@stencil/core';
export class Main {
  constructor() {
    this.document = {};
    this.isOpen = false;
    this.allowedExtensions = Object.freeze(["PDF", "DOC", "DOCX"]);
    this.setCloneDocument = (event) => {
      event.stopPropagation();
      this.cloneDocument = event.detail;
    };
    this.openDialog = () => {
      this.isOpen = true;
    };
    this.closeDialog = () => {
      this.isOpen = false;
    };
  }
  goToScrive(id, scriveDocId) {
    var _a;
    const { scriveHost, includePerson, includeCoworker, target } = (_a = this.config) === null || _a === void 0 ? void 0 : _a.limepkg_scrive;
    const lang = this.session.language;
    window.open(`${scriveHost}/public/?limeDocId=${id}&lang=${lang}&usePerson=${includePerson}&useCoworker=${includeCoworker}&cloneDocument=${this.cloneDocument}&scriveDocId=${scriveDocId}`, target);
  }
  files() {
    var _a;
    const fileMap = ((_a = this.document) === null || _a === void 0 ? void 0 : _a._files) || {};
    const fileIds = Object.keys(fileMap);
    return fileIds.map(id => fileMap[id]);
  }
  isSignable(file) {
    return this.allowedExtensions.includes((file.extension || "").toUpperCase());
  }
  render() {
    var _a, _b, _c;
    if (this.context.limetype !== 'document') {
      return;
    }
    const signableFiles = this.files().filter(this.isSignable, this);
    const noSignableFiles = signableFiles.length === 0;
    const tooManySignableFiles = signableFiles.length > 1;
    if (noSignableFiles || tooManySignableFiles) {
      return;
    }
    const translate = this.platform.get(PlatformServiceName.Translate);
    const esignLabel = translate.get("limepkg_scrive.primary_action");
    const cloneLabel = translate.get("limepkg_scrive.clone_document");
    const cloneHintLabel = translate.get("limepkg_scrive.clone_hint");
    const cloneInfoLabel = translate.get("limepkg_scrive.clone_info");
    const okLabel = translate.get("limepkg_scrive.ok");
    return (h("section", null, h("limel-button", { id: "scrive_esign_button", label: esignLabel, outlined: true, icon: "signature", onClick: () => { var _a; return this.goToScrive(this.context.id, (_a = this.document) === null || _a === void 0 ? void 0 : _a.scrive_document_id); } }), h("p", null, h("limel-flex-container", { justify: "start" }, h("limel-checkbox", { label: cloneLabel, checked: (_a = this.cloneDocument) !== null && _a !== void 0 ? _a : (_c = (_b = this.config) === null || _b === void 0 ? void 0 : _b.limepkg_scrive) === null || _c === void 0 ? void 0 : _c.cloneDocument, onChange: this.setCloneDocument }), h("limel-icon-button", { icon: "question_mark", label: cloneHintLabel, onClick: this.openDialog }))), h("limel-dialog", { open: this.isOpen, onClose: this.closeDialog }, h("p", null, cloneInfoLabel), h("limel-button", { label: okLabel, onClick: this.closeDialog, slot: "button" }))));
  }
  static get is() { return "lwc-limepkg-scrive"; }
  static get encapsulation() { return "shadow"; }
  static get originalStyleUrls() {
    return {
      "$": ["lwc-limepkg-scrive-main.scss"]
    };
  }
  static get styleUrls() {
    return {
      "$": ["lwc-limepkg-scrive-main.css"]
    };
  }
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
  static get states() {
    return {
      "document": {},
      "session": {},
      "config": {},
      "cloneDocument": {},
      "isOpen": {}
    };
  }
}
__decorate([
  SelectCurrentLimeObject()
], Main.prototype, "document", void 0);
__decorate([
  SelectSession()
], Main.prototype, "session", void 0);
__decorate([
  SelectConfig({})
], Main.prototype, "config", void 0);
