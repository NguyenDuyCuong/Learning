import {NgModule, Optional, SkipSelf} from '@angular/core';

import {PageNotFoundComponent} from './page-not-found/page-not-found.component';

@NgModule({
    declarations: [PageNotFoundComponent],
    imports: [],
})
export class ViewsModule {
    constructor(
        @Optional()
        @SkipSelf()
        parentModule: ViewsModule
    ) {
        if (parentModule) {
            throw new Error(
                'ViewsModule is already loaded. Import it in the AppModule only.'
            );
        }
    }
}
