import { g as getElement } from './index-e7f7b2d6.js';

/**
 * Core platform service names
 * @public
 * @group Core
 */
const PlatformServiceName = {
    Route: 'route',
};

const SERVICE_NAME$m = 'state.limetypes';
PlatformServiceName.LimeTypeRepository = SERVICE_NAME$m;

function isFunction(value) {
    return typeof value === 'function';
}

function createErrorClass(createImpl) {
    const _super = (instance) => {
        Error.call(instance);
        instance.stack = new Error().stack;
    };
    const ctorFunc = createImpl(_super);
    ctorFunc.prototype = Object.create(Error.prototype);
    ctorFunc.prototype.constructor = ctorFunc;
    return ctorFunc;
}

const UnsubscriptionError = createErrorClass((_super) => function UnsubscriptionErrorImpl(errors) {
    _super(this);
    this.message = errors
        ? `${errors.length} errors occurred during unsubscription:
${errors.map((err, i) => `${i + 1}) ${err.toString()}`).join('\n  ')}`
        : '';
    this.name = 'UnsubscriptionError';
    this.errors = errors;
});

function arrRemove(arr, item) {
    if (arr) {
        const index = arr.indexOf(item);
        0 <= index && arr.splice(index, 1);
    }
}

class Subscription {
    constructor(initialTeardown) {
        this.initialTeardown = initialTeardown;
        this.closed = false;
        this._parentage = null;
        this._finalizers = null;
    }
    unsubscribe() {
        let errors;
        if (!this.closed) {
            this.closed = true;
            const { _parentage } = this;
            if (_parentage) {
                this._parentage = null;
                if (Array.isArray(_parentage)) {
                    for (const parent of _parentage) {
                        parent.remove(this);
                    }
                }
                else {
                    _parentage.remove(this);
                }
            }
            const { initialTeardown: initialFinalizer } = this;
            if (isFunction(initialFinalizer)) {
                try {
                    initialFinalizer();
                }
                catch (e) {
                    errors = e instanceof UnsubscriptionError ? e.errors : [e];
                }
            }
            const { _finalizers } = this;
            if (_finalizers) {
                this._finalizers = null;
                for (const finalizer of _finalizers) {
                    try {
                        execFinalizer(finalizer);
                    }
                    catch (err) {
                        errors = errors !== null && errors !== void 0 ? errors : [];
                        if (err instanceof UnsubscriptionError) {
                            errors = [...errors, ...err.errors];
                        }
                        else {
                            errors.push(err);
                        }
                    }
                }
            }
            if (errors) {
                throw new UnsubscriptionError(errors);
            }
        }
    }
    add(teardown) {
        var _a;
        if (teardown && teardown !== this) {
            if (this.closed) {
                execFinalizer(teardown);
            }
            else {
                if (teardown instanceof Subscription) {
                    if (teardown.closed || teardown._hasParent(this)) {
                        return;
                    }
                    teardown._addParent(this);
                }
                (this._finalizers = (_a = this._finalizers) !== null && _a !== void 0 ? _a : []).push(teardown);
            }
        }
    }
    _hasParent(parent) {
        const { _parentage } = this;
        return _parentage === parent || (Array.isArray(_parentage) && _parentage.includes(parent));
    }
    _addParent(parent) {
        const { _parentage } = this;
        this._parentage = Array.isArray(_parentage) ? (_parentage.push(parent), _parentage) : _parentage ? [_parentage, parent] : parent;
    }
    _removeParent(parent) {
        const { _parentage } = this;
        if (_parentage === parent) {
            this._parentage = null;
        }
        else if (Array.isArray(_parentage)) {
            arrRemove(_parentage, parent);
        }
    }
    remove(teardown) {
        const { _finalizers } = this;
        _finalizers && arrRemove(_finalizers, teardown);
        if (teardown instanceof Subscription) {
            teardown._removeParent(this);
        }
    }
}
Subscription.EMPTY = (() => {
    const empty = new Subscription();
    empty.closed = true;
    return empty;
})();
const EMPTY_SUBSCRIPTION = Subscription.EMPTY;
function isSubscription(value) {
    return (value instanceof Subscription ||
        (value && 'closed' in value && isFunction(value.remove) && isFunction(value.add) && isFunction(value.unsubscribe)));
}
function execFinalizer(finalizer) {
    if (isFunction(finalizer)) {
        finalizer();
    }
    else {
        finalizer.unsubscribe();
    }
}

