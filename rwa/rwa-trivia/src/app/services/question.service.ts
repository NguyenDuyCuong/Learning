import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import '../rxjs-extensions';

import { Question, Category } from '../models';
import { CategoryService } from './category.service';

@Injectable({
  providedIn: 'root'
})
export class QuestionService {
  private serviceUrl = 'http://localhost:3000/questions';  // URL to web api

  constructor(private http: HttpClient, private categoryService: CategoryService) {
  }

  getQuestions(): Observable<Question[]> {
    const url = this.serviceUrl;

    return this.http.get<Question[]>(url);
  }
}
