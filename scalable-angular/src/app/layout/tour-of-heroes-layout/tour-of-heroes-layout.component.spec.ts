import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TourOfHeroesLayoutComponent } from './tour-of-heroes-layout.component';

describe('TourOfHeroesLayoutComponent', () => {
  let component: TourOfHeroesLayoutComponent;
  let fixture: ComponentFixture<TourOfHeroesLayoutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TourOfHeroesLayoutComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TourOfHeroesLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
