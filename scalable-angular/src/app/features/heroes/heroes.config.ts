import { APP_CONFIG } from "@app/app.config"
import { SortOrder } from "@app/app.constants"

export const HEROES_CONFIG = {
    requests: {
        listHeroes: {
            name: 'listHeroes',
            url: `${APP_CONFIG.apiBaseUrl}/heroes.json`
        }
    },
    defaultSortField: 'name',
    defaultSortOrder: SortOrder.Asc
}