const config = {
    onUnhandledError: null,
    onStoppedNotification: null,
    Promise: undefined,
    useDeprecatedSynchronousErrorHandling: false,
    useDeprecatedNextContext: false,
};

const timeoutProvider = {
    setTimeout(handler, timeout, ...args) {
        const { delegate } = timeoutProvider;
        if (delegate === null || delegate === void 0 ? void 0 : delegate.setTimeout) {
            return delegate.setTimeout(handler, timeout, ...args);
        }
        return setTimeout(handler, timeout, ...args);
    },
    clearTimeout(handle) {
        const { delegate } = timeoutProvider;
        return ((delegate === null || delegate === void 0 ? void 0 : delegate.clearTimeout) || clearTimeout)(handle);
    },
    delegate: undefined,
};

function reportUnhandledError(err) {
    timeoutProvider.setTimeout(() => {
        const { onUnhandledError } = config;
        if (onUnhandledError) {
            onUnhandledError(err);
        }
        else {
            throw err;
        }
    });
}

function noop() { }

const COMPLETE_NOTIFICATION = (() => createNotification('C', undefined, undefined))();
function errorNotification(error) {
    return createNotification('E', undefined, error);
}
function nextNotification(value) {
    return createNotification('N', value, undefined);
}
function createNotification(kind, value, error) {
    return {
        kind,
        value,
        error,
    };
}

function errorContext(cb) {
    {
        cb();
    }
}

