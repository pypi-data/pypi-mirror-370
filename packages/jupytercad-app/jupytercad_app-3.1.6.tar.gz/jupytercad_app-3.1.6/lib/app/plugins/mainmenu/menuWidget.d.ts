import { CommandRegistry } from '@lumino/commands';
import { MenuBar } from '@lumino/widgets';
import { IThemeManager } from '@jupyterlab/apputils';
export declare class MainMenu extends MenuBar {
    constructor(options: {
        commands: CommandRegistry;
        themeManager: IThemeManager;
    });
    private _createHelpMenu;
    private _createFileMenu;
    private _createEditMenu;
    private _createViewMenu;
    private _commands;
    private _themeManager;
}
