import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import '../rxjs-extensions';

import { Question } from '../models/question';

@Injectable({
  providedIn: 'root'
})
export class QuestionService {
  private serviceUrl = 'http://localhost:3000/questions';  // URL to web api

  constructor(private http: HttpClient) {
  }

  getQuestions(): Observable<Question[]> {
    const url = this.serviceUrl;
    return this.http.get<Question[]>(url);
    // .map(res => res.json());
  }
}
