import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeroesRoutingModule } from './heroes-routing.module';
import { SharedModule } from '@app/shared/shared.module';
import { HeroDetailComponent } from './components/hero-detail/hero-detail.component';
import { FormsModule } from '@angular/forms';
import { HeroListComponent } from './views/hero-list/hero-list.component';



@NgModule({
  declarations: [
    HeroDetailComponent,
    HeroListComponent
  ],
  imports: [
    HeroesRoutingModule, SharedModule,
    CommonModule,

    FormsModule
  ]
})
export class HeroesModule { }
