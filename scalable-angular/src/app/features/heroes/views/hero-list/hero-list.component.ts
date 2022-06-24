import { AfterViewInit, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ModalComponent } from '@app/shared/components/modal/modal.component';
import { Subject } from 'rxjs';
import {takeUntil} from 'rxjs/operators';
import { HeroesEndpoint } from '../../services/heroes.endpoint';
import { HeroesStore } from '../../services/heroes.store';
import { Hero } from '../../types/hero';

@Component({
  selector: 'app-hero-list',
  templateUrl: './hero-list.component.html',
  styleUrls: ['./hero-list.component.scss'],
  providers: [HeroesStore, HeroesEndpoint]
})
export class HeroListComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('detailsModal')
  detailsModal: ModalComponent;

  private ngUnsubscribe$: Subject<undefined> = new Subject();

  constructor(public store: HeroesStore, private route: ActivatedRoute) { }

  ngAfterViewInit(): void {
    this.store.setDetailsModal(this.detailsModal);
  }

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
