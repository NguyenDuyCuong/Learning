import {NgModule, Optional, SkipSelf} from '@angular/core';
import {RouterModule} from '@angular/router';

import {HeaderComponent} from './header/header.component';
import { TourOfHeroesLayoutComponent } from './tour-of-heroes-layout/tour-of-heroes-layout.component';
import { DefaultLayoutComponent } from './default-layout/default-layout.component';

const EXPORTED_DECLARATIONS = [HeaderComponent, TourOfHeroesLayoutComponent, DefaultLayoutComponent];

@NgModule({
    declarations: [...EXPORTED_DECLARATIONS],
    exports: [...EXPORTED_DECLARATIONS],
    imports: [RouterModule],
    providers: [],
})
export class LayoutModule {
    constructor(
        @Optional()
        @SkipSelf()
        parentModule: LayoutModule
    ) {
        if (parentModule) {
            throw new Error(
                'LayoutModule is already loaded. Import it in the AppModule only.'
            );
        }
    }
}
