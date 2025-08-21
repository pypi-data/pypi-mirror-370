'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const index = require('./index-c74a2cd5.js');

/*
 Stencil Client Patch Esm v2.18.1 | MIT Licensed | https://stenciljs.com
 */
const patchEsm = () => {
    return index.promiseResolve();
};

const defineCustomElements = (win, options) => {
  if (typeof window === 'undefined') return Promise.resolve();
  return patchEsm().then(() => {
  return index.bootstrapLazy([["lwc-limepkg-scrive.cjs",[[1,"lwc-limepkg-scrive",{"platform":[16],"context":[16],"document":[32],"session":[32],"config":[32],"cloneDocument":[32],"isOpen":[32]}]]],["lwc-limepkg-scrive-loader.cjs",[[1,"lwc-limepkg-scrive-loader",{"platform":[16],"context":[16]}]]]], options);
  });
};

exports.defineCustomElements = defineCustomElements;