class Subscriber extends Subscription {
    constructor(destination) {
        super();
        this.isStopped = false;
        if (destination) {
            this.destination = destination;
            if (isSubscription(destination)) {
                destination.add(this);
            }
        }
        else {
            this.destination = EMPTY_OBSERVER;
        }
    }
    static create(next, error, complete) {
        return new SafeSubscriber(next, error, complete);
    }
    next(value) {
        if (this.isStopped) {
            handleStoppedNotification(nextNotification(value), this);
        }
        else {
            this._next(value);
        }
    }
    error(err) {
        if (this.isStopped) {
            handleStoppedNotification(errorNotification(err), this);
        }
        else {
            this.isStopped = true;
            this._error(err);
        }
    }
    complete() {
        if (this.isStopped) {
            handleStoppedNotification(COMPLETE_NOTIFICATION, this);
        }
        else {
            this.isStopped = true;
            this._complete();
        }
    }
    unsubscribe() {
        if (!this.closed) {
            this.isStopped = true;
            super.unsubscribe();
            this.destination = null;
        }
    }
    _next(value) {
        this.destination.next(value);
    }
    _error(err) {
        try {
            this.destination.error(err);
        }
        finally {
            this.unsubscribe();
        }
    }
    _complete() {
        try {
            this.destination.complete();
        }
        finally {
            this.unsubscribe();
        }
    }
}
const _bind = Function.prototype.bind;
function bind(fn, thisArg) {
    return _bind.call(fn, thisArg);
}
class ConsumerObserver {
    constructor(partialObserver) {
        this.partialObserver = partialObserver;
    }
    next(value) {
        const { partialObserver } = this;
        if (partialObserver.next) {
            try {
                partialObserver.next(value);
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
    }
    error(err) {
        const { partialObserver } = this;
        if (partialObserver.error) {
            try {
                partialObserver.error(err);
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
        else {
            handleUnhandledError(err);
        }
    }
    complete() {
        const { partialObserver } = this;
        if (partialObserver.complete) {
            try {
                partialObserver.complete();
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
    }
}
class SafeSubscriber extends Subscriber {
    constructor(observerOrNext, error, complete) {
        super();
        let partialObserver;
        if (isFunction(observerOrNext) || !observerOrNext) {
            partialObserver = {
                next: (observerOrNext !== null && observerOrNext !== void 0 ? observerOrNext : undefined),
                error: error !== null && error !== void 0 ? error : undefined,
                complete: complete !== null && complete !== void 0 ? complete : undefined,
            };
        }
        else {
            let context;
            if (this && config.useDeprecatedNextContext) {
                context = Object.create(observerOrNext);
                context.unsubscribe = () => this.unsubscribe();
                partialObserver = {
                    next: observerOrNext.next && bind(observerOrNext.next, context),
                    error: observerOrNext.error && bind(observerOrNext.error, context),
                    complete: observerOrNext.complete && bind(observerOrNext.complete, context),
                };
            }
            else {
                partialObserver = observerOrNext;
            }
        }
        this.destination = new ConsumerObserver(partialObserver);
    }
}
function handleUnhandledError(error) {
    {
        reportUnhandledError(error);
    }
}
function defaultErrorHandler(err) {
    throw err;
}
function handleStoppedNotification(notification, subscriber) {
    const { onStoppedNotification } = config;
    onStoppedNotification && timeoutProvider.setTimeout(() => onStoppedNotification(notification, subscriber));
}
const EMPTY_OBSERVER = {
    closed: true,
    next: noop,
    error: defaultErrorHandler,
    complete: noop,
};

const observable = (() => (typeof Symbol === 'function' && Symbol.observable) || '@@observable')();

function identity(x) {
    return x;
}

function pipeFromArray(fns) {
    if (fns.length === 0) {
        return identity;
    }
    if (fns.length === 1) {
        return fns[0];
    }
    return function piped(input) {
        return fns.reduce((prev, fn) => fn(prev), input);
    };
}

class Observable {
    constructor(subscribe) {
        if (subscribe) {
            this._subscribe = subscribe;
        }
    }
    lift(operator) {
        const observable = new Observable();
        observable.source = this;
        observable.operator = operator;
        return observable;
    }
    subscribe(observerOrNext, error, complete) {
        const subscriber = isSubscriber(observerOrNext) ? observerOrNext : new SafeSubscriber(observerOrNext, error, complete);
        errorContext(() => {
            const { operator, source } = this;
            subscriber.add(operator
                ?
                    operator.call(subscriber, source)
                : source
                    ?
                        this._subscribe(subscriber)
                    :
                        this._trySubscribe(subscriber));
        });
        return subscriber;
    }
    _trySubscribe(sink) {
        try {
            return this._subscribe(sink);
        }
        catch (err) {
            sink.error(err);
        }
    }
    forEach(next, promiseCtor) {
        promiseCtor = getPromiseCtor(promiseCtor);
        return new promiseCtor((resolve, reject) => {
            const subscriber = new SafeSubscriber({
                next: (value) => {
                    try {
                        next(value);
                    }
                    catch (err) {
                        reject(err);
                        subscriber.unsubscribe();
                    }
                },
                error: reject,
                complete: resolve,
            });
            this.subscribe(subscriber);
        });
    }
    _subscribe(subscriber) {
        var _a;
        return (_a = this.source) === null || _a === void 0 ? void 0 : _a.subscribe(subscriber);
    }
    [observable]() {
        return this;
    }
    pipe(...operations) {
        return pipeFromArray(operations)(this);
    }
    toPromise(promiseCtor) {
        promiseCtor = getPromiseCtor(promiseCtor);
        return new promiseCtor((resolve, reject) => {
            let value;
            this.subscribe((x) => (value = x), (err) => reject(err), () => resolve(value));
        });
    }
}
Observable.create = (subscribe) => {
    return new Observable(subscribe);
};
function getPromiseCtor(promiseCtor) {
    var _a;
    return (_a = promiseCtor !== null && promiseCtor !== void 0 ? promiseCtor : config.Promise) !== null && _a !== void 0 ? _a : Promise;
}
function isObserver(value) {
    return value && isFunction(value.next) && isFunction(value.error) && isFunction(value.complete);
}
function isSubscriber(value) {
    return (value && value instanceof Subscriber) || (isObserver(value) && isSubscription(value));
}

const ObjectUnsubscribedError = createErrorClass((_super) => function ObjectUnsubscribedErrorImpl() {
    _super(this);
    this.name = 'ObjectUnsubscribedError';
    this.message = 'object unsubscribed';
});

class Subject extends Observable {
    constructor() {
        super();
        this.closed = false;
        this.currentObservers = null;
        this.observers = [];
        this.isStopped = false;
        this.hasError = false;
        this.thrownError = null;
    }
    lift(operator) {
        const subject = new AnonymousSubject(this, this);
        subject.operator = operator;
        return subject;
    }
    _throwIfClosed() {
        if (this.closed) {
            throw new ObjectUnsubscribedError();
        }
    }
    next(value) {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                if (!this.currentObservers) {
                    this.currentObservers = Array.from(this.observers);
                }
                for (const observer of this.currentObservers) {
                    observer.next(value);
                }
            }
        });
    }
    error(err) {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                this.hasError = this.isStopped = true;
                this.thrownError = err;
                const { observers } = this;
                while (observers.length) {
                    observers.shift().error(err);
                }
            }
        });
    }
    complete() {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                this.isStopped = true;
                const { observers } = this;
                while (observers.length) {
                    observers.shift().complete();
                }
            }
        });
    }
    unsubscribe() {
        this.isStopped = this.closed = true;
        this.observers = this.currentObservers = null;
    }
    get observed() {
        var _a;
        return ((_a = this.observers) === null || _a === void 0 ? void 0 : _a.length) > 0;
    }
    _trySubscribe(subscriber) {
        this._throwIfClosed();
        return super._trySubscribe(subscriber);
    }
    _subscribe(subscriber) {
        this._throwIfClosed();
        this._checkFinalizedStatuses(subscriber);
        return this._innerSubscribe(subscriber);
    }
    _innerSubscribe(subscriber) {
        const { hasError, isStopped, observers } = this;
        if (hasError || isStopped) {
            return EMPTY_SUBSCRIPTION;
        }
        this.currentObservers = null;
        observers.push(subscriber);
        return new Subscription(() => {
            this.currentObservers = null;
            arrRemove(observers, subscriber);
        });
    }
    _checkFinalizedStatuses(subscriber) {
        const { hasError, thrownError, isStopped } = this;
        if (hasError) {
            subscriber.error(thrownError);
        }
        else if (isStopped) {
            subscriber.complete();
        }
    }
    asObservable() {
        const observable = new Observable();
        observable.source = this;
        return observable;
    }
}
Subject.create = (destination, source) => {
    return new AnonymousSubject(destination, source);
};
class AnonymousSubject extends Subject {
    constructor(destination, source) {
        super();
        this.destination = destination;
        this.source = source;
    }
    next(value) {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.next) === null || _b === void 0 ? void 0 : _b.call(_a, value);
    }
    error(err) {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.error) === null || _b === void 0 ? void 0 : _b.call(_a, err);
    }
    complete() {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.complete) === null || _b === void 0 ? void 0 : _b.call(_a);
    }
    _subscribe(subscriber) {
        var _a, _b;
        return (_b = (_a = this.source) === null || _a === void 0 ? void 0 : _a.subscribe(subscriber)) !== null && _b !== void 0 ? _b : EMPTY_SUBSCRIPTION;
    }
}

