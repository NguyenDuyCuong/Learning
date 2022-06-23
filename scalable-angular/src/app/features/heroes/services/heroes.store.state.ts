import { HEROES_CONFIG } from "../heroes.config";
import { DetailsModal } from "../types/detail-modal";
import { HeroList } from "../types/hero-list";
import { Requests } from "../types/request";

export class HeroesStoreState {
    heroList: HeroList = {
        heroes: [],
        sort: {
            field: HEROES_CONFIG.defaultSortField,
            order: HEROES_CONFIG.defaultSortOrder
        }
    };
    detailsModal: DetailsModal = {};
    requests: Requests = {
        listHeroes: {}
    };
}
