import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import { TourOfHeroesLayoutComponent } from '@app/layout/tour-of-heroes-layout/tour-of-heroes-layout.component';
import { HeroListComponent } from './views/hero-list/hero-list.component';

const routes: Routes = [
    {
        path: '',
        component: TourOfHeroesLayoutComponent,
        children: [
            {
                path: 'heroes',
                component: HeroListComponent
            }
        ]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class HeroesRoutingModule {}