class BehaviorSubject extends Subject {
    constructor(_value) {
        super();
        this._value = _value;
    }
    get value() {
        return this.getValue();
    }
    _subscribe(subscriber) {
        const subscription = super._subscribe(subscriber);
        !subscription.closed && subscriber.next(this._value);
        return subscription;
    }
    getValue() {
        const { hasError, thrownError, _value } = this;
        if (hasError) {
            throw thrownError;
        }
        this._throwIfClosed();
        return _value;
    }
    next(value) {
        super.next((this._value = value));
    }
}

function defaultOptionFactory(options) {
    return options;
}
/**
 * Create a new state decorator
 *
 * @param options - decorator options
 * @param config - decorator configuration
 * @returns state decorator
 * @public
 */
function createStateDecorator(options, config) {
    return (target, property) => {
        const properties = getComponentProperties(target, property, options, config);
        if (properties.length === 1) {
            extendLifecycleMethods(target, properties);
        }
    };
}
const componentProperties = new WeakMap();
const componentSubscriptions = new WeakMap();
const connectedComponents = new WeakMap();
/**
 * Get properties data for a component
 *
 * @param component - the component class containing the decorator
 * @param property - name of the property
 * @param options - decorator options
 * @param config - decorator configuration
 * @returns properties data for the component
 */
function getComponentProperties(component, property, options, config) {
    let properties = componentProperties.get(component);
    if (!properties) {
        properties = [];
        componentProperties.set(component, properties);
    }
    properties.push({
        options: options,
        name: property,
        optionFactory: config.optionFactory || defaultOptionFactory,
        service: {
            name: config.name,
            method: config.method || 'subscribe',
        },
    });
    return properties;
}
/**
 * Extend the lifecycle methods on the component
 *
 * @param component - the component to extend
 * @param properties - the properties with which to extend the component
 * @returns
 */
