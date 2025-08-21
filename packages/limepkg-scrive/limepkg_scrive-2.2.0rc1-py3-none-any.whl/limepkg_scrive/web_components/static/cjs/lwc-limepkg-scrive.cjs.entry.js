'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const index = require('./index-c74a2cd5.js');
const types = require('./types-f1bea775.js');

/**
 * Get the limeobject for the current context
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Lime objects
 */
function SelectCurrentLimeObject(options = {}) {
    const config = {
        name: types.PlatformServiceName.LimeObjectRepository,
    };
    options.map = [currentLimeobject, ...(options.map || [])];
    options.context = null;
    return types.createStateDecorator(options, config);
}
function currentLimeobject(limeobjects) {
    const { limetype, id } = this.context;
    if (!limeobjects[limetype]) {
        return undefined;
    }
    return limeobjects[limetype].find((object) => object.id === id);
}

const lwcLimepkgScriveMainCss = ".container{margin-left:1.25rem;margin-right:1.25rem}#scrive_esign_button{isolation:isolate;position:relative}#scrive_esign_button:after{content:\"\";display:block;width:1.5rem;height:1.5rem;position:absolute;z-index:1;top:0;left:0.25rem;bottom:0;margin:auto;background-image:url(\"data:image/svg+xml; utf8, <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128.9 116.04'><defs><style>.cls-1{fill:none;}.cls-2{fill:%2327282d;}</style></defs><g id='Layer_2' data-name='Layer 2'><g id='S_Mark_Dark' data-name='S Mark Dark'><g id='S_Black' data-name='S Black'><rect class='cls-1' width='128.9' height='116.04'/><path class='cls-2' d='M65.51,65.48a29.87,29.87,0,0,1,7.76,2,7.3,7.3,0,0,1,3.62,3,8.64,8.64,0,0,1,1,4.35A10.34,10.34,0,0,1,76,80.71a12.35,12.35,0,0,1-4.64,3.53c-4.65,2.1-11.05,2.69-16.06,2.73A40.35,40.35,0,0,1,44,85.53,20.24,20.24,0,0,1,36.8,82,13.63,13.63,0,0,1,33,77.1,13.1,13.1,0,0,1,31.86,72H17.67A28.57,28.57,0,0,0,20.6,83a22,22,0,0,0,6.22,7.55,31.48,31.48,0,0,0,8.63,4.6,48.07,48.07,0,0,0,9.91,2.31,75.66,75.66,0,0,0,10.35.63c10.94,0,25-2.14,32.12-11.44A22.22,22.22,0,0,0,92.07,73.2a18,18,0,0,0-1.61-7.8A19.6,19.6,0,0,0,86,59.48a22.44,22.44,0,0,0-6.43-4,29.84,29.84,0,0,0-7.69-2.1C63.47,52.2,44.59,50.46,39.22,48A7.21,7.21,0,0,1,35.56,45a7.69,7.69,0,0,1-1-4.3,8.74,8.74,0,0,1,1.72-5.52,12.69,12.69,0,0,1,4.6-3.53,26.67,26.67,0,0,1,6.37-1.85,43.93,43.93,0,0,1,6.88-.55,34.38,34.38,0,0,1,12.25,2,17.4,17.4,0,0,1,7.35,5,11.88,11.88,0,0,1,2.67,7H90.64A27.58,27.58,0,0,0,87.9,33.17a24.4,24.4,0,0,0-6.73-8,31.92,31.92,0,0,0-11-5.19,60.15,60.15,0,0,0-15.84-1.92A52.27,52.27,0,0,0,36.22,21a25.4,25.4,0,0,0-11.67,8.24,20.92,20.92,0,0,0-4.17,13A18.17,18.17,0,0,0,26.49,56,22.45,22.45,0,0,0,32.92,60a29.63,29.63,0,0,0,7.61,2.06C48.91,63.23,57.21,64.37,65.51,65.48Z'/><path class='cls-2' d='M111.23,89.19a8.84,8.84,0,1,1-8.84-8.88A8.87,8.87,0,0,1,111.23,89.19Z'/></g></g></g></svg>\");background-color:var(--lime-elevated-surface-background-color);background-size:contain;background-repeat:no-repeat;background-position:center}";

var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function")
    r = Reflect.decorate(decorators, target, key, desc);
  else
    for (var i = decorators.length - 1; i >= 0; i--)
      if (d = decorators[i])
        r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
const Main = class {
  constructor(hostRef) {
    index.registerInstance(this, hostRef);
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
    const translate = this.platform.get(types.PlatformServiceName.Translate);
    const esignLabel = translate.get("limepkg_scrive.primary_action");
    const cloneLabel = translate.get("limepkg_scrive.clone_document");
    const cloneHintLabel = translate.get("limepkg_scrive.clone_hint");
    const cloneInfoLabel = translate.get("limepkg_scrive.clone_info");
    const okLabel = translate.get("limepkg_scrive.ok");
    return (index.h("section", null, index.h("limel-button", { id: "scrive_esign_button", label: esignLabel, outlined: true, icon: "signature", onClick: () => { var _a; return this.goToScrive(this.context.id, (_a = this.document) === null || _a === void 0 ? void 0 : _a.scrive_document_id); } }), index.h("p", null, index.h("limel-flex-container", { justify: "start" }, index.h("limel-checkbox", { label: cloneLabel, checked: (_a = this.cloneDocument) !== null && _a !== void 0 ? _a : (_c = (_b = this.config) === null || _b === void 0 ? void 0 : _b.limepkg_scrive) === null || _c === void 0 ? void 0 : _c.cloneDocument, onChange: this.setCloneDocument }), index.h("limel-icon-button", { icon: "question_mark", label: cloneHintLabel, onClick: this.openDialog }))), index.h("limel-dialog", { open: this.isOpen, onClose: this.closeDialog }, index.h("p", null, cloneInfoLabel), index.h("limel-button", { label: okLabel, onClick: this.closeDialog, slot: "button" }))));
  }
};
__decorate([
  SelectCurrentLimeObject()
], Main.prototype, "document", void 0);
__decorate([
  types.SelectSession()
], Main.prototype, "session", void 0);
__decorate([
  types.SelectConfig({})
], Main.prototype, "config", void 0);
Main.style = lwcLimepkgScriveMainCss;

exports.lwc_limepkg_scrive = Main;
