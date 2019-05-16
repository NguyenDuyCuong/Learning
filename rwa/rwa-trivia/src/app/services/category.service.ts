import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import '../rxjs-extensions';

import { Category } from '../models/category';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private serviceUrl = 'http://localhost:3000/categories';  // URL to web api

  constructor(private http: HttpClient) { }

  getCategories(): Observable<Category[]> {
    const url = this.serviceUrl;
    return this.http.get<Category[]>(url);
  }
}