function extendLifecycleMethods(component, properties) {
    // `componentWillLoad` and `componentDidUnload` is included for backwards
    // compatibility reasons. The correct way to setup the subscriptions is in
    // `connectedCallback` and `disconnectedCallback`, but since not all
    // plugins might implement those methods yet we still have include them
    // until we make `connectedCallback` and `disconnectedCallback` required
    // on the interface.
    component.connectedCallback = createConnectedCallback(component.connectedCallback, properties);
    component.componentWillLoad = createComponentWillLoad(component.componentWillLoad, properties);
    component.componentDidUnload = createDisconnectedCallback(component.componentDidUnload);
    component.disconnectedCallback = createDisconnectedCallback(component.disconnectedCallback);
}
function createConnectedCallback(original, properties) {
    return async function (...args) {
        connectedComponents.set(this, true);
        componentSubscriptions.set(this, []);
        await ensureLimeProps(this);
        const observable = new BehaviorSubject(this.context);
        watchProp(this, 'context', observable);
        properties.forEach((property) => {
            property.options = property.optionFactory(property.options, this);
            if (isContextAware(property.options)) {
                property.options.context = observable;
            }
            subscribe(this, property);
        });
        if (original) {
            return original.apply(this, args);
        }
    };
}
function createComponentWillLoad(original, properties) {
    return async function (...args) {
        if (connectedComponents.get(this) === true) {
            await ensureLimeProps(this);
            if (original) {
                return original.apply(this, args);
            }
            return;
        }
        const connectedCallback = createConnectedCallback(original, properties);
        return connectedCallback.apply(this, args);
    };
}
function createDisconnectedCallback(original) {
    return async function (...args) {
        let result;
        if (original) {
            result = original.apply(this, args);
        }
        unsubscribeAll(this);
        return result;
    };
}
/**
 * Check if the options are context aware
 *
 * @param options - state decorator options
 * @returns true if the options are context aware
 */
function isContextAware(options) {
    return 'context' in options;
}
/**
 * Make sure that all required lime properties are set on the web component
 *
 * @param target - the web component
 * @returns a promise that resolves when all properties are defined
 */
function ensureLimeProps(target) {
    const promises = [];
    if (!target.platform) {
        promises.push(waitForProp(target, 'platform'));
    }
    if (!target.context) {
        promises.push(waitForProp(target, 'context'));
    }
    if (!promises.length) {
        return Promise.resolve();
    }
    return Promise.all(promises);
}
/**
 * Wait for a property to be defined on an object
 *
 * @param target - the web component
 * @param property - the name of the property to watch
 * @returns a promise that will resolve when the property is set on the object
 */
function waitForProp(target, property) {
    const element = getElement(target);
    return new Promise((resolve) => {
        Object.defineProperty(element, property, {
            configurable: true,
            set: (value) => {
                delete element[property];
                element[property] = value;
                resolve();
            },
        });
    });
}
function watchProp(target, property, observer) {
    const element = getElement(target);
    const { get, set } = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), property);
    Object.defineProperty(element, property, {
        configurable: true,
        get: get,
        set: function (value) {
            set.call(this, value);
            observer.next(value);
        },
    });
}
/**
 * Subscribe to changes from the state
 *
 * @param component - the component instance
 * @param property - property to update when subscription triggers
 * @returns
 */
function subscribe(component, property) {
    const subscription = createSubscription(component, property);
    const subscriptions = componentSubscriptions.get(component);
    subscriptions.push(subscription);
}
/**
 * Unsubscribe to changes from the state
 *
 * @param component - the instance of the component
 * @returns
 */
function unsubscribeAll(component) {
    const subscriptions = componentSubscriptions.get(component);
    subscriptions.forEach((unsubscribe) => unsubscribe());
    componentSubscriptions.set(component, []);
}
/**
 * Get a function that accepts a state, and updates the given property
 * on the given component with that state
 *
 * @param instance - the component to augment
 * @param property - name of the property on the component
 * @returns updates the state
 */
function mapState(instance, property) {
    return (state) => {
        instance[property] = state;
    };
}
/**
 * Create a state subscription
 *
 * @param component - the component instance
 * @param property - the property on the component
 * @returns unsubscribe function
 */
