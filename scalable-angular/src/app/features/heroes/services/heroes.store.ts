import { Injectable, OnDestroy } from "@angular/core";
import { StoreRequestStateUpdater } from "@app/shared/types/store-request-state-updater";
import { Subject, switchMap, takeUntil, tap } from "rxjs";
import { Store } from "rxjs-observable-store";
import { HeroesEndpoint } from "./heroes.endpoint";
import { HeroesStoreState } from "./heroes.store.state";
import * as endpointHelpers from '@shared/helpers/endpoint.helpers';
import { Hero, IHero } from "../types/hero";
import { ModalComponent } from "@app/shared/components/modal/modal.component";
import { NullHero } from "../types/null-hero";

@Injectable()
export class HeroesStore extends Store<HeroesStoreState> implements OnDestroy {
    private ngUnsubscribe$: Subject<undefined> = new Subject();
    private reloadHeroes$: Subject<undefined> = new Subject();
    private detailsModal: ModalComponent;
    private storeRequestStateUpdater: StoreRequestStateUpdater;

    constructor(private endpoint: HeroesEndpoint){
        super(new HeroesStoreState());
    }

    init(): void {
        this.initReloadHeroes$();

        this.storeRequestStateUpdater = endpointHelpers.getStoreRequestStateUpdater(this);
    }
    
    ngOnDestroy(): void {
        this.ngUnsubscribe$.next(undefined);
        this.ngUnsubscribe$.complete();
    }
    
    reloadHeroes(): void {
        this.reloadHeroes$.next(undefined);
    }

    setDetailsModal(detailsModal: ModalComponent): void {
        this.detailsModal = detailsModal;
    }

    openDetailsModal(hero: Hero): void {
        this.setDetailsModalState(hero);
        this.detailsModal.open();
    }

    closeDetailsModal(): void {
        this.setDetailsModalState(new NullHero());
        this.detailsModal.close();
    }

    setDetailsModalState(hero: IHero = new NullHero()): void {
        this.setState({
            ...this.state,
            detailsModal: {
                hero
            },
        });
    }

    private initReloadHeroes$(): void {
        this.reloadHeroes$
        .pipe(
            switchMap(() => {
                return this.endpoint.listHeroes(this.state.heroList.sort,
                    this.storeRequestStateUpdater)
            }),
            tap(heroes => {
                this.updateHeroesState(heroes);
            }),
            takeUntil(this.ngUnsubscribe$)
        )
        .subscribe();
    }

    private updateHeroesState(heroes: Hero[]) : void {
        this.setState({
            ...this.state,
            heroList: {
                ...this.state.heroList,
                heroes
            }
        })
    }
}
