import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IShell } from './shell';
import { IRenderMime } from '@jupyterlab/rendermime';
/**
 * App is the main application class. It is instantiated once and shared.
 */
export declare class App extends JupyterFrontEnd<IShell> {
    /**
     * Construct a new App object.
     *
     * @param options The instantiation options for an application.
     */
    constructor(options: App.IOptions);
    /**
     * The name of the application.
     */
    readonly name = "JupyterLab Custom App";
    /**
     * A namespace/prefix plugins may use to denote their provenance.
     */
    readonly namespace = "JupyterLab Custom App";
    /**
     * The version of the application.
     */
    readonly version = "unknown";
    /**
     * The JupyterLab application paths dictionary.
     */
    get paths(): JupyterFrontEnd.IPaths;
    /**
     * Register plugins from a plugin module.
     *
     * @param mod - The plugin module to register.
     */
    registerPluginModule(mod: App.IPluginModule): void;
    /**
     * Register the plugins from multiple plugin modules.
     *
     * @param mods - The plugin modules to register.
     */
    registerPluginModules(mods: App.IPluginModule[]): void;
}
/**
 * A namespace for App statics.
 */
export declare namespace App {
    /**
     * The instantiation options for an App application.
     */
    interface IOptions extends JupyterFrontEnd.IOptions<IShell>, Partial<IInfo> {
        paths?: Partial<JupyterFrontEnd.IPaths>;
    }
    /**
     * The information about a application.
     */
    interface IInfo {
        /**
         * The mime renderer extensions.
         */
        readonly mimeExtensions: IRenderMime.IExtensionModule[];
    }
    /**
     * The interface for a module that exports a plugin or plugins as
     * the default value.
     */
    interface IPluginModule {
        /**
         * The default export.
         */
        default: JupyterFrontEndPlugin<any> | JupyterFrontEndPlugin<any>[];
    }
}
