import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import {takeUntil} from 'rxjs/operators';
import { HeroesEndpoint } from '../../services/heroes.endpoint';
import { HeroesStore } from '../../services/heroes.store';
import * as sortHelpers from '@shared/helpers/sort.helpers';
import { HEROES_CONFIG } from '../../heroes.config';

@Component({
  selector: 'app-hero-list',
  templateUrl: './hero-list.component.html',
  styleUrls: ['./hero-list.component.scss'],
  providers: [HeroesStore, HeroesEndpoint]
})
export class HeroListComponent implements OnInit {
  private ngUnsubscribe$: Subject<undefined> = new Subject();

  constructor(public store: HeroesStore, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.store.init()
    this.subscribeToQueryParamsUpdates();
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe$.next(undefined);
    this.ngUnsubscribe$.complete();
  }

  private subscribeToQueryParamsUpdates(): void {
    this.route.queryParams
        .pipe(takeUntil(this.ngUnsubscribe$))
        .subscribe(params => {
            this.store.reloadHeroes();
        });
  }
}
