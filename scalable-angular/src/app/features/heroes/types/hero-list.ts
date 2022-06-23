import { Sort } from "@app/shared/types/sort";
import { Hero } from "./hero";

export interface HeroList {
    heroes: Hero[];
    sort: Sort;
}