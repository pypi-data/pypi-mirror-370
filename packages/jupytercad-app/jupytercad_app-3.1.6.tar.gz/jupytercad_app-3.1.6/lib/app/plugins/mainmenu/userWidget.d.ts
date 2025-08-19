import { User } from '@jupyterlab/services';
import { Widget } from '@lumino/widgets';
export declare class UserMenu extends Widget {
    constructor(options: {
        user: User.IManager;
    });
    private _createUserIcon;
    private _user;
}
