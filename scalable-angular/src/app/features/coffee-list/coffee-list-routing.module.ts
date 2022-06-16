import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import { CoffeeListComponent } from './views/coffee-list/coffee-list.component';



export const routingPaths = {
    coffeeList: 'list',
};

const routes: Routes = [
    {
        path: routingPaths.coffeeList,
        component: CoffeeListComponent,
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class CoffeeListRoutingModule {}
