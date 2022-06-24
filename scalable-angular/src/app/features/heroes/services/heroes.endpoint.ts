import { HttpClient, HttpErrorResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Sort } from "@shared/types/sort";
import { StoreRequestStateUpdater } from "@shared/types/store-request-state-updater";
import { catchError, map, Observable, throwError } from "rxjs";
import { HEROES_CONFIG } from "../heroes.config";
import { Hero } from "../types/hero";
import * as endpointHelpers from '@shared/helpers/endpoint.helpers';
import * as sortHelpers from '@shared/helpers/sort.helpers';
import { ApiResponse } from "@app/shared/types/api-response";

@Injectable()
export class HeroesEndpoint {
    constructor(private http: HttpClient) {}

    listHeroes(sort: Sort, requestStateUpdater: StoreRequestStateUpdater) : Observable<Hero[]> {
        const request = HEROES_CONFIG.requests.listHeroes;
        const options = {
            params: {
                ...sortHelpers.convertSortToRequestParams(sort)
            }
        };
        requestStateUpdater(request.name, {inProgress: true});
        return this.http.get<ApiResponse<Hero[]>>(request.url, options)
        .pipe(
            map(response => {
                requestStateUpdater(request.name, {inProgress: false});
                return response.data;
            }),
            catchError((error: HttpErrorResponse)=> {
                requestStateUpdater(request.name, {
                    inProgress: false,
                    error: true
                });

                return throwError(()=> error);
            })
        )
    }
}