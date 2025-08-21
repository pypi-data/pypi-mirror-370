import { p as promiseResolve, b as bootstrapLazy } from './index-e7f7b2d6.js';

/*
 Stencil Client Patch Esm v2.18.1 | MIT Licensed | https://stenciljs.com
 */
const patchEsm = () => {
    return promiseResolve();
};

const defineCustomElements = (win, options) => {
  if (typeof window === 'undefined') return Promise.resolve();
  return patchEsm().then(() => {
  return bootstrapLazy([["lwc-limepkg-scrive",[[1,"lwc-limepkg-scrive",{"platform":[16],"context":[16],"document":[32],"session":[32],"config":[32],"cloneDocument":[32],"isOpen":[32]}]]],["lwc-limepkg-scrive-loader",[[1,"lwc-limepkg-scrive-loader",{"platform":[16],"context":[16]}]]]], options);
  });
};

export { defineCustomElements };
