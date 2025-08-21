'use strict';

const index = require('./index-c74a2cd5.js');

/*
 Stencil Client Patch Browser v2.18.1 | MIT Licensed | https://stenciljs.com
 */
const patchBrowser = () => {
    const importMeta = (typeof document === 'undefined' ? new (require('u' + 'rl').URL)('file:' + __filename).href : (document.currentScript && document.currentScript.src || new URL('limepkg-scrive-lwc-components.cjs.js', document.baseURI).href));
    const opts = {};
    if (importMeta !== '') {
        opts.resourcesUrl = new URL('.', importMeta).href;
    }
    return index.promiseResolve(opts);
};

patchBrowser().then(options => {
  return index.bootstrapLazy([["lwc-limepkg-scrive.cjs",[[1,"lwc-limepkg-scrive",{"platform":[16],"context":[16],"document":[32],"session":[32],"config":[32],"cloneDocument":[32],"isOpen":[32]}]]],["lwc-limepkg-scrive-loader.cjs",[[1,"lwc-limepkg-scrive-loader",{"platform":[16],"context":[16]}]]]], options);
});
