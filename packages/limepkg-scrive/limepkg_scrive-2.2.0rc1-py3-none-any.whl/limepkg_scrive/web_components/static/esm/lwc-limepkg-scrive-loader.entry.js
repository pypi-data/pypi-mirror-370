import { r as registerInstance } from './index-e7f7b2d6.js';
import { C as Command, O as Operator, P as PlatformServiceName, a as SelectConfig, S as SelectSession } from './types-184d2acd.js';

var __decorate$1 = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
  else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
let EsignCommand = class EsignCommand {
};
EsignCommand = __decorate$1([
  Command({
    id: 'limepkg_scrive.esign',
  })
], EsignCommand);

class EsignHandler {
  constructor(notifications, query, config, language) {
    this.notifications = notifications;
    this.query = query;
    this.config = config;
    this.language = language;
    this.config = config;
  }
  async handle(command) {
    const limeDocIds = command.filter.exp;
    const scriveDocumentIds = await this.fetchScriveDocumentIds(limeDocIds);
    const isDocumentLimetype = command.context.limetype === 'document';
    const isInFilterExpression = command.filter && command.filter.op === 'IN' && command.filter.key === '_id';
    if (!isDocumentLimetype || !isInFilterExpression) {
      this.notifications.notify('The EsignCommand can only be run on document limetypes with a filter expression that includes _id.');
      return;
    }
    const { scriveHost, includePerson, includeCoworker, cloneDocument, target } = this.config;
    window.open(`${scriveHost}/public/?limeDocId=${limeDocIds.join(",")}&lang=${this.language}&usePerson=${includePerson}&useCoworker=${includeCoworker}&cloneDocument=${cloneDocument}&scriveDocId=${scriveDocumentIds.join(",")}`, target);
  }
  async fetchScriveDocumentIds(limeDocIds) {
    const results = await Promise.all(limeDocIds.map(limeDocId => this.query.execute({
      limetype: 'document',
      filter: {
        op: Operator.EQUALS,
        key: '_id',
        exp: limeDocId,
      },
      responseFormat: {
        object: {
          _id: '',
          scrive_document_id: '',
          scrive_document_status: '',
        },
      },
    })));
    return results.map(result => result.objects).map((obj) => obj[0].scrive_document_id || '');
  }
}

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
const Loader = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
  }
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
};
__decorate([
  SelectConfig({})
], Loader.prototype, "config", void 0);
__decorate([
  SelectSession()
], Loader.prototype, "session", void 0);

export { Loader as lwc_limepkg_scrive_loader };
