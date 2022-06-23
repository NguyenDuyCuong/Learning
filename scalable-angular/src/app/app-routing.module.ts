import { NgModule, Optional, SkipSelf } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { PageNotFoundComponent } from './views/page-not-found/page-not-found.component';

const appRoutes: Routes = [
    {
        path: '',
        redirectTo: 'coffee',
        pathMatch: 'full',
    },
    {
        path: 'coffee',
        loadChildren: () => import('./features/coffee-list/coffee-list.module').then(m => m.CoffeeListModule)
    },
    {
        path: 'heroes',
        loadChildren: () => import('./features/heroes/heroes.module').then(m => m.HeroesModule)
    },
    { path: '**', component: PageNotFoundComponent },
];

@NgModule({
    imports: [RouterModule.forRoot(appRoutes)],
    exports: [RouterModule],
})
export class AppRoutingModule {
    constructor(
        @Optional()
        @SkipSelf()
        parentModule: AppRoutingModule
    ) {
        if (parentModule) {
            throw new Error(
                'AppRoutingModule is already loaded. Import it in the AppModule only.'
            );
        }
    }
}
