import {APP_CONFIG} from '@app/app.config';

export const USER_CONFIG = {
    requests: {
        getUser: {
            name: 'getUser',
            url: `${APP_CONFIG.apiBaseUrl}/user.json`,
        },
    },
};
