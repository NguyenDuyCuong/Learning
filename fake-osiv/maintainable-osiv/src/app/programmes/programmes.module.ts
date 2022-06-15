import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ProgrammesRoutingModule } from './programmes-routing.module';
import { ProgrammesComponent } from './programmes.component';


@NgModule({
  declarations: [
    ProgrammesComponent
  ],
  imports: [
    CommonModule,
    ProgrammesRoutingModule
  ]
})
export class ProgrammesModule { }