function createSubscription(component, property) {
    const myOptions = Object.assign({}, property.options);
    bindFunctions(myOptions, component);
    const name = property.service.name;
    const platform = component.platform;
    if (!platform.has(name)) {
        throw new Error(`Service ${name} does not exist`);
    }
    const service = platform.get(name);
    return service[property.service.method](mapState(component, property.name), myOptions);
}
/**
 * Bind connect functions to the current scope
 *
 * @param options - options for the selector
 * @param scope - the current scope to bind to
 * @returns
 */
function bindFunctions(options, scope) {
    if (options.filter) {
        options.filter = options.filter.map((func) => func.bind(scope));
    }
    if (options.map) {
        options.map = options.map.map((func) => func.bind(scope));
    }
}

const SERVICE_NAME$l = 'state.limeobjects';
PlatformServiceName.LimeObjectRepository = SERVICE_NAME$l;

/******************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */

function __decorate(decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
}

typeof SuppressedError === "function" ? SuppressedError : function (error, suppressed, message) {
    var e = new Error(message);
    return e.name = "SuppressedError", e.error = error, e.suppressed = suppressed, e;
};

/**
 * Events dispatched by the commandbus event middleware
 * @public
 * @group Command bus
 */
var CommandEventName;
(function (CommandEventName) {
    /**
     * Dispatched when the command has been received by the commandbus.
     * Calling `preventDefault()` on the event will stop the command from being handled
     *
     * @see {@link CommandEvent}
     */
    CommandEventName["Received"] = "command.received";
    /**
     * Dispatched when the command has been handled by the commandbus
     *
     * @see {@link CommandEvent}
     */
    CommandEventName["Handled"] = "command.handled";
    /**
     * Dispatched if an error occurs while handling the command
     *
     * @see {@link CommandEvent}
     */
    CommandEventName["Failed"] = "command.failed";
})(CommandEventName || (CommandEventName = {}));
/**
 * Register a class as a command
 *
 * @param options - a CommandOptions object containing the id of the command
 *
 * @returns callback which accepts a `CommandClass` and sets the command id
 * @public
 * @group Command bus
 */
function Command(options) {
    return (commandClass) => {
        setCommandId(commandClass, options.id);
        setHasInstance(commandClass, options.id);
    };
}
function setCommandId(commandClass, id) {
    // eslint-disable-next-line @typescript-eslint/dot-notation
    commandClass['commandId'] = id;
}
function setHasInstance(commandClass, id) {
    Object.defineProperty(commandClass, Symbol.hasInstance, {
        value: (instance) => {
            return getCommandIds(instance).includes(id);
        },
    });
}
/**
 * Get the registered id of the command
 *
 * @param value - either a command or a command identifier
 *
 * @returns id of the command
 * @public
 * @group Command bus
 */
function getCommandId(value) {
    if (typeof value === 'string') {
        return value;
    }
    /* eslint-disable @typescript-eslint/dot-notation */
    if (value && value.constructor && value.constructor['commandId']) {
        return value.constructor['commandId'];
    }
    if (value && value['commandId']) {
        return value['commandId'];
    }
    /* eslint-enable @typescript-eslint/dot-notation */
    return null;
}
/**
 * Get all registered ids of a command and its parent classes
 *
 * @param value - either a command or a command identifier
 *
 * @returns ids of the command
 * @beta
 * @group Command bus
 */
function getCommandIds(value) {
    let ids = [];
    let id;
    let commandClass = value;
    while ((id = getCommandId(commandClass))) {
        ids = [...ids, id];
        commandClass = Object.getPrototypeOf(commandClass);
    }
    return Array.from(new Set(ids));
}

const SERVICE_NAME$k = 'commandBus';
PlatformServiceName.CommandBus = SERVICE_NAME$k;

