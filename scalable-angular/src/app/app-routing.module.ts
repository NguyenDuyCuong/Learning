import {NgModule, Optional, SkipSelf} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {routingPaths as coffeeListRoutingPaths} from './features/coffee-list/coffee-list-routing.module';
import { PageNotFoundComponent } from './views/page-not-found/page-not-found.component';

const appRoutes: Routes = [
    {
        path: '',
        redirectTo: coffeeListRoutingPaths.coffeeList,
        pathMatch: 'full',
    },
    {path: '**', component: PageNotFoundComponent},
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
