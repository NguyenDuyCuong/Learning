import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import '../rxjs-extensions';

@Injectable({
  providedIn: 'root'
})
export class TagService {

  private serviceUrl = 'http://localhost:3000/tagList';  // URL to web api

  constructor(private http: HttpClient) { }

  getTags(): Observable<string[]> {
    const url = this.serviceUrl;
    return this.http.get<string[]>(url);
    //.map(res => res.json());
  }
}
