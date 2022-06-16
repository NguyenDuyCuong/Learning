import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CoffeeListComponent } from './views/coffee-list/coffee-list.component';
import { SharedModule } from '@app/shared/shared.module';
import { CoffeeListRoutingModule } from './coffee-list-routing.module';
import { CandidateDetailsComponent } from './components/candidate-details/candidate-details.component';
import { CoffeeCandidateComponent } from './components/coffee-candidate/coffee-candidate.component';



@NgModule({
  declarations: [
    CoffeeListComponent,
    CandidateDetailsComponent,
    CoffeeCandidateComponent
  ],
  imports: [CoffeeListRoutingModule, SharedModule,
    CommonModule
  ]
})
export class CoffeeListModule { }
