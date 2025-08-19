import { createRendermimePlugins, JupyterFrontEnd } from '@jupyterlab/application';
import { PageConfig } from '@jupyterlab/coreutils';
import { Shell } from './shell';
/**
 * App is the main application class. It is instantiated once and shared.
 */
export class App extends JupyterFrontEnd {
    /**
     * Construct a new App object.
     *
     * @param options The instantiation options for an application.
     */
    constructor(options) {
        var _a;
        super(Object.assign(Object.assign({}, options), { shell: (_a = options.shell) !== null && _a !== void 0 ? _a : new Shell() }));
        /**
         * The name of the application.
         */
        this.name = 'JupyterLab Custom App';
        /**
         * A namespace/prefix plugins may use to denote their provenance.
         */
        this.namespace = this.name;
        /**
         * The version of the application.
         */
        // TODO proper version
        this.version = 'unknown';
        if (options.mimeExtensions) {
            for (const plugin of createRendermimePlugins(options.mimeExtensions)) {
                this.registerPlugin(plugin);
            }
        }
    }
    /**
     * The JupyterLab application paths dictionary.
     */
    get paths() {
        return {
            urls: {
                base: PageConfig.getOption('baseUrl'),
                notFound: PageConfig.getOption('notFoundUrl'),
                app: PageConfig.getOption('appUrl'),
                static: PageConfig.getOption('staticUrl'),
                settings: PageConfig.getOption('settingsUrl'),
                themes: PageConfig.getOption('themesUrl'),
                doc: PageConfig.getOption('docUrl'),
                translations: PageConfig.getOption('translationsApiUrl'),
                hubHost: PageConfig.getOption('hubHost') || undefined,
                hubPrefix: PageConfig.getOption('hubPrefix') || undefined,
                hubUser: PageConfig.getOption('hubUser') || undefined,
                hubServerName: PageConfig.getOption('hubServerName') || undefined
            },
            directories: {
                appSettings: PageConfig.getOption('appSettingsDir'),
                schemas: PageConfig.getOption('schemasDir'),
                static: PageConfig.getOption('staticDir'),
                templates: PageConfig.getOption('templatesDir'),
                themes: PageConfig.getOption('themesDir'),
                userSettings: PageConfig.getOption('userSettingsDir'),
                serverRoot: PageConfig.getOption('serverRoot'),
                workspaces: PageConfig.getOption('workspacesDir')
            }
        };
    }
    /**
     * Register plugins from a plugin module.
     *
     * @param mod - The plugin module to register.
     */
    registerPluginModule(mod) {
        let data = mod.default;
        // Handle commonjs exports.
        if (!Object.prototype.hasOwnProperty.call(mod, '__esModule')) {
            data = mod;
        }
        if (!Array.isArray(data)) {
            data = [data];
        }
        data.forEach(item => {
            try {
                this.registerPlugin(item);
            }
            catch (error) {
                console.error(error);
            }
        });
    }
    /**
     * Register the plugins from multiple plugin modules.
     *
     * @param mods - The plugin modules to register.
     */
    registerPluginModules(mods) {
        mods.forEach(mod => {
            this.registerPluginModule(mod);
        });
    }
}
