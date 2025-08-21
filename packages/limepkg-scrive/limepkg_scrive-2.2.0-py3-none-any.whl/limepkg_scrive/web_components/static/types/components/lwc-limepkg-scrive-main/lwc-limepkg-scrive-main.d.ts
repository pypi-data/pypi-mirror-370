import { LimeWebComponent, LimeWebComponentContext, LimeWebComponentPlatform } from '@limetech/lime-web-components';
export declare class Main implements LimeWebComponent {
  /**
   * @inherit
   */
  platform: LimeWebComponentPlatform;
  /**
   * @inherit
   */
  context: LimeWebComponentContext;
  private document;
  private session;
  private config;
  private cloneDocument;
  private isOpen;
  private goToScrive;
  private files;
  private allowedExtensions;
  private isSignable;
  private setCloneDocument;
  private openDialog;
  private closeDialog;
  render(): any;
}
