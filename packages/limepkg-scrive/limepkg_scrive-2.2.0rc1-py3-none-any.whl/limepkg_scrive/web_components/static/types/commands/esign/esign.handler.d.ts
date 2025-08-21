import { CommandHandler, Notifications, QueryService } from '@limetech/lime-web-components';
import { EsignCommand } from './esign.command';
import { OurAwesomePackageConfig } from 'src/types';
export declare class EsignHandler implements CommandHandler {
  private notifications;
  private query;
  private config;
  private language;
  constructor(notifications: Notifications, query: QueryService, config: OurAwesomePackageConfig, language: string);
  handle(command: EsignCommand): Promise<void>;
  private fetchScriveDocumentIds;
}
