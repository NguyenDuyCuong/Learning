import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import { DefaultLayoutComponent } from '@app/layout/default-layout/default-layout.component';
import { CoffeeListComponent } from './views/coffee-list/coffee-list.component';



export const routingPaths = {
    coffeeList: '',
};

const routes: Routes = [
    {
        path: '',
        component: DefaultLayoutComponent,
        children: [
            {
                path: '',
                component: CoffeeListComponent
            }
        ]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class CoffeeListRoutingModule {}
