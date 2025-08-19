import { Widget } from '@lumino/widgets';
export class UserMenu extends Widget {
    constructor(options) {
        super();
        this._user = options.user;
        this._user.ready.then(() => this._createUserIcon());
    }
    _createUserIcon() {
        const userData = this._user.identity;
        if (!userData) {
            return;
        }
        const nameEl = document.createElement('span');
        nameEl.innerText = userData.display_name;
        this.node.appendChild(nameEl);
        const iconEl = document.createElement('div');
        iconEl.classList.add('lm-MenuBar-itemIcon');
        iconEl.title = userData.display_name;
        if (userData === null || userData === void 0 ? void 0 : userData.avatar_url) {
            iconEl.classList.add('jp-MenuBar-imageIcon');
            const img = document.createElement('img');
            img.src = userData.avatar_url;
            iconEl.appendChild(img);
        }
        else {
            iconEl.classList.add('jc-MenuBar-anonymousIcon');
            iconEl.style.backgroundColor = userData.color;
            const sp = document.createElement('span');
            sp.innerText = userData.initials;
            iconEl.appendChild(sp);
        }
        this.node.appendChild(iconEl);
    }
}
