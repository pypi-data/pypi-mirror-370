import { ILabShell } from '@jupyterlab/application';
const launcherPlugin = {
    id: '@jupyterlab/-custom-launcher-extension',
    description: 'Customize the default launcher.',
    requires: [ILabShell],
    autoStart: true,
    activate: (app, labShell) => {
        labShell.layoutModified.connect(() => {
            var _a, _b;
            const launcherSection = document.getElementsByClassName('jp-Launcher-section');
            for (let index = 0; index < launcherSection.length; index++) {
                const element = launcherSection.item(index);
                const label = (_a = element === null || element === void 0 ? void 0 : element.getElementsByClassName('jp-LauncherCard-label')) === null || _a === void 0 ? void 0 : _a.item(0);
                if (!label) {
                    continue;
                }
                if (label.innerHTML.includes('CAD File')) {
                    const els = (_b = element
                        .getElementsByClassName('jp-Launcher-sectionTitle')) === null || _b === void 0 ? void 0 : _b.item(0);
                    if (els) {
                        els.innerHTML = 'Create New Project';
                    }
                }
                else {
                    element.style.display = 'none';
                }
            }
        });
    }
};
export default launcherPlugin;
