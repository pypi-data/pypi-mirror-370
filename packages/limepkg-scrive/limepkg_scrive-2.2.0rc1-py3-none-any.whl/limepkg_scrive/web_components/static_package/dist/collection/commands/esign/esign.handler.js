import { Operator } from '@limetech/lime-web-components';
export class EsignHandler {
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
