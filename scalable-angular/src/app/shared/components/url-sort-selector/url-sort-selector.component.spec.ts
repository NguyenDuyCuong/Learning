import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlSortSelectorComponent } from './url-sort-selector.component';

describe('UrlSortSelectorComponent', () => {
  let component: UrlSortSelectorComponent;
  let fixture: ComponentFixture<UrlSortSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UrlSortSelectorComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UrlSortSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