/**
 * Open a dialog for bulk creating limeobjects
 *
 *
 * ### Flow example
 * Let's have a look at the general flow by going through the concrete example of adding several persons to a marketing activity:
 * - Go to the table view of persons.
 * - Filter everyone who should be included in the marketing activity.
 * - Select 'Bulk create objects' form the action menu.
 * - Fill out the form and click 'create'.
 * - A toast message appears and gives you 5 seconds to undo the action before it creates the corresponding task.
 * - Another toast message will inform you after the task is completed.
 * - If the task ended successful you can go to the participant table view and check the result.
 *
 * ### Configuration
 * In order to activate the feature go to a table configuration in lime-admin to the limetype you want to bulk create from
 * and add the following configuration:
 *
 * ```json
 * "actions": [
 * {
 *      "id": "limeobject.bulk-create-dialog",
 *      "params": {
 *        "relation": "<name of relation>"
 *      }
 *    }
 * ],
 * ```
 *
 * @id `limeobject.bulk-create-dialog`
 * @public
 * @group Lime objects
 */
let BulkCreateDialogCommand = class BulkCreateDialogCommand {
    constructor() {
        /**
         * A list of relation names that are possible to create from the limetype
         *
         * @deprecated The dialog no longer supports multiple relations to be
         * picked from. Use the new {@link BulkCreateDialogCommand.relation}
         * property instead
         */
        this.relations = [];
    }
};
BulkCreateDialogCommand = __decorate([
    Command({
        id: 'limeobject.bulk-create-dialog',
    })
], BulkCreateDialogCommand);

/**
 * Open a dialog for creating a new limeobject or editing a specific limeobject
 *
 * The create dialog is implemented as a command so a plugin can easily replace the original dialog with a custom one.
 * Check out the "Hello, Event!" tutorial for a detailed description on how to implement your own create dialog.
 *
 * This dialog also useful to edit a limeobject that already exists
 *
 * @id `limeobject.create-dialog`
 * @public
 * @group Lime objects
 */
let CreateLimeobjectDialogCommand = class CreateLimeobjectDialogCommand {
    constructor() {
        /**
         * Specifies if routing to limeobject should be done after confirmation
         */
        this.route = false;
    }
};
CreateLimeobjectDialogCommand = __decorate([
    Command({
        id: 'limeobject.create-dialog',
    })
], CreateLimeobjectDialogCommand);

/**
 * Deletes the object from the database
 *
 * @id `limeobject.delete-object`
 * @public
 * @group Lime objects
 */
let DeleteObjectCommand = class DeleteObjectCommand {
};
DeleteObjectCommand = __decorate([
    Command({
        id: 'limeobject.delete-object',
    })
], DeleteObjectCommand);

/**
 * Open a dialog to view and edit object access information
 *
 * @id `limeobject.object-access`
 * @public
 * @group Lime objects
 */
let OpenObjectAccessDialogCommand = class OpenObjectAccessDialogCommand {
};
OpenObjectAccessDialogCommand = __decorate([
    Command({
        id: 'limeobject.object-access',
    })
], OpenObjectAccessDialogCommand);

/**
 * Saves the object to the database
 *
 * @id `limeobject.save-object`
 * @public
 * @group Lime objects
 */
let SaveLimeObjectCommand = class SaveLimeObjectCommand {
    constructor() {
        /**
         * Specifies if routing to limeobject should be done after confirmation
         */
        this.route = false;
    }
};
SaveLimeObjectCommand = __decorate([
    Command({
        id: 'limeobject.save-object',
    })
], SaveLimeObjectCommand);

/**
 * @public
 * @group Query
 */
var Operator;
(function (Operator) {
    Operator["AND"] = "AND";
    Operator["OR"] = "OR";
    Operator["NOT"] = "!";
    Operator["EQUALS"] = "=";
    Operator["NOT_EQUALS"] = "!=";
    Operator["GREATER"] = ">";
    Operator["LESS"] = "<";
    Operator["IN"] = "IN";
    Operator["BEGINS"] = "=?";
    Operator["LIKE"] = "?";
    Operator["LESS_OR_EQUAL"] = "<=";
    Operator["GREATER_OR_EQUAL"] = ">=";
    Operator["ENDS"] = "=$";
})(Operator || (Operator = {}));

const SERVICE_NAME$j = 'query';
PlatformServiceName.Query = SERVICE_NAME$j;

const SERVICE_NAME$i = 'http';
PlatformServiceName.Http = SERVICE_NAME$i;

const SERVICE_NAME$h = 'eventDispatcher';
PlatformServiceName.EventDispatcher = SERVICE_NAME$h;

const SERVICE_NAME$g = 'translate';
PlatformServiceName.Translate = SERVICE_NAME$g;

