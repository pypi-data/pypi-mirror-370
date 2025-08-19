import { JupyterFrontEnd } from '@jupyterlab/application';
/**
 * The default paths.
 */
const paths = {
    id: 'jupytercad:paths',
    activate: (app) => {
        return app.paths;
    },
    autoStart: true,
    provides: JupyterFrontEnd.IPaths
};
export default paths;
