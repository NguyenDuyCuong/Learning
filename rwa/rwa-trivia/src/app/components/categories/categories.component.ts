import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable } from 'rxjs';

import { Category } from '../../models';
import { CategoryService } from '../../services';

@Component({
  selector: 'app-category-list',
  templateUrl: './categories.component.html',
  styleUrls: ['./categories.component.scss']
})
export class CategoriesComponent implements OnInit, OnDestroy {
  categories: Category[];
  sub: any;

  constructor(private categoryService: CategoryService) {
  }

  ngOnInit() {
    this.sub = this.categoryService.getCategories()
      .subscribe(categories => this.categories = categories);
  }

  ngOnDestroy() {
    if (this.sub) {
      this.sub.unsubscribe();
    }
  }

}