const SERVICE_NAME$f = 'dialog';
PlatformServiceName.Dialog = SERVICE_NAME$f;

const SERVICE_NAME$e = 'keybindingRegistry';
PlatformServiceName.KeybindingRegistry = SERVICE_NAME$e;

const SERVICE_NAME$d = 'navigator';
PlatformServiceName.Navigator = SERVICE_NAME$d;

/**
 * Navigates to a new location
 *
 * @id `navigator.navigate`
 * @beta
 * @group Navigation
 */
let NavigateCommand = class NavigateCommand {
};
NavigateCommand = __decorate([
    Command({
        id: 'navigator.navigate',
    })
], NavigateCommand);

const SERVICE_NAME$c = 'notifications';
PlatformServiceName.Notification = SERVICE_NAME$c;

const SERVICE_NAME$b = 'routeRegistry';
PlatformServiceName.RouteRegistry = SERVICE_NAME$b;

/**
 * @public
 * @group Tasks
 */
var TaskState;
(function (TaskState) {
    /**
     * Task state is unknown
     */
    TaskState["Pending"] = "PENDING";
    /**
     * Task was started by a worker
     */
    TaskState["Started"] = "STARTED";
    /**
     * Task is waiting for retry
     */
    TaskState["Retry"] = "RETRY";
    /**
     * Task succeeded
     */
    TaskState["Success"] = "SUCCESS";
    /**
     * Task failed
     */
    TaskState["Failure"] = "FAILURE";
})(TaskState || (TaskState = {}));
/**
 * Events dispatched by the task service
 * @public
 * @group Tasks
 */
var TaskEventType;
(function (TaskEventType) {
    /**
     * Dispatched when a task has been created.
     *
     * @see {@link TaskEvent}
     */
    TaskEventType["Created"] = "task.created";
    /**
     * Dispatched when the task has successfully been completed
     *
     * @see {@link TaskEvent}
     */
    TaskEventType["Success"] = "task.success";
    /**
     * Dispatched if an error occured while running the task
     *
     * @see {@link TaskEvent}
     */
    TaskEventType["Failed"] = "task.failed";
})(TaskEventType || (TaskEventType = {}));

const SERVICE_NAME$a = 'state.tasks';
PlatformServiceName.TaskRepository = SERVICE_NAME$a;

const SERVICE_NAME$9 = 'state.configs';
PlatformServiceName.ConfigRepository = SERVICE_NAME$9;

/**
 * Gets an object with all configs where key is used as key.
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Config
 */
function SelectConfig(options) {
    const config = {
        name: PlatformServiceName.ConfigRepository,
    };
    return createStateDecorator(options, config);
}

const SERVICE_NAME$8 = 'state.device';
PlatformServiceName.Device = SERVICE_NAME$8;

const SERVICE_NAME$7 = 'state.filters';
PlatformServiceName.FilterRepository = SERVICE_NAME$7;

const SERVICE_NAME$6 = 'state.user-data';
PlatformServiceName.UserDataRepository = SERVICE_NAME$6;

const SERVICE_NAME$5 = 'state.application';
PlatformServiceName.Application = SERVICE_NAME$5;

/**
 * Get the application session
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Application
 */
function SelectSession(options = {}) {
    const config = {
        name: PlatformServiceName.Application,
    };
    options.map = [getSession, ...(options.map || [])];
    return createStateDecorator(options, config);
}
function getSession(applicationData) {
    return applicationData.session;
}

const SERVICE_NAME$4 = 'userPreferences';
PlatformServiceName.UserPreferencesRepository = SERVICE_NAME$4;

const SERVICE_NAME$3 = 'datetimeformatter';
PlatformServiceName.DateTimeFormatter = SERVICE_NAME$3;

const SERVICE_NAME$2 = 'conditionRegistry';
PlatformServiceName.ConditionRegistry = SERVICE_NAME$2;

const SERVICE_NAME$1 = 'viewFactoryRegistry';
PlatformServiceName.ViewFactoryRegistry = SERVICE_NAME$1;

const SERVICE_NAME = 'webComponentRegistry';
PlatformServiceName.WebComponentRegistry = SERVICE_NAME;

export { Command as C, Operator as O, PlatformServiceName as P, SelectSession as S, SelectConfig as a, createStateDecorator as c };
