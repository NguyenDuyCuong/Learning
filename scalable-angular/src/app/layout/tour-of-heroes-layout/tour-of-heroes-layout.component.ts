import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-tour-of-heroes-layout',
  templateUrl: './tour-of-heroes-layout.component.html',
  styleUrls: ['./tour-of-heroes-layout.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TourOfHeroesLayoutComponent {
  title = 'Tour of Heroes';
}
