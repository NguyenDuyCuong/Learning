import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoffeeCandidateComponent } from './coffee-candidate.component';

describe('CoffeeCandidateComponent', () => {
  let component: CoffeeCandidateComponent;
  let fixture: ComponentFixture<CoffeeCandidateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CoffeeCandidateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CoffeeCandidateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
